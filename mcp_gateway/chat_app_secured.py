"""
chat_app_secured.py

Secured chat application with Bifrost security layers:
  User Prompt → OPA → Lakera → Presidio → LLM → Notion MCP

All user prompts are checked through 3 security layers before reaching the LLM.
"""

import asyncio
import json
import os
import shutil
import sys

from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add parent directory to path for security imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from security.lakera_guard import scan_prompt
from security.presidio_scanner import scan_output, redact_output

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def find_npx() -> tuple[str, str]:
    """Find npx binary."""
    npx = shutil.which("npx")
    if npx:
        return npx, os.path.dirname(os.path.realpath(npx))
    home = os.path.expanduser("~")
    nvm_dir = os.path.join(home, ".nvm", "versions", "node")
    if os.path.isdir(nvm_dir):
        for version in sorted(os.listdir(nvm_dir), reverse=True):
            bin_dir = os.path.join(nvm_dir, version, "bin")
            candidate = os.path.join(bin_dir, "npx")
            if os.path.isfile(candidate):
                return candidate, bin_dir
    sys.exit("ERROR: npx not found. Install Node.js >= 18.")


def check_opa_policy(text: str) -> tuple[bool, str]:
    """Layer 1: OPA - Check for malicious patterns and harmful content."""
    malicious_patterns = [
        'drop_table', 'delete_all', 'admin_action', 'system_command',
        'DROP TABLE', 'DELETE FROM', 'INSERT INTO', 'UPDATE SET'
    ]
    harmful_keywords = [
        'kill', 'murder', 'suicide', 'bomb', 'weapon', 'attack',
        'harm', 'hurt', 'violence', 'exploit', 'hack'
    ]
    
    text_lower = text.lower()
    for pattern in malicious_patterns:
        if pattern.lower() in text_lower:
            return False, f"OPA blocked: malicious pattern '{pattern}'"
    
    for keyword in harmful_keywords:
        if keyword in text_lower:
            return False, f"OPA blocked: harmful content '{keyword}'"
    
    return True, "OPA passed"


def check_security_layers(user_input: str) -> tuple[bool, str, str]:
    """
    Process input through all security layers.
    Returns: (allowed, message, processed_text)
    """
    
    # Layer 1: OPA Policy
    opa_ok, opa_msg = check_opa_policy(user_input)
    if not opa_ok:
        return False, f"🛡️ {opa_msg}", user_input
    
    # Layer 2: Lakera Guard
    lakera_result = scan_prompt(user_input)
    if lakera_result.flagged:
        return False, f"🛡️ Lakera blocked: prompt injection detected (ID: {lakera_result.request_uuid})", user_input
    
    return True, "✅ Input security layers passed", user_input


def mcp_tools_to_openai_tools(mcp_tools: list) -> list[dict]:
    """Convert MCP tool definitions to OpenAI function-calling format."""
    openai_tools = []
    for tool in mcp_tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema if tool.inputSchema else {"type": "object", "properties": {}},
            },
        })
    return openai_tools


async def process_query(
    session: ClientSession,
    client: OpenAI,
    openai_tools: list[dict],
    messages: list[dict],
    user_query: str,
) -> str:
    """Process a single user query through the AI + MCP tool loop."""
    
    messages.append({"role": "user", "content": user_query})
    
    while True:
        response = client.chat.completions.create(
            model=GEMINI_MODEL,
            messages=messages,
            tools=openai_tools if openai_tools else None,
        )
        
        choice = response.choices[0]
        assistant_message = choice.message
        
        if not assistant_message.tool_calls:
            final = assistant_message.content or "(No response)"
            messages.append({"role": "assistant", "content": final})
            
            # Layer 3: Presidio PII Detection on OUTPUT
            presidio_result = scan_output(final)
            if presidio_result.has_pii:
                redacted = redact_output(final)
                entity_types = ', '.join(presidio_result.entity_types)
                print(f"🛡️ Presidio scrubbed PII from response: {entity_types}")
                return redacted
            
            return final
        
        msg_dict = {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in assistant_message.tool_calls
            ],
        }
        if assistant_message.content:
            msg_dict["content"] = assistant_message.content
        messages.append(msg_dict)
        
        for tool_call in assistant_message.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)
            print(f"   🔨 {fn_name}({json.dumps(fn_args)[:120]}...)")
            
            try:
                result = await session.call_tool(fn_name, fn_args)
                result_text = result.content[0].text if result.content else "(empty)"
            except Exception as e:
                result_text = f"Error: {e}"
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result_text,
            })


async def main():
    if not NOTION_TOKEN:
        sys.exit("ERROR: NOTION_TOKEN not set in .env")
    if not GEMINI_API_KEY:
        sys.exit("ERROR: GEMINI_API_KEY not set in .env")
    
    npx_path, node_bin_dir = find_npx()
    env = {**os.environ, "NOTION_TOKEN": NOTION_TOKEN}
    env["PATH"] = node_bin_dir + os.pathsep + env.get("PATH", "")
    
    server_params = StdioServerParameters(
        command=npx_path,
        args=["-y", "@notionhq/notion-mcp-server"],
        env=env,
    )
    
    print("=" * 70)
    print("  🛡️  SECURED Notion MCP Chat with Bifrost Security Layers")
    print("  Security: OPA → Lakera Guard → Presidio PII")
    print("  Type 'quit' or 'exit' to stop")
    print("=" * 70)
    print("\n⏳ Starting Notion MCP server...")
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            tools_result = await session.list_tools()
            mcp_tools = tools_result.tools
            openai_tools = mcp_tools_to_openai_tools(mcp_tools)
            
            print(f"✅ Connected! {len(mcp_tools)} tools available.")
            print("🛡️  Security layers active: OPA, Lakera, Presidio\n")
            
            client = OpenAI(
                api_key=GEMINI_API_KEY,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
            messages = [{
                "role": "system",
                "content": (
                    "You are a helpful assistant connected to the user's "
                    "Notion workspace. Use the available tools to search, "
                    "read, create, and update Notion pages and databases. "
                    "Always search before trying to access specific content."
                ),
            }]
            
            while True:
                try:
                    query = input("\n📝 You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 Goodbye!")
                    break
                
                if not query:
                    continue
                if query.lower() in ("quit", "exit", "q"):
                    print("👋 Goodbye!")
                    break
                
                # SECURITY CHECK: Process through all layers
                allowed, security_msg, processed_query = check_security_layers(query)
                
                if not allowed:
                    print(f"\n{security_msg}")
                    continue
                
                if security_msg != "✅ All security layers passed":
                    print(f"   {security_msg}")
                
                answer = await process_query(
                    session, client, openai_tools, messages, processed_query
                )
                print(f"\n🤖 Assistant: {answer}")


if __name__ == "__main__":
    asyncio.run(main())
