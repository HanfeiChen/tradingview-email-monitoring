import os
import time
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

load_dotenv()  # load environment variables from .env file


# define the email address to monitor
monitor_email = "example@gmail.com"

def ensure_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

# define the code to execute when a new email arrives
def on_email_received():
    print("New email received!")

# function to check for new emails and execute the code if one is found
def check_for_new_emails():
    # set up Gmail API client
    creds = ensure_credentials()
    service = build("gmail", "v1", credentials=creds)

    try:
        # search for unread emails from the monitored email address
        response = service.users().messages().list(
            userId="me",
            q=f"from:{monitor_email} is:unread"
        ).execute()

        messages = []
        if "messages" in response:
            messages.extend(response["messages"])

        # iterate over each unread email and execute the code
        for message in messages:
            msg = service.users().messages().get(userId="me", id=message["id"]).execute()
            payload = msg["payload"]
            headers = payload["headers"]
            for header in headers:
                if header["name"] == "From" and monitor_email in header["value"]:
                    on_email_received()

            # mark the email as read
            service.users().messages().modify(userId="me", id=message["id"], body={"removeLabelIds": ["UNREAD"]}).execute()

    except HttpError as error:
        print(f"An error occurred: {error}")

# continuously check for new emails every 10 seconds
while True:
    check_for_new_emails()
    time.sleep(10)
