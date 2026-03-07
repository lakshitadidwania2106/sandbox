import os
from agno.agent import Agent
from agno.models.google import Gemini

def get_api_key():
    with open(".env") as f:
        for line in f:
            if line.startswith("GOOGLE_API_KEY"):
                return line.strip().split("=")[1].strip()

os.environ["GOOGLE_API_KEY"] = get_api_key()

agent = Agent(
    model=Gemini(id="gemini-2.5-flash"),
    instructions="Say hello world"
)
print("Agent initialized. Running...")
response = agent.run("Test message")
print("Response:", response.content)
