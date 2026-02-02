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
import base64
from .salesforce_utils import get_fresh_salesforce_credentials

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

def extract_email_body(payload):
    """
    Recursively extract text/plain or text/html body from Gmail message payload

    Args:
        payload: Gmail message payload object

    Returns:
        Decoded email body text or empty string if not found
    """
    body_text = ""

    # Check if body data exists directly (simple single-part message)
    if 'body' in payload and 'data' in payload['body']:
        data = payload['body']['data']
        body_text = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')
        return body_text

    # Check if multipart message (has parts)
    if 'parts' in payload:
        for part in payload['parts']:
            mime_type = part.get('mimeType', '')

            # Prefer text/plain content
            if mime_type == 'text/plain':
                if 'data' in part['body']:
                    data = part['body']['data']
                    body_text = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')
                    return body_text

            # Fallback to text/html if no plain text found yet
            elif mime_type == 'text/html' and not body_text:
                if 'data' in part['body']:
                    data = part['body']['data']
                    body_text = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')

            # Recursively check nested parts (for complex multipart messages)
            elif 'parts' in part:
                nested_body = extract_email_body(part)
                if nested_body:
                    return nested_body

    return body_text

# 2. Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Fetch emails from google
@mcp.tool()
def listEmails(context: Context, max_results: int = 10) -> str:
    """
    List recent emails from Gmail inbox with basic metadata (From, Subject, Date, ID)

    This tool returns email headers and IDs, but NOT the full email body content.
    To get full email body content, use the getEmailBodies() tool with the email IDs
    returned by this tool.

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
def createGmailDraft(context: Context, receiver: str, sender: str, subject: str, body: str):
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
def listGmailDrafts(context: Context, max_results: int = 10):
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
def editGmailDraft(context: Context, draft_id: str, subject: str = None, body: str = None):
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

@mcp.tool()
def getEmailBodies(context: Context, email_ids: list[str]) -> str:
    """
    Fetch full email bodies for specified email message IDs

    Use this tool to retrieve the complete content of emails. You can get email IDs
    from the listEmails() tool. This tool supports fetching 1 to 20 emails at once.
    The returned email bodies can then be summarized, analyzed, or processed.

    IMPORTANT: When user asks to summarize N emails, you MUST pass ALL N email IDs
    to this tool. Do not arbitrarily reduce the number of emails.

    Args:
        email_ids: List of Gmail message IDs (obtained from listEmails tool)

    Returns:
        Formatted string containing full email content (headers + body) for each email
    """
    creds = getGoogleCreds(context)
    if creds == None:
        return "User not authenticated with Google OAuth"

    try:
        # Validate input: limit to prevent token overflow and API rate limits
        if not email_ids:
            return "Error: Please provide at least one email ID"

        if len(email_ids) > 20:
            return "Error: Maximum 20 email IDs allowed per request. Please split into multiple requests."

        service = build("gmail", "v1", credentials=creds)

        result = f"Fetched {len(email_ids)} email(s):\n\n"

        for i, email_id in enumerate(email_ids, 1):
            # Fetch full message with complete MIME structure
            msg = service.users().messages().get(
                userId="me",
                id=email_id,
                format="full"
            ).execute()

            # Extract headers for metadata
            headers = {h["name"]: h["value"]
                      for h in msg.get("payload", {}).get("headers", [])}
            from_addr = headers.get("From", "Unknown")
            subject = headers.get("Subject", "(No subject)")
            date = headers.get("Date", "Unknown date")

            # Extract body content using helper function
            payload = msg.get("payload", {})
            body = extract_email_body(payload)

            if not body:
                body = "(No content or unsupported format)"

            # Truncate very long emails to prevent token overflow
            if len(body) > 5000:
                body = body[:5000] + "\n\n...(content truncated due to length)"

            # Format output in readable structure
            result += f"{'='*70}\n"
            result += f"EMAIL {i}/{len(email_ids)}\n"
            result += f"{'='*70}\n"
            result += f"From: {from_addr}\n"
            result += f"Subject: {subject}\n"
            result += f"Date: {date}\n"
            result += f"Message ID: {email_id}\n\n"
            result += f"Body:\n{body}\n\n"

        print(f"Successfully fetched {len(email_ids)} email bodies")
        return result

    except HttpError as error:
        print(f"An error occurred: {error}")
        return f"An error occurred: {error}"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return f"An unexpected error occurred: {e}"

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
        
@mcp.tool()
def addCalendarEvent(context: Context, summary: str, startTime: datetime, endTime: datetime, location: str = "", description: str = "", attendees: list[str] = [], reminders: list[int] = [] ):
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
    creds = getGoogleCreds(context)
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
                    'dateTime': startTime,
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': endTime,
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
def addAttendeeToEvent(context: Context, eventId: str, attendeeEmail: str, calendarId: str = "primary"):
    """
    Add an attendee to an existing Google Calendar event.

    Args:
        calendarId: The ID of the calendar (e.g., "primary" or a shared calendar ID)
        eventId: The ID of the event to update
        attendeeEmail: The email of the attendee to add
    """

    creds = getGoogleCreds(context)
    if creds == None:
        return "User not authenticated with Google OAuth"
    else:
        try:
            service = build("calendar", "v3", credentials=creds)

            # Get the current event
            event = service.events().get(calendarId=calendarId, eventId=eventId).execute()

            # Initialize attendees list if missing
            attendees = event.get("attendees", [])

            # Check if attendee already exists
            if any(a.get("email") == attendeeEmail for a in attendees):
                return {"status": "exists", "message": f"{attendeeEmail} is already an attendee."}

            # Add new attendee
            attendees.append({"email": attendeeEmail})

            # Update event
            event["attendees"] = attendees
            updated_event = service.events().update(
                calendarId=calendarId,
                eventId=eventId,
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

def getSalesforceCreds(ctx):
    """Retrieve Salesforce credentials for the logged-in user, refreshing if needed"""
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
                        current_creds = sf_service.get("credentials")
                        # Get fresh credentials (will refresh if needed)
                        fresh_creds = get_fresh_salesforce_credentials(user_id, current_creds)
                        return fresh_creds
        return None

    except Exception as e:
        print(f"Error getting Salesforce credentials: {e}")
        return None

@mcp.tool()
def summarizeEmail(email_content: str) -> str:
    """
    Summarize a single email's content using a structured prompt.

    This tool takes raw email content and returns a concise summary including:
    - Main purpose/topic of the email
    - Key action items or requests
    - Important deadlines or dates
    - Overall sentiment/urgency

    Args:
        email_content: The full text content of the email to summarize

    Returns:
        A structured summary of the email
    """
    # Create the summarization prompt
    summarization_prompt = f"""
Please analyze and summarize the following email. Provide a concise summary with these sections:

**Subject/Purpose:** What is this email about?
**Key Points:** Main information or topics discussed (bullet points)
**Action Items:** Any tasks, requests, or actions needed
**Deadlines/Dates:** Important dates or time-sensitive information
**Sentiment/Urgency:** Overall tone and priority level

Email content:
---
{email_content}
---

Summary:"""

    # Return the prompt which will be processed by the LLM
    # The LLM agent will see this prompt and generate the summary
    return summarization_prompt

@mcp.tool()
def summarizeRecentEmails(context: Context, num_emails: int = 5) -> str:
    """
    Fetch and summarize recent emails from Gmail inbox in one step.

    This is a convenience tool that combines listEmails, getEmailBodies, and summarizeEmail
    into a single operation. Use this when the user asks to summarize their recent emails.

    Args:
        num_emails: Number of recent emails to summarize (default: 5, max: 20)

    Returns:
        Formatted summaries of the requested number of emails with structured information
    """
    creds = getGoogleCreds(context)
    if creds == None:
        return "User not authenticated with Google OAuth"

    try:
        # Limit num_emails to reasonable bounds
        num_emails = min(max(1, num_emails), 20)

        # Step 1: List recent emails to get IDs
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(
            userId="me",
            labelIds=["INBOX"],
            maxResults=num_emails
        ).execute()

        messages = results.get("messages", [])
        if not messages:
            return "No messages found in inbox."

        # Step 2: Fetch full email bodies for all emails
        summaries = f"Summaries of your {len(messages)} most recent emails:\n\n"

        for i, message in enumerate(messages, 1):
            # Fetch full message
            msg = service.users().messages().get(
                userId="me",
                id=message["id"],
                format="full"
            ).execute()

            # Extract headers
            headers = {h["name"]: h["value"]
                      for h in msg.get("payload", {}).get("headers", [])}
            from_addr = headers.get("From", "Unknown")
            subject = headers.get("Subject", "(No subject)")
            date = headers.get("Date", "Unknown date")

            # Extract body
            payload = msg.get("payload", {})
            body = extract_email_body(payload)
            if not body:
                body = "(No content or unsupported format)"

            # Truncate very long emails
            if len(body) > 3000:
                body = body[:3000] + "\n...(truncated)"

            # Format the summary prompt for this email
            summaries += f"{'='*70}\n"
            summaries += f"EMAIL {i}/{len(messages)}\n"
            summaries += f"{'='*70}\n"
            summaries += f"From: {from_addr}\n"
            summaries += f"Subject: {subject}\n"
            summaries += f"Date: {date}\n\n"

            # Add the summarization instruction
            summaries += f"""Please analyze and summarize this email:

**Subject/Purpose:** What is this email about?
**Key Points:** Main information or topics discussed
**Action Items:** Any tasks or requests
**Deadlines/Dates:** Important dates
**Sentiment/Urgency:** Tone and priority

Email body:
{body}

---

"""

        summaries += f"\nPlease provide concise summaries for all {len(messages)} emails above."

        return summaries

    except HttpError as error:
        print(f"An error occurred: {error}")
        return f"An error occurred: {error}"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return f"An unexpected error occurred: {e}"

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


@mcp.tool()
def createSalesforceCase(context: Context, subject: str,
                           description: str = "",
                           origin: str = "Web",
                           status: str = "New"):
    """
    Creates a Salesforce case if a related one doesn't already exist.
    Returns: Case ID on success.
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return "User not authenticated with Salesforce."

    instance_url = creds.get('instance_url')
    access_token = creds.get('access_token')

    url = f"{instance_url}/services/data/v60.0/sobjects/Case"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "Subject": subject,
        "Description": description,
        "Origin": origin,
        "Status": status
    }

    resp = requests.post(url, json=payload, headers=headers)

    if resp.status_code not in (200, 201):
        return {
            "success": False,
            "status_code": resp.status_code,
            "error": resp.text
        }

    data = resp.json()
    return {
        "success": data.get("success", False),
        "case_id": data.get("id"),
        "errors": data.get("errors", [])
    }

@mcp.tool()
def listSalesforceCases(context: Context, limit: int = 10):
    """
    List the most recent Salesforce Cases for a user.
    
    Args:
        limit: number of cases to retrieve (default 10)
        
    Returns:
        List of cases with Id, Subject, Status, CreatedDate
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return "User not authenticated with Salesforce."

    instance_url = creds.get("instance_url")
    access_token = creds.get("access_token")

    if not instance_url or not access_token:
        return {"success": False, "error": "Incomplete Salesforce credentials."}

    # query for cases
    query = f"SELECT Id, Subject, Status, CreatedDate FROM Case ORDER BY CreatedDate DESC LIMIT {limit}"
    url = f"{instance_url}/services/data/v60.0/query"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    params = {"q": query}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        cases = data.get("records", [])
        return {"success": True, "cases": cases}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": str(e), "response": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}


