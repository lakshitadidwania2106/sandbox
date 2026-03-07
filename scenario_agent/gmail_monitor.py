import os
import time
import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from pync import Notifier

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def authenticate():
    creds = None

    # Load saved token
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If credentials not valid, login again
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)

    return service


def get_sender(headers):
    for header in headers:
        if header["name"] == "From":
            return header["value"]
    return "Unknown Sender"


def monitor_gmail():
    print("📧 Gmail monitoring started...")

    service = authenticate()

    last_message_id = None

    while True:
        try:
            results = service.users().messages().list(
                userId="me",
                maxResults=1
            ).execute()

            messages = results.get("messages", [])

            if not messages:
                time.sleep(10)
                continue

            msg_id = messages[0]["id"]

            if msg_id != last_message_id:

                msg = service.users().messages().get(
                    userId="me",
                    id=msg_id
                ).execute()

                headers = msg["payload"]["headers"]

                sender = get_sender(headers)

                print(f"📩 New email from: {sender}")

                Notifier.notify(
                    f"Email from: {sender}",
                    title="New Gmail",
                    sound=True
                )

                last_message_id = msg_id

        except Exception as e:
            print("Gmail monitor error:", e)

        time.sleep(15)