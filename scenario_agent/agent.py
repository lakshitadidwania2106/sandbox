import os

from agno.agent import Agent
from agno.models.google import Gemini
from tools.system_tools import query_database, run_shell


# function to read API key directly from .env file
def get_api_key():
    with open(".env") as f:
        for line in f:
            if line.startswith("GOOGLE_API_KEY"):
                return line.strip().split("=")[1]

api_key = get_api_key()

print("API KEY LOADED:", api_key[:10], "...")

# Use Bifrost gateway as proxy
bifrost_url = os.getenv("BIFROST_URL", "http://localhost:8080")
print(f"🌈 Using Bifrost Gateway: {bifrost_url}")

agent = Agent(
    model=Gemini(
        id="gemini-2.5-flash",
        api_key=api_key,
        base_url=bifrost_url  # Route through Bifrost
    ),
    tools=[
        query_database,
        run_shell
    ],
    instructions="""
You are an IT support AI agent.

You can:
- query internal databases
- check system logs
- help employees
"""
)

print("✅ Agent initialized with Bifrost security layers")
print("   → Lakera: Prompt injection detection")
print("   → OPA: Policy enforcement")
print("   → Presidio: PII scrubbing")
print()

while True:
    user_input = input("\nUser: ")

    if user_input.lower() == "exit":
        break

    try:
        response = agent.run(user_input)
        print("\nAgent:", response.content)
    except Exception as e:
        print(f"\n❌ Error: {e}")