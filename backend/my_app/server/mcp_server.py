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
from .salesforce_utils import get_fresh_salesforce_credentials, salesforce_api_request
from .telesign_auth import (
    send_sms,
    send_voice_call,
    verify_phone_number,
    send_verification_code,
    verify_code,
    assess_phone_risk,
    get_message_status,
    get_detailed_message_status,
    poll_message_until_complete,
    batch_verify_phones,
    batch_send_sms
)

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


# ==================== CONTACTS & ACCOUNTS ====================

@mcp.tool()
def createSalesforceContact(context: Context, last_name: str, first_name: str = "", 
                           email: str = "", phone: str = "", account_id: str = ""):
    """
    Create a new Salesforce Contact.
    
    Args:
        last_name: Contact's last name (required)
        first_name: Contact's first name (optional)
        email: Contact's email address (optional)
        phone: Contact's phone number (optional)
        account_id: Salesforce Account ID to link this contact to (optional)
        
    Returns:
        dict with success flag and contact_id or error details
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    payload = {"LastName": last_name}
    if first_name:
        payload["FirstName"] = first_name
    if email:
        payload["Email"] = email
    if phone:
        payload["Phone"] = phone
    if account_id:
        payload["AccountId"] = account_id
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "POST",
        "/services/data/v60.0/sobjects/Contact",
        data=payload
    )
    
    if result["success"] and "data" in result:
        return {
            "success": True,
            "contact_id": result["data"].get("id"),
            "errors": result["data"].get("errors", [])
        }
    return result


@mcp.tool()
def listSalesforceContacts(context: Context, limit: int = 10, account_id: str = ""):
    """
    List Salesforce Contacts with optional filtering by Account.
    
    Args:
        limit: Maximum number of contacts to return (default 10)
        account_id: Optional Account ID to filter contacts
        
    Returns:
        dict with success flag and list of contacts
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    query = f"SELECT Id, FirstName, LastName, Email, Phone, AccountId FROM Contact"
    if account_id:
        query += f" WHERE AccountId = '{account_id}'"
    query += f" ORDER BY CreatedDate DESC LIMIT {limit}"
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "GET",
        "/services/data/v60.0/query",
        params={"q": query}
    )
    
    if result["success"] and "data" in result:
        return {"success": True, "contacts": result["data"].get("records", [])}
    return result


@mcp.tool()
def createSalesforceAccount(context: Context, name: str, industry: str = "", 
                           phone: str = "", website: str = ""):
    """
    Create a new Salesforce Account (company/organization).
    
    Args:
        name: Account name (required)
        industry: Industry type (optional)
        phone: Account phone number (optional)
        website: Company website (optional)
        
    Returns:
        dict with success flag and account_id or error details
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    payload = {"Name": name}
    if industry:
        payload["Industry"] = industry
    if phone:
        payload["Phone"] = phone
    if website:
        payload["Website"] = website
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "POST",
        "/services/data/v60.0/sobjects/Account",
        data=payload
    )
    
    if result["success"] and "data" in result:
        return {
            "success": True,
            "account_id": result["data"].get("id"),
            "errors": result["data"].get("errors", [])
        }
    return result


@mcp.tool()
def listSalesforceAccounts(context: Context, limit: int = 10):
    """
    List Salesforce Accounts (companies/organizations).
    
    Args:
        limit: Maximum number of accounts to return (default 10)
        
    Returns:
        dict with success flag and list of accounts
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    query = f"SELECT Id, Name, Industry, Phone, Website FROM Account ORDER BY CreatedDate DESC LIMIT {limit}"
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "GET",
        "/services/data/v60.0/query",
        params={"q": query}
    )
    
    if result["success"] and "data" in result:
        return {"success": True, "accounts": result["data"].get("records", [])}
    return result


# ==================== OPPORTUNITIES ====================

@mcp.tool()
def createSalesforceOpportunity(context: Context, name: str, stage: str, close_date: str,
                                amount: float = 0, account_id: str = ""):
    """
    Create a new Salesforce Opportunity (sales deal).
    
    Args:
        name: Opportunity name (required)
        stage: Sales stage (e.g., "Prospecting", "Qualification", "Closed Won") (required)
        close_date: Expected close date in YYYY-MM-DD format (required)
        amount: Deal amount in dollars (optional)
        account_id: Associated Account ID (optional)
        
    Returns:
        dict with success flag and opportunity_id or error details
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    payload = {
        "Name": name,
        "StageName": stage,
        "CloseDate": close_date
    }
    if amount > 0:
        payload["Amount"] = amount
    if account_id:
        payload["AccountId"] = account_id
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "POST",
        "/services/data/v60.0/sobjects/Opportunity",
        data=payload
    )
    
    if result["success"] and "data" in result:
        return {
            "success": True,
            "opportunity_id": result["data"].get("id"),
            "errors": result["data"].get("errors", [])
        }
    return result


@mcp.tool()
def listSalesforceOpportunities(context: Context, limit: int = 10, stage: str = ""):
    """
    List Salesforce Opportunities with optional stage filtering.
    
    Args:
        limit: Maximum number of opportunities to return (default 10)
        stage: Optional stage name to filter by (e.g., "Prospecting", "Closed Won")
        
    Returns:
        dict with success flag and list of opportunities
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    query = f"SELECT Id, Name, StageName, Amount, CloseDate, AccountId FROM Opportunity"
    if stage:
        query += f" WHERE StageName = '{stage}'"
    query += f" ORDER BY CreatedDate DESC LIMIT {limit}"
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "GET",
        "/services/data/v60.0/query",
        params={"q": query}
    )
    
    if result["success"] and "data" in result:
        return {"success": True, "opportunities": result["data"].get("records", [])}
    return result


@mcp.tool()
def updateSalesforceOpportunity(context: Context, opportunity_id: str, stage: str = "",
                                amount: float = None, close_date: str = ""):
    """
    Update an existing Salesforce Opportunity.
    
    Args:
        opportunity_id: Opportunity ID to update (required)
        stage: New sales stage (optional)
        amount: New deal amount (optional)
        close_date: New close date in YYYY-MM-DD format (optional)
        
    Returns:
        dict with success flag or error details
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    payload = {}
    if stage:
        payload["StageName"] = stage
    if amount is not None:
        payload["Amount"] = amount
    if close_date:
        payload["CloseDate"] = close_date
    
    if not payload:
        return {"success": False, "error": "No fields provided to update"}
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "PATCH",
        f"/services/data/v60.0/sobjects/Opportunity/{opportunity_id}",
        data=payload
    )
    
    return result


# ==================== SEARCH (SOQL/SOSL) ====================

@mcp.tool()
def salesforceSOQLQuery(context: Context, query: str):
    """
    Execute a custom SOQL (Salesforce Object Query Language) query.
    
    Args:
        query: SOQL query string (e.g., "SELECT Id, Name FROM Account WHERE Industry = 'Technology'")
        
    Returns:
        dict with success flag and query results
        
    Example queries:
        - "SELECT Id, Name, Email FROM Contact WHERE LastName = 'Smith'"
        - "SELECT Id, Subject, Status FROM Case WHERE Status = 'New'"
        - "SELECT COUNT() FROM Opportunity WHERE StageName = 'Closed Won'"
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "GET",
        "/services/data/v60.0/query",
        params={"q": query}
    )
    
    if result["success"] and "data" in result:
        return {
            "success": True,
            "records": result["data"].get("records", []),
            "total_size": result["data"].get("totalSize", 0)
        }
    return result


@mcp.tool()
def salesforceSOSLSearch(context: Context, search_text: str, objects: str = "Contact,Account,Lead"):
    """
    Execute a SOSL (Salesforce Object Search Language) full-text search across multiple objects.
    
    Args:
        search_text: Text to search for (e.g., "John Smith")
        objects: Comma-separated list of objects to search (default: "Contact,Account,Lead")
        
    Returns:
        dict with success flag and search results grouped by object type
        
    Example:
        salesforceSOSLSearch("john.doe@example.com", "Contact,Lead")
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    # Build SOSL query
    sosl_query = f"FIND {{{search_text}}} IN ALL FIELDS RETURNING {objects}"
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "GET",
        "/services/data/v60.0/search",
        params={"q": sosl_query}
    )
    
    if result["success"] and "data" in result:
        return {"success": True, "search_records": result["data"].get("searchRecords", [])}
    return result


# ==================== EMAIL ====================

@mcp.tool()
def sendSalesforceEmail(context: Context, to_addresses: str, subject: str, body: str,
                        html_body: str = "", cc_addresses: str = ""):
    """
    Send an email through Salesforce.
    
    Args:
        to_addresses: Comma-separated email addresses (e.g., "user@example.com,other@example.com")
        subject: Email subject line
        body: Plain text email body
        html_body: Optional HTML email body
        cc_addresses: Optional comma-separated CC email addresses
        
    Returns:
        dict with success flag or error details
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    to_list = [addr.strip() for addr in to_addresses.split(",")]
    cc_list = [addr.strip() for addr in cc_addresses.split(",")] if cc_addresses else []
    
    payload = {
        "inputs": [{
            "toAddress": ";".join(to_list),
            "subject": subject,
            "plainTextBody": body
        }]
    }
    
    if html_body:
        payload["inputs"][0]["htmlBody"] = html_body
    if cc_list:
        payload["inputs"][0]["ccAddress"] = ";".join(cc_list)
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "POST",
        "/services/data/v60.0/actions/standard/emailSimple",
        data=payload
    )
    
    return result


# ==================== USER INFO & LIMITS ====================

@mcp.tool()
def getSalesforceUserInfo(context: Context):
    """
    Get information about the currently authenticated Salesforce user.
    
    Returns:
        dict with user details including name, email, username, org info, permissions
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    # Get user ID from credentials
    sf_id = creds.get("id", "")
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "GET",
        sf_id  # The ID URL contains user info endpoint
    )
    
    return result


@mcp.tool()
def getSalesforceOrgLimits(context: Context):
    """
    Get Salesforce organization limits including API calls, data storage, and other quotas.
    
    Returns:
        dict with all org limits showing max, remaining, and usage for each resource
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "GET",
        "/services/data/v60.0/limits"
    )
    
    return result


# ==================== CHATTER ====================

@mcp.tool()
def postSalesforceChatter(context: Context, message: str, mention_user_id: str = ""):
    """
    Post a message to Salesforce Chatter feed.
    
    Args:
        message: Message text to post
        mention_user_id: Optional Salesforce User ID to @mention in the post
        
    Returns:
        dict with success flag and post details
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    # Build message segments
    segments = []
    if mention_user_id:
        segments.append({
            "type": "Mention",
            "id": mention_user_id
        })
        segments.append({
            "type": "Text",
            "text": f" {message}"
        })
    else:
        segments.append({
            "type": "Text",
            "text": message
        })
    
    payload = {
        "body": {
            "messageSegments": segments
        }
    }
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "POST",
        "/services/data/v60.0/chatter/feed-elements",
        data=payload
    )
    
    return result


@mcp.tool()
def getSalesforceChatterFeed(context: Context, limit: int = 10):
    """
    Get recent Chatter feed posts.
    
    Args:
        limit: Maximum number of posts to retrieve (default 10, max 100)
        
    Returns:
        dict with success flag and list of feed items
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    # Limit to max 100
    limit = min(limit, 100)
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "GET",
        f"/services/data/v60.0/chatter/feeds/news/me/feed-elements",
        params={"pageSize": limit}
    )
    
    if result["success"] and "data" in result:
        return {"success": True, "feed_items": result["data"].get("elements", [])}
    return result


# ==================== TASKS & EVENTS ====================

@mcp.tool()
def createSalesforceTask(context: Context, subject: str, priority: str = "Normal",
                         status: str = "Not Started", due_date: str = "",
                         related_to_id: str = ""):
    """
    Create a new Salesforce Task (to-do item).
    
    Args:
        subject: Task subject/description (required)
        priority: Priority level - "High", "Normal", or "Low" (default: "Normal")
        status: Task status - "Not Started", "In Progress", "Completed" (default: "Not Started")
        due_date: Due date in YYYY-MM-DD format (optional)
        related_to_id: ID of related record (Account, Contact, Opportunity, etc.) (optional)
        
    Returns:
        dict with success flag and task_id or error details
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    payload = {
        "Subject": subject,
        "Priority": priority,
        "Status": status
    }
    if due_date:
        payload["ActivityDate"] = due_date
    if related_to_id:
        payload["WhatId"] = related_to_id
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "POST",
        "/services/data/v60.0/sobjects/Task",
        data=payload
    )
    
    if result["success"] and "data" in result:
        return {
            "success": True,
            "task_id": result["data"].get("id"),
            "errors": result["data"].get("errors", [])
        }
    return result


@mcp.tool()
def listSalesforceTasks(context: Context, limit: int = 10, status: str = ""):
    """
    List Salesforce Tasks with optional status filtering.
    
    Args:
        limit: Maximum number of tasks to return (default 10)
        status: Optional status filter ("Not Started", "In Progress", "Completed")
        
    Returns:
        dict with success flag and list of tasks
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    query = f"SELECT Id, Subject, Status, Priority, ActivityDate FROM Task"
    if status:
        query += f" WHERE Status = '{status}'"
    query += f" ORDER BY CreatedDate DESC LIMIT {limit}"
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "GET",
        "/services/data/v60.0/query",
        params={"q": query}
    )
    
    if result["success"] and "data" in result:
        return {"success": True, "tasks": result["data"].get("records", [])}
    return result


@mcp.tool()
def createSalesforceEvent(context: Context, subject: str, start_datetime: str,
                          end_datetime: str, location: str = "", description: str = ""):
    """
    Create a new Salesforce Event (calendar appointment).
    
    Args:
        subject: Event subject/title (required)
        start_datetime: Start date/time in ISO format (e.g., "2026-03-15T14:00:00Z") (required)
        end_datetime: End date/time in ISO format (required)
        location: Event location (optional)
        description: Event description (optional)
        
    Returns:
        dict with success flag and event_id or error details
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    payload = {
        "Subject": subject,
        "StartDateTime": start_datetime,
        "EndDateTime": end_datetime
    }
    if location:
        payload["Location"] = location
    if description:
        payload["Description"] = description
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "POST",
        "/services/data/v60.0/sobjects/Event",
        data=payload
    )
    
    if result["success"] and "data" in result:
        return {
            "success": True,
            "event_id": result["data"].get("id"),
            "errors": result["data"].get("errors", [])
        }
    return result


@mcp.tool()
def listSalesforceEvents(context: Context, limit: int = 10, from_date: str = ""):
    """
    List Salesforce Events (calendar appointments).
    
    Args:
        limit: Maximum number of events to return (default 10)
        from_date: Optional filter for events starting from this date (YYYY-MM-DD format)
        
    Returns:
        dict with success flag and list of events
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    query = f"SELECT Id, Subject, StartDateTime, EndDateTime, Location FROM Event"
    if from_date:
        query += f" WHERE StartDateTime >= {from_date}T00:00:00Z"
    query += f" ORDER BY StartDateTime DESC LIMIT {limit}"
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "GET",
        "/services/data/v60.0/query",
        params={"q": query}
    )
    
    if result["success"] and "data" in result:
        return {"success": True, "events": result["data"].get("records", [])}
    return result


# ==================== FILES & CONTENT ====================

@mcp.tool()
def uploadSalesforceFile(context: Context, title: str, file_data: str, 
                        file_extension: str = "txt", related_record_id: str = ""):
    """
    Upload a file to Salesforce Files (ContentVersion).
    
    Args:
        title: File title/name without extension
        file_data: Base64-encoded file content
        file_extension: File extension (e.g., "txt", "pdf", "jpg") (default: "txt")
        related_record_id: Optional ID of record to associate file with
        
    Returns:
        dict with success flag and file details (ContentVersion ID and ContentDocument ID)
        
    Note: file_data should be base64-encoded. For text files, you can use:
          import base64; base64.b64encode(b"your text content").decode()
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    payload = {
        "Title": title,
        "PathOnClient": f"{title}.{file_extension}",
        "VersionData": file_data
    }
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "POST",
        "/services/data/v60.0/sobjects/ContentVersion",
        data=payload
    )
    
    if result["success"] and "data" in result and related_record_id:
        # Link file to record using ContentDocumentLink
        version_id = result["data"].get("id")
        
        # Get ContentDocument ID from ContentVersion
        doc_query = f"SELECT ContentDocumentId FROM ContentVersion WHERE Id = '{version_id}'"
        doc_result = salesforce_api_request(
            creds["instance_url"],
            creds["access_token"],
            "GET",
            "/services/data/v60.0/query",
            params={"q": doc_query}
        )
        
        if doc_result["success"] and doc_result.get("data", {}).get("records"):
            doc_id = doc_result["data"]["records"][0]["ContentDocumentId"]
            
            # Create ContentDocumentLink
            link_payload = {
                "ContentDocumentId": doc_id,
                "LinkedEntityId": related_record_id,
                "ShareType": "V"
            }
            salesforce_api_request(
                creds["instance_url"],
                creds["access_token"],
                "POST",
                "/services/data/v60.0/sobjects/ContentDocumentLink",
                data=link_payload
            )
    
    return result


@mcp.tool()
def listSalesforceFiles(context: Context, limit: int = 10):
    """
    List recently uploaded Salesforce Files.
    
    Args:
        limit: Maximum number of files to return (default 10)
        
    Returns:
        dict with success flag and list of files with metadata
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    query = f"SELECT Id, Title, FileExtension, ContentSize, CreatedDate FROM ContentDocument ORDER BY CreatedDate DESC LIMIT {limit}"
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "GET",
        "/services/data/v60.0/query",
        params={"q": query}
    )
    
    if result["success"] and "data" in result:
        return {"success": True, "files": result["data"].get("records", [])}
    return result


@mcp.tool()
def downloadSalesforceFile(context: Context, content_version_id: str):
    """
    Download a file from Salesforce Files by ContentVersion ID.
    
    Args:
        content_version_id: The ContentVersion ID of the file to download
        
    Returns:
        dict with success flag and base64-encoded file data
    """
    creds = getSalesforceCreds(context)
    if not creds:
        return {"success": False, "error": "User not authenticated with Salesforce."}
    
    result = salesforce_api_request(
        creds["instance_url"],
        creds["access_token"],
        "GET",
        f"/services/data/v60.0/sobjects/ContentVersion/{content_version_id}/VersionData"
    )
    
    return result


# ==================== TELESIGN MCP TOOLS ====================
# Comprehensive TeleSign tools for self-service accounts

@mcp.tool()
def sendSMS(phone_number: str, message: str, message_type: str = "OTP") -> str:
    """
    Send an SMS message using TeleSign
    
    Args:
        phone_number: Target phone number (e.g., "2623984079" or "+12623984079")
        message: SMS message text to send (max 160 chars for single message)
        message_type: Message type - OTP (default), ARN (alerts), or MKT (marketing)
    
    Returns:
        JSON string with status, reference_id, and delivery status
    
    Example:
        sendSMS("2623984079", "Your code is 12345", "OTP")
    """
    try:
        result = send_sms(phone_number, message, message_type)
        
        if result.get('success'):
            return json.dumps({
                "success": True,
                "message": "SMS sent successfully",
                "reference_id": result.get('reference_id'),
                "status": result.get('status'),
                "phone_number": phone_number
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": result.get('errors', 'Unknown error'),
                "status_code": result.get('status_code')
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def sendVoiceCall(phone_number: str, message: str, voice_name: str = "female") -> str:
    """
    Send a voice call with text-to-speech message
    
    Args:
        phone_number: Target phone number
        message: Message to speak (text-to-speech)
        voice_name: Voice type - "female" or "male" (default: "female")
    
    Returns:
        JSON string with status and reference_id
    
    Example:
        sendVoiceCall("2623984079", "Your verification code is 1 2 3 4 5")
    """
    try:
        result = send_voice_call(phone_number, message, voice_name)
        
        if result.get('success'):
            return json.dumps({
                "success": True,
                "message": "Voice call initiated",
                "reference_id": result.get('reference_id'),
                "phone_number": phone_number
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": result.get('error', 'Voice call failed'),
                "status_code": result.get('status_code')
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def verifyPhoneNumber(phone_number: str) -> str:
    """
    Verify a phone number and get detailed information including carrier, location, and type
    
    Args:
        phone_number: Phone number to verify (e.g., "2623984079")
    
    Returns:
        JSON string with phone type, carrier, location, contact info, and whether it's blocked
    
    Example:
        verifyPhoneNumber("2623984079")
    """
    try:
        result = verify_phone_number(phone_number)
        
        if result.get('success'):
            return json.dumps({
                "success": True,
                "phone_number": result.get('formatted_number'),
                "phone_type": result.get('phone_type'),
                "carrier": result.get('carrier'),
                "country": result.get('country'),
                "country_code": result.get('country_code'),
                "city": result.get('city'),
                "state": result.get('state'),
                "time_zone": result.get('time_zone'),
                "blocked": result.get('blocked'),
                "contact_info": result.get('contact_info'),
                "reference_id": result.get('reference_id')
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": result.get('error', 'Verification failed')
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def sendVerificationCode(phone_number: str, code_length: int = 5) -> str:
    """
    Send a 2FA verification code via SMS
    
    Args:
        phone_number: Target phone number (e.g., "2623984079")
        code_length: Length of verification code (3-10, default: 5)
    
    Returns:
        JSON string with reference_id and verification code
        Store the reference_id and verify_code to validate user input later
    
    Example:
        sendVerificationCode("2623984079", 6)
    """
    try:
        result = send_verification_code(phone_number, code_length)
        
        if result.get('success'):
            return json.dumps({
                "success": True,
                "message": "Verification code sent",
                "reference_id": result.get('reference_id'),
                "verify_code": result.get('verify_code'),  # Store this to verify user input
                "phone_number": phone_number
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": result.get('errors', 'Failed to send code')
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def verifyUserCode(reference_id: str, user_code: str, original_code: str) -> str:
    """
    Verify a code entered by the user against the original code
    
    Args:
        reference_id: Reference ID from sendVerificationCode
        user_code: Code entered by the user
        original_code: Original verify_code from sendVerificationCode result
    
    Returns:
        JSON string with validation result
    
    Example:
        verifyUserCode("ref123", "12345", "12345")
    """
    try:
        result = verify_code(reference_id, user_code, original_code)
        
        return json.dumps({
            "success": True,
            "valid": result.get('valid'),
            "message": result.get('message'),
            "reference_id": reference_id
        }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def checkPhoneRisk(phone_number: str, lifecycle_event: str = "create") -> str:
    """
    Assess fraud risk for a phone number using TeleSign Intelligence
    
    Args:
        phone_number: Phone number to assess (e.g., "2623984079")
        lifecycle_event: Account lifecycle stage:
            - "create": New account creation (default)
            - "sign-in": User login
            - "transact": Financial transaction
            - "update": Account update
    
    Returns:
        JSON string with risk level (low/medium/high), risk score (0-1000), 
        recommendation (allow/flag/block), and phone details
    
    Example:
        checkPhoneRisk("2623984079", "create")
    """
    try:
        result = assess_phone_risk(phone_number, lifecycle_event)
        
        if result.get('success'):
            return json.dumps({
                "success": True,
                "phone_number": phone_number,
                "risk_level": result.get('risk_level'),
                "risk_score": result.get('risk_score'),
                "recommendation": result.get('recommendation'),
                "phone_type": result.get('phone_type'),
                "carrier": result.get('carrier'),
                "reference_id": result.get('reference_id')
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": result.get('error', 'Risk assessment failed')
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def checkMessageStatus(reference_id: str) -> str:
    """
    Check the delivery status of a sent message (SMS or voice)
    
    Args:
        reference_id: Reference ID from sendSMS, sendVoiceCall, or sendVerificationCode
    
    Returns:
        JSON string with delivery status, timestamps, and any errors
    
    Status codes:
        - 200-299: Delivered successfully
        - 400-499: Failed (invalid number, blocked, etc.)
        - 500-599: TeleSign error
    
    Example:
        checkMessageStatus("ref_abc123xyz")
    """
    try:
        result = get_message_status(reference_id)
        
        if result.get('success'):
            return json.dumps({
                "success": True,
                "reference_id": reference_id,
                "status": result.get('status'),
                "delivered": result.get('status', {}).get('code') in [200, 203, 207, 290, 291, 295]
            }, indent=2)
        else:
            return json.dumps({
                "success": False,
                "error": result.get('error', 'Status check failed')
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def getDetailedMessageStatus(reference_id: str) -> str:
    """
    Get detailed delivery status including timestamps, carrier feedback, and pricing
    
    Args:
        reference_id: Reference ID from a sent message
    
    Returns:
        JSON string with detailed status including:
        - Delivery timestamps (submitted_at, completed_on, updated_on)
        - Carrier error codes and descriptions
        - Message price and currency
        - Recipient details
    
    Example:
        getDetailedMessageStatus("ref_abc123xyz")
    """
    try:
        result = get_detailed_message_status(reference_id)
        
        return json.dumps({
            "success": result.get('status_code') == 200,
            "reference_id": reference_id,
            "status_code": result.get('message_status_code'),
            "status_description": result.get('status_description'),
            "submitted_at": result.get('submitted_at'),
            "completed_on": result.get('completed_on'),
            "updated_on": result.get('updated_on'),
            "recipient": result.get('recipient'),
            "price": result.get('price'),
            "currency": result.get('currency'),
            "errors": result.get('errors', [])
        }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def pollMessageStatusUntilComplete(reference_id: str, max_attempts: int = 10) -> str:
    """
    Poll message status repeatedly until delivered or failed (useful for testing)
    
    Args:
        reference_id: Reference ID from a sent message
        max_attempts: Maximum polling attempts (default: 10, waits 2 sec between)
    
    Returns:
        JSON string with final delivery status
    
    Note: This tool blocks until the message is delivered or fails.
    For production, use checkMessageStatus with webhooks instead.
    
    Example:
        pollMessageStatusUntilComplete("ref_abc123xyz", 5)
    """
    try:
        result = poll_message_until_complete(reference_id, max_attempts)
        
        return json.dumps({
            "success": result.get('polling_complete', False),
            "reference_id": reference_id,
            "status": result.get('status_description'),
            "delivered": not result.get('failed', False),
            "attempts": result.get('attempts'),
            "timeout": result.get('timeout', False)
        }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def batchVerifyPhoneNumbers(phone_numbers: str) -> str:
    """
    Verify multiple phone numbers in batch
    
    Args:
        phone_numbers: Comma-separated phone numbers (e.g., "2623984079,3105551234,4155551234")
    
    Returns:
        JSON string with verification results for each number
    
    Example:
        batchVerifyPhoneNumbers("2623984079,3105551234")
    """
    try:
        # Parse comma-separated numbers
        numbers = [n.strip() for n in phone_numbers.split(',')]
        
        results = batch_verify_phones(numbers)
        
        return json.dumps({
            "success": True,
            "total_numbers": len(numbers),
            "results": results
        }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def batchSendSMS(recipients_json: str) -> str:
    """
    Send SMS to multiple recipients
    
    Args:
        recipients_json: JSON array of recipients with phone_number and message
            Example: '[{"phone_number":"2623984079","message":"Hello"},{"phone_number":"3105551234","message":"Hi"}]'
    
    Returns:
        JSON string with send results for each recipient
    
    Example:
        batchSendSMS('[{"phone_number":"2623984079","message":"Test 1"}]')
    """
    try:
        recipients = json.loads(recipients_json)
        
        results = batch_send_sms(recipients)
        
        return json.dumps({
            "success": True,
            "total_recipients": len(recipients),
            "results": results
        }, indent=2)
            
    except json.JSONDecodeError:
        return json.dumps({
            "success": False,
            "error": "Invalid JSON format. Expected array of {phone_number, message} objects"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

# ==================== END TELESIGN TOOLS ====================


