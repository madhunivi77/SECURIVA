import datetime
from mcp.server.fastmcp import FastMCP, Context
from .token_verifier import SimpleTokenVerifier
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import os
import jwt
from pathlib import Path
import time

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
    
def get_google_creds(ctx) -> Credentials:
    try:
        # extract the jwt from the request to get the subject
        encoded_token = ctx.request_context.request.headers.get('Authorization').split(" ")[1]
        payload = jwt.decode(encoded_token, JWT_SECRET_KEY, algorithms=["HS256"])
        subject = payload.get('sub')

        # fetch google tokens for the subject
        with open(Path(__file__).parent / "oauth.json", "r") as f:
            data = json.load(f)
            users = data.get("users", [])
            for user in users:
                if user.get("user_id") == subject:
                    # build credentials from google_creds json
                    return Credentials.from_authorized_user_info(json.loads(user.get("google_creds")))
            else:
                return None
            
    except Exception as e:
        print(e)

# 2. Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Fetch emails from google
@mcp.tool()
def list_emails(context: Context) -> str:
    """List my emails"""
    creds = get_google_creds(context)
    if creds == None:
        return "User not authenticated with Google OAuth"
    else:
        # query google
        try:
            # Call the Gmail API to fetch emails
            service = build("gmail", "v1", credentials=creds)
            results = (
                service.users().messages().list(userId="me", labelIds=["INBOX"]).execute()
            )
            messages = results.get("messages", [])

            if not messages:
                print("No messages found.")
                return

            # Format the messages into a string
            res = "Messages:"
            for message in messages:
                res += f'\nMessage ID: {message["id"]}\n'
                msg = (
                    service.users().messages().get(userId="me", id=message["id"]).execute()
                )
                res += f'Subject: {msg["snippet"]}'

        except HttpError as error:
            print(f"An error occurred: {error}")
            return f"An error occurred: {error}"
        print("emails found")
        return res

# list upcoming events from google calendar
@mcp.tool()
def list_upcoming_events(context: Context, numEvents=5):
    """List upcoming events from my calendar"""
    creds = get_google_creds(context)
    if creds == None:
        return "User not authenticated with Google OAuth"
    else:
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
                res += f"\n{event['summary']} at {start}"
            return res
        except HttpError as error:
            print(f"An error occurred: {error}")
            return f"An error occurred: {error}"
        
@mcp.tool()
def add_calendar_event(context: Context, summary: str, start_time: datetime, end_time: datetime, location: str = "", description: str = "", attendees: list[str] = [], reminders: list[int] = [] ):
    """
    Create an event in my calendar
    Args:
        summary: The name of the event
        startTime: A DateTime object representing the requested start time
        endTime: A DateTime object representing the requested end time
        location: A string representation of the location of the meeting
        description: Any further details specified about the event
        attendees: a list of email addresses of the people to attend the event
        reminders: a list of integers representing the number of seconds before the event that the atendees should be notified
    """
    creds = get_google_creds(context)
    if creds == None:
        return "User not authenticated with Google OAuth"
    else:
        try:
            service = build("calendar", "v3", credentials=creds)
            event = {
                'summary': summary,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'America/Los_Angeles',
                },
                'recurrence': [],
                'attendees': [{'email': item} for item in attendees],
                'reminders': {
                    'useDefault': False,
                    'overrides': [{'method': 'email', 'minutes': sec} for sec in reminders],
                },
            }
            event = service.events().insert(calendarId='primary', body=event).execute()
            print(f"Event created: {(event.get('htmlLink'))}")
            return f"Event created: {(event.get('htmlLink'))}"
        except Exception as error:
            print(f"An error occurred: {error}")
            return f"An error occurred: {error}"

@mcp.tool()
def add_attendee_to_event(context: Context, event_id: str, attendee_email: str, calendar_id: str = "primary"):
    """
    Add an attendee to an existing Google Calendar event.

    Args:
        calendar_id: The ID of the calendar (e.g., "primary" or a shared calendar ID)
        event_id: The ID of the event to update
        attendee_email: The email of the attendee to add
        credentials: Authorized Google credentials (already fetched elsewhere)
    """

    creds = get_google_creds(context)
    if creds == None:
        return "User not authenticated with Google OAuth"
    else:
        try:
            service = build("calendar", "v3", credentials=creds)

            # Get the current event
            event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

            # Initialize attendees list if missing
            attendees = event.get("attendees", [])

            # Check if attendee already exists
            if any(a.get("email") == attendee_email for a in attendees):
                return {"status": "exists", "message": f"{attendee_email} is already an attendee."}

            # Add new attendee
            attendees.append({"email": attendee_email})

            # Update event
            event["attendees"] = attendees
            updated_event = service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates="all"  # Sends email notification to new attendee
            ).execute()

            return f"Success. Updated attendees: {[a['email'] for a in updated_event.get('attendees', [])]}"
        except Exception as error:
            print(f"An error occurred: {error}")
            return f"An error occurred: {error}"

# 3. Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello from your MCP resource, {name}!"
