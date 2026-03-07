from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from config.settings import ANTHROPIC_API_KEY
from agent.tools import tools

llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    api_key=ANTHROPIC_API_KEY,
    temperature=0
)

agent = create_agent(llm, tools=tools)

# In-memory conversation history for context
_messages = []


def run_agent(user_input):
    global _messages
    _messages.append(HumanMessage(content=user_input))
    result = agent.invoke({"messages": _messages})
    _messages = result["messages"]
    # Get last AI message content (final response after tool use)
    from langchain_core.messages import AIMessage
    for msg in reversed(_messages):
        if isinstance(msg, AIMessage) and msg.content:
            return str(msg.content)
    return "No response generated."
