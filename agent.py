import os
import db_tool
import gmail_tool
from google import genai
from google.genai import types

# function to read environment variables from .env file
def load_env():
    env_vars = {}
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    env_vars[key.strip()] = val.strip()
    return env_vars

env = load_env()
if "GOOGLE_API_KEY" in env:
    api_key = env["GOOGLE_API_KEY"]
else:
    print("WARNING: GOOGLE_API_KEY not found in .env file.")
    api_key = None

# Initialize the Gemini client
client = genai.Client(api_key=api_key)

def customer_support_agent(question, email):
    
    print("\n[AGENT] Gathering context for email:", email)
    
    # Tool 1: Check Database for Orders & Tickets
    orders = db_tool.search_orders(email)
    tickets = db_tool.search_tickets(email)
    
    # Tool 2: Check Gmail for past correspondence
    emails = gmail_tool.get_customer_emails(email)
    
    # Tool 3: Check Gmail for 'amazon' keyword
    amazon_emails = gmail_tool.search_emails_by_keyword("amazon")
    
    print("[AGENT] Context gathered. Asking LLM...\n")

    context = f"""
Customer email: {email}

Orders from Database:
{orders}

Tickets from Database:
{tickets}

Previous Emails from Gmail (from customer):
{emails}

Previous Emails from Gmail (keyword 'amazon'):
{amazon_emails}

User Question:
{question}
"""
    
    sys_instruct = "You are a helpdesk customer support assistant for an ecommerce company. Use the provided context to answer questions. If there is a new complaint and no open ticket exists for it, suggest that you've created one (or use the info from the database if they ask about an existing one). Be polite and professional."
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=context,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct,
            ),
        )
        return response.text
    except Exception as e:
        print(f"\n[ALERT] LLM Error: {e}")
        return f"""**[System Fallback Mode Active - Invalid API Key]**
        
I am the Agent, but my LLM connection is currently offline due to an invalid API Key.
However, I successfully pulled your context automatically!

**Based on my DB & Gmail Search:**
*   **Your Orders:** {orders}
*   **Your Tickets:** {tickets}
*   **Recent Emails:** {emails[:150]}...

If my LLM was online, I would now synthesize this information into a human-readable response for you!"""

def ask_agent(query, email):
    """Wrapper format for API calls."""
    return customer_support_agent(query, email)

def main():
    print("\n--- AI Customer Care Demo ---")
    email = "lakshita21lr@gmail.com"
    print(f"Welcome! Connected to the default profile: '{email}'")
    
    print("\n[Automatically Checking Amazon Order...]")
    initial_response = customer_support_agent("Tell me about my Amazon order", email)
    print("\n[Agent]:", initial_response)
    
    print("\nType 'exit' to quit.")
    while True:
        try:
            user_input = input("\n[Raise Ticket] You: ")
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.lower() in ['exit', 'quit', 'q']:
            break

        if not user_input.strip():
            continue

        # Automatically fetches from DB and Gmail and synthesizes answer
        response = customer_support_agent(user_input, email)
        
        print("\n[Agent]:", response)

if __name__ == "__main__":
    main()