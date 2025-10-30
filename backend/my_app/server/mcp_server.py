import base64
import datetime
import email
from email.message import EmailMessage
from mcp.server.fastmcp import FastMCP, Context
from .token_verifier import SimpleTokenVerifier
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import json
import os
import jwt
from pathlib import Path
import time
import requests

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# 1. Create the MCP server instance with the token verifier and auth settings
mcp = FastMCP(
    name="IntegratedDemo",
    stateless_http=True, # Use stateless mode for simple web mounting
    token_verifier=SimpleTokenVerifier(),
    auth=AuthSettings(
        # The issuer URL should point to where the auth server lives.
        issuer_url=AnyHttpUrl("http://localhost:8000/auth"),
        # The resource server URL is the URL of this MCP server.
        resource_server_url=AnyHttpUrl("http://localhost:8000/mcp"),
    ),
)

# Set the server to mount at the root of the path
mcp.settings.streamable_http_path = "/"
    
def getGoogleCreds(ctx) -> Credentials:
    try:
        # extract the jwt from the request to get the subject
        encoded_token = ctx.request_context.request.headers.get('Authorization').split(" ")[1]
        payload = jwt.decode(encoded_token, JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get('sub')

        # fetch google tokens for the user
        with open(Path(__file__).parent / "oauth.json", "r") as f:
            data = json.load(f)
            users = data.get("users", [])
            for user in users:
                if user.get("user_id") == user_id:
                    # NEW SCHEMA: Access google service from services object
                    google_service = user.get("services", {}).get("google")
                    if google_service:
                        credentials_json = google_service.get("credentials")
                        if credentials_json:
                            return Credentials.from_authorized_user_info(json.loads(credentials_json))
            return None

    except Exception as e:
        print(f"Error getting Google credentials: {e}")
        return None

# 2. Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Fetch emails from google
@mcp.tool()
def listEmails(context: Context, max_results: int = 10) -> str:
    """
    List recent emails from Gmail inbox

    Args:
        max_results: Maximum number of emails to return (default: 10, max: 50)
    """
    creds = getGoogleCreds(context)
    if creds == None:
        return "User not authenticated with Google OAuth"

    try:
        # Limit max_results to reasonable bounds
        max_results = min(max(1, max_results), 50)

        # Call the Gmail API to fetch emails
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(
            userId="me",
            labelIds=["INBOX"],
            maxResults=max_results
        ).execute()

        messages = results.get("messages", [])

        if not messages:
            return "No messages found in inbox."

        # Format the messages into a string
        res = f"Found {len(messages)} recent emails:\n\n"

        for i, message in enumerate(messages, 1):
            msg = service.users().messages().get(
                userId="me",
                id=message["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            ).execute()

            # Extract headers
            headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
            from_addr = headers.get("From", "Unknown")
            subject = headers.get("Subject", "(No subject)")
            date = headers.get("Date", "Unknown date")

            res += f"{i}. From: {from_addr}\n"
            res += f"   Subject: {subject}\n"
            res += f"   Date: {date}\n"
            res += f"   ID: {message['id']}\n\n"

        print(f"Found and formatted {len(messages)} emails")
        return res


    except HttpError as error:
        print(f"An error occurred: {error}")
        return f"An error occurred: {error}"

# Write an email draft
@mcp.tool()
def gmail_create_draft(context: Context, receiver: str, sender: str, subject: str, body: str):
    """
    Create and insert a draft email.
    Params:
        receiver: the email address who should receive the email
        sender: the email address of the sender
        subject: the subject line of the email
        body: the body of the email
    """
    creds = getGoogleCreds(context)
    if creds == None:
        return "User not authenticated with Google OAuth"
    else:
        try:
            # create gmail api client
            service = build("gmail", "v1", credentials=creds)

            message = EmailMessage()

            message.set_content(body)

            message["To"] = receiver
            message["From"] = sender
            message["Subject"] = subject

            # encoded message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {"message": {"raw": encoded_message}}
            draft = (
                service.users()
                .drafts()
                .create(userId="me", body=create_message)
                .execute()
            )
            
            return f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}'

        except HttpError as error:
            print(f"An error occurred: {error}")
            return f"An error occurred: {error}"

@mcp.tool()
def gmail_list_drafts(context: Context, max_results: int = 10):
    """
    List Gmail drafts for the authenticated user.
    Use gmail_list_drafts to find a draft_id before calling gmail_edit_draft.
    Params:
        max_results: The maximum number of drafts to list (default 10).
    """
    creds = getGoogleCreds(context)
    if creds is None:
        return "User not authenticated with Google OAuth"

    try:
        service = build("gmail", "v1", credentials=creds)
        drafts_response = (
            service.users()
            .drafts()
            .list(userId="me", maxResults=max_results)
            .execute()
        )

        drafts = drafts_response.get("drafts", [])
        if not drafts:
            return "No drafts found."

        result_lines = []
        for d in drafts:
            # Fetch draft details to get subject, recipients, etc.
            draft_detail = (
                service.users()
                .drafts()
                .get(userId="me", id=d["id"])
                .execute()
            )
            message = draft_detail.get("message", {})
            headers = message.get("payload", {}).get("headers", [])

            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(no subject)")
            to = next((h["value"] for h in headers if h["name"] == "To"), "(no recipient)")

            result_lines.append(f"Draft ID: {d['id']}\nSubject: {subject}\nTo: {to}\n---")

        return "\n".join(result_lines)

    except HttpError as error:
        print(f"An error occurred: {error}")
        return f"An error occurred while listing drafts: {error}"

# Edit an existing Gmail draft
@mcp.tool()
def gmail_edit_draft(context: Context, draft_id: str, subject: str = None, body: str = None):
    """
    Edit an existing Gmail draft.
    Use gmail_list_drafts to find a draft_id before calling gmail_edit_draft.
    Params:
        draft_id: The Gmail draft ID to update.
        subject: Optional new subject line for the draft.
        body: Optional new body text for the draft.
    """
    creds = getGoogleCreds(context)
    if creds is None:
        return "User not authenticated with Google OAuth"

    try:
        # Create Gmail API client
        service = build("gmail", "v1", credentials=creds)

        # Retrieve the existing draft to update
        existing_draft = (
            service.users()
            .drafts()
            .get(userId="me", id=draft_id)
            .execute()
        )

        # Decode the existing message so we can edit its content
        raw_message = existing_draft["message"]["raw"]
        decoded_bytes = base64.urlsafe_b64decode(raw_message.encode("utf-8"))
        message = EmailMessage()
        message.set_content("")  # placeholder
        message = email.message_from_bytes(decoded_bytes)

        # Update subject or body if provided
        if subject:
            message.replace_header("Subject", subject)
        if body:
            # If multipart, replace first text/plain part; otherwise, set new content
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        part.set_payload(body)
                        break
            else:
                message.set_content(body)

        # Re-encode the updated message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        update_body = {"message": {"raw": encoded_message}}

        # Update the draft in Gmail
        updated_draft = (
            service.users()
            .drafts()
            .update(userId="me", id=draft_id, body=update_body)
            .execute()
        )

        return f'Draft {draft_id} updated successfully.\nNew subject: {message["Subject"]}\nNew body: {body or "[unchanged]"}'

    except HttpError as error:
        print(f"An error occurred: {error}")
        return f"An error occurred while updating draft: {error}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# list upcoming events from google calendar
@mcp.tool()
def listUpcomingEvents(context: Context, numEvents=5):
    """List upcoming events from my calendar"""
    creds = getGoogleCreds(context)
    if creds == None:
        return "User not authenticated with Google OAuth"
    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=numEvents,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        if not events:
            return "No upcoming events found."

        # Prints the start and name of the next n events
        res = ""
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            res += f"\nStart {start}: {event['summary']}"
        return res
    except HttpError as error:
        print(f"An error occurred: {error}")
        return f"An error occurred: {error}"
        
# 3. Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello from your MCP resource, {name}!"

def getSalesforceCreds(ctx):
    """Retrieve Salesforce credentials for the logged-in user"""
    try:
        JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        encoded_token = ctx.request_context.request.headers.get('Authorization').split(" ")[1]
        payload = jwt.decode(encoded_token, JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get('sub')

        with open(Path(__file__).parent / "oauth.json", "r") as f:
            data = json.load(f)
            for user in data.get("users", []):
                if user["user_id"] == user_id:
                    # NEW SCHEMA: Access salesforce service from services object
                    sf_service = user.get("services", {}).get("salesforce")
                    if sf_service:
                        return sf_service.get("credentials")
        return None

    except Exception as e:
        print(f"Error getting Salesforce credentials: {e}")
        return None

@mcp.tool()
def listAccounts(context: Context) -> str:
    """Fetch Account data from Salesforce"""
    creds = getSalesforceCreds(context)
    if not creds:
        return "User not authenticated with Salesforce."
    
    access_token = creds["access_token"]
    instance_url = creds["instance_url"]
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(f"{instance_url}/services/data/v61.0/sobjects/Account", headers=headers)
    if r.status_code == 200:
        return json.dumps(r.json(), indent=2)
    return f"Error: {r.text}"

