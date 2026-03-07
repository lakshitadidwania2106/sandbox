"""
MITM Proxy for Bifrost (Based on SigmaShield)
==============================================

This intercepts ALL network traffic and checks for proprietary code leaks.
Based on the working SigmaShield implementation.

Usage:
    # Start the proxy
    python security/mitm_proxy.py
    
    # Or use mitmdump directly
    mitmdump -s security/mitm_proxy.py
"""

import json
import urllib.parse
import asyncio
from pathlib import Path
from mitmproxy import http
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Import our detection logic (SigmaShield-style)
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from security.fuzzy_detector import check_if_company_code as detect_proprietary

# Configuration
PROPRIETARY_CODE_PATH = "./proprietary_code"
MIN_SIMILARITY_SCORE = 60  # 0-100 scale (60 = 60% similar)

# Verify proprietary code directory exists
if Path(PROPRIETARY_CODE_PATH).exists():
    print(f"✅ Proprietary code directory found: {PROPRIETARY_CODE_PATH}")
else:
    print(f"⚠️  Warning: {PROPRIETARY_CODE_PATH} not found. Create it and add your proprietary code.")

executor = ThreadPoolExecutor(max_workers=2)


def check_if_company_code(text: str) -> bool:
    """
    Check if text contains proprietary code.
    Uses SigmaShield-style fuzzy similarity matching.
    """
    if not text or len(text.strip()) < 20:
        return False
    
    # Use SigmaShield-style detection
    is_proprietary = detect_proprietary(
        text, 
        folder_path=PROPRIETARY_CODE_PATH,
        min_score=MIN_SIMILARITY_SCORE
    )
    
    if is_proprietary:
        print(f"🚨 PROPRIETARY CODE DETECTED!")
        print(f"   Text length: {len(text)} chars")
    
    return is_proprietary


def handle_chatgpt(flow: http.HTTPFlow) -> bool:
    """
    Handle ChatGPT requests.
    Extracts messages and checks for proprietary code.
    """
    try:
        request_text = flow.request.content.decode('utf-8')
        request_data = json.loads(request_text)
        
        if 'messages' in request_data:
            for message in request_data['messages']:
                content = message.get('content', {})
                
                # Handle different content formats
                if isinstance(content, dict):
                    parts = content.get('parts', [])
                    for part in parts:
                        if check_if_company_code(str(part)):
                            return True
                elif isinstance(content, str):
                    if check_if_company_code(content):
                        return True
        
        return False
    
    except Exception as e:
        print(f"Error handling ChatGPT request: {e}")
        return False


def handle_twitter(flow: http.HTTPFlow) -> bool:
    """
    Handle Twitter/X requests.
    Extracts tweet text and checks for proprietary code.
    """
    try:
        request_text = flow.request.content.decode('utf-8')
        request_data = json.loads(request_text)
        
        if 'variables' in request_data:
            variables = request_data['variables']
            tweet_text = variables.get('tweet_text')
            
            if tweet_text and check_if_company_code(tweet_text):
                return True
        
        return False
    
    except Exception as e:
        print(f"Error handling Twitter request: {e}")
        return False


def handle_stackoverflow(flow: http.HTTPFlow) -> bool:
    """
    Handle StackOverflow requests.
    Extracts post text and checks for proprietary code.
    """
    try:
        request_text = flow.request.content.decode('utf-8')
        form_data = urllib.parse.parse_qs(request_text)
        
        post_text_list = form_data.get('post-text', [])
        if post_text_list:
            post_text = post_text_list[0]
            if check_if_company_code(post_text):
                return True
        
        return False
    
    except Exception as e:
        print(f"Error handling StackOverflow request: {e}")
        return False


def handle_generic_post(flow: http.HTTPFlow) -> bool:
    """
    Generic handler for any POST request.
    Checks common fields for proprietary code.
    """
    try:
        content_type = flow.request.headers.get("Content-Type", "").lower()
        
        # Handle JSON
        if "application/json" in content_type:
            request_text = flow.request.content.decode('utf-8')
            request_data = json.loads(request_text)
            
            # Check common fields
            fields_to_check = ['text', 'content', 'message', 'body', 'code', 'prompt']
            
            def check_dict(d):
                if isinstance(d, dict):
                    for key, value in d.items():
                        if key in fields_to_check and isinstance(value, str):
                            if check_if_company_code(value):
                                return True
                        elif isinstance(value, (dict, list)):
                            if check_dict(value):
                                return True
                elif isinstance(d, list):
                    for item in d:
                        if check_dict(item):
                            return True
                return False
            
            return check_dict(request_data)
        
        # Handle form data
        elif "application/x-www-form-urlencoded" in content_type:
            request_text = flow.request.content.decode('utf-8')
            form_data = urllib.parse.parse_qs(request_text)
            
            for key, values in form_data.items():
                for value in values:
                    if check_if_company_code(value):
                        return True
        
        return False
    
    except Exception as e:
        print(f"Error handling generic POST: {e}")
        return False


class BlockProprietaryRequests:
    """
    Main MITM proxy addon that intercepts and checks requests.
    """
    
    def request(self, flow: http.HTTPFlow) -> None:
        """
        Called for every HTTP request.
        Checks if request contains proprietary code and blocks if found.
        """
        url = flow.request.url.lower()
        
        # Only check POST requests (where data is sent)
        if flow.request.method != 'POST':
            return
        
        blocked = False
        reason = ""
        
        # Check specific sites
        if "chatgpt.com" in url and "conversation" in url:
            print(f"📝 Checking ChatGPT request...")
            if handle_chatgpt(flow):
                blocked = True
                reason = "PROPRIETARY_CODE_IN_CHATGPT"
        
        elif ("x.com" in url or "twitter.com" in url) and "createtweet" in url:
            print(f"🐦 Checking Twitter request...")
            if handle_twitter(flow):
                blocked = True
                reason = "PROPRIETARY_CODE_IN_TWITTER"
        
        elif "stackoverflow.com" in url and "submit" in url:
            print(f"📚 Checking StackOverflow request...")
            if handle_stackoverflow(flow):
                blocked = True
                reason = "PROPRIETARY_CODE_IN_STACKOVERFLOW"
        
        # Generic check for LLM APIs (Claude Desktop, Cursor, etc.)
        elif any(domain in url for domain in [
            "api.openai.com",           # OpenAI API
            "api.anthropic.com",        # Claude API
            "generativelanguage.googleapis.com",  # Gemini API
            "api.cohere.ai",            # Cohere API
            "api.together.xyz",         # Together AI
            "api.perplexity.ai",        # Perplexity
            "api.mistral.ai",           # Mistral
        ]):
            print(f"🤖 Checking LLM API request to {url}...")
            if handle_generic_post(flow):
                blocked = True
                reason = "PROPRIETARY_CODE_IN_LLM_API"
        
        # Block if proprietary code detected
        if blocked:
            self.block(flow, reason)
    
    def block(self, flow: http.HTTPFlow, reason: str):
        """
        Block the request and return 403 response.
        """
        print(f"🚫 [{reason}] Blocking request to {flow.request.url}")
        
        flow.response = http.Response.make(
            403,
            b"Request blocked: Proprietary code detected. This request has been blocked to prevent code leakage.",
            {"Content-Type": "text/plain"}
        )


# Register the addon with mitmproxy
addons = [
    BlockProprietaryRequests()
]


# For running as standalone script
if __name__ == "__main__":
    print("="*70)
    print("BIFROST MITM PROXY")
    print("="*70)
    print()
    print("This proxy intercepts network traffic and blocks proprietary code leaks.")
    print()
    print("To start:")
    print("1. Install mitmproxy: pip install mitmproxy")
    print("2. Run: mitmdump -s security/mitm_proxy.py")
    print("3. Configure system proxy to 127.0.0.1:8080")
    print("4. Install mitmproxy certificate (for HTTPS)")
    print()
    print("Monitored sites:")
    print("  - ChatGPT (chatgpt.com)")
    print("  - Twitter/X (x.com, twitter.com)")
    print("  - StackOverflow (stackoverflow.com)")
    print("  - LLM APIs:")
    print("    • OpenAI (api.openai.com)")
    print("    • Anthropic/Claude (api.anthropic.com)")
    print("    • Google Gemini (generativelanguage.googleapis.com)")
    print("    • Cohere (api.cohere.ai)")
    print("    • Together AI (api.together.xyz)")
    print("    • Perplexity (api.perplexity.ai)")
    print("    • Mistral (api.mistral.ai)")
    print()
    print("This will protect:")
    print("  - Web browsers (ChatGPT, Twitter, etc.)")
    print("  - Terminal agents (Claude Code, Aider, etc.)")
    print("  - AI IDEs (Cursor, Windsurf, Continue.dev, etc.)")
    print("  - Custom scripts using LLM APIs")
    print()
    print("="*70)
