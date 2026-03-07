import os
import pickle
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]

def _get_gmail_service():
    """Helper to get an authenticated Gmail API service instance."""
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
            
    return build("gmail", "v1", credentials=creds)

def get_customer_emails(customer_email):
    """Fetches recent emails sent by the customer."""
    print(f"\n--- [GMAIL TOOL] Searching emails from {customer_email} ---")
    service = _get_gmail_service()
    
    # Execute search query
    results = service.users().messages().list(
        userId='me',
        q=f"from:{customer_email}",
        maxResults=3
    ).execute()

    messages = results.get("messages", [])
    
    if not messages:
        return "No recent emails found."

    summaries = []

    for msg in messages:
        # Get the full message
        message = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        # Extract snippet as summary
        snippet = message.get("snippet", "No snippet available.")
        
        # Extract Date for context
        headers = message.get("payload", {}).get("headers", [])
        date = next((header["value"] for header in headers if header["name"].lower() == "date"), "Unknown Date")
        
        summaries.append(f"Date: {date}\nSnippet: {snippet}")

    return "\n---\n".join(summaries)

def search_emails_by_keyword(keyword):
    """Fetches recent emails matching a specific keyword."""
    print(f"\n--- [GMAIL TOOL] Searching emails for keyword: '{keyword}' ---")
    service = _get_gmail_service()
    
    # Execute search query
    results = service.users().messages().list(
        userId='me',
        q=keyword,
        maxResults=3
    ).execute()

    messages = results.get("messages", [])
    
    if not messages:
        return f"No emails found for keyword '{keyword}'."

    summaries = []

    for msg in messages:
        message = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        snippet = message.get("snippet", "No snippet available.")
        headers = message.get("payload", {}).get("headers", [])
        date = next((header["value"] for header in headers if header["name"].lower() == "date"), "Unknown Date")
        # Added Subject extraction for extra clarity
        subject = next((header["value"] for header in headers if header["name"].lower() == "subject"), "No Subject")
        
        summaries.append(f"Date: {date}\nSubject: {subject}\nSnippet: {snippet}")

    return "\n---\n".join(summaries)

from email.message import EmailMessage

def send_email(to, subject, body):
    """Sends an email using the Gmail API."""
    print(f"\n--- [GMAIL TOOL] Sending email to {to} ---")
    service = _get_gmail_service()
    
    message = EmailMessage()
    message.set_content(body)
    message['To'] = to
    message['From'] = 'me'
    message['Subject'] = subject
    
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    
    try:
        sent_message = service.users().messages().send(userId="me", body=create_message).execute()
        print(f"Message Id: {sent_message['id']}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
