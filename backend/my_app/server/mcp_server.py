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
from concurrent.futures import ThreadPoolExecutor
from groq import Groq
from .salesforce_utils import get_fresh_salesforce_credentials, load_oauth_data, salesforce_api_request
from ..config.settings import settings
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
from .compliance_tools import (
    get_compliance_overview,
    get_compliance_requirements,
    get_compliance_checklist,
    get_penalty_information,
    get_breach_notification_requirements,
    cross_reference_compliance_topic,
    search_compliance_requirements,
    generate_compliance_report
)
from .compliance_module_generator import (
    create_compliance_module_dry_run,
    create_compliance_module,
    list_compliance_modules
)
from .guidance_catalog import GuidanceCatalog

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
guidance_catalog = GuidanceCatalog()

LEGACY_DECISION_TREE_MAP = {
    "email_compliance": "email_compliance_decision",
    "data_sharing": "data_sharing_decision",
    "data_deletion": "data_deletion_decision",
    "vendor_access": "vendor_access_decision",
}

# 1. Create the MCP server instance with the token verifier and auth settings
mcp = FastMCP(
    name="IntegratedDemo",
    stateless_http=True, # Use stateless mode for simple web mounting
    token_verifier=SimpleTokenVerifier(),
    auth=AuthSettings(
        # The issuer URL should point to where the auth server lives.
        issuer_url=AnyHttpUrl(f"{settings.BACKEND_URL}/auth"),
        # The resource server URL is the URL of this MCP server.
        resource_server_url=AnyHttpUrl(f"{settings.BACKEND_URL}/mcp"),
    ),
)

# Set the server to mount at the root of the path
mcp.settings.streamable_http_path = "/"
    
def getGoogleCreds(ctx) -> Credentials:
    try:
        if not JWT_SECRET_KEY:
            print("JWT_SECRET_KEY not configured")
            return None

        t0 = time.time()
        # extract the jwt from the request to get the subject
        encoded_token = ctx.request_context.request.headers.get('Authorization').split(" ")[1]
        payload = jwt.decode(encoded_token, JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get('sub')

        # fetch google tokens for the user
        data = load_oauth_data()
        users = data.get("users", [])
        for user in users:
            if user.get("user_id") == user_id:
                # NEW SCHEMA: Access google service from services object
                google_service = user.get("services", {}).get("google")
                if not google_service:
                    print(f"⚠️  [MCP-TOOL] getGoogleCreds: No google service configured for user={user_id}")
                    return None
                credentials_json = google_service.get("credentials")
                if not credentials_json:
                    print(f"⚠️  [MCP-TOOL] getGoogleCreds: No credentials stored for user={user_id}")
                    return None
                creds = Credentials.from_authorized_user_info(json.loads(credentials_json))
                print(f"⏱️  [MCP-TOOL] getGoogleCreds: {((time.time()-t0)*1000):.0f}ms")
                return creds

        print(f"⚠️  [MCP-TOOL] getGoogleCreds: No user found in oauth.json for user_id={user_id}")
        return None

    except Exception as e:
        print(f"❌ [MCP-TOOL] getGoogleCreds exception: {type(e).__name__}: {e}")
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

        # Batch fetch all message metadata in a single HTTP request
        fetched = {}
        def metadata_callback(request_id, response, exception):
            if exception is None:
                fetched[request_id] = response

        batch = service.new_batch_http_request(callback=metadata_callback)
        for message in messages:
            batch.add(
                service.users().messages().get(
                    userId="me",
                    id=message["id"],
                    format="metadata",
                    metadataHeaders=["From", "Subject", "Date"]
                ),
                request_id=message["id"],
            )
        batch.execute()

        # Format the messages into a string (preserve original order)
        res = f"Found {len(messages)} recent emails:\n\n"

        for i, message in enumerate(messages, 1):
            msg = fetched.get(message["id"], {})
            headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
            from_addr = headers.get("From", "Unknown")
            subject = headers.get("Subject", "(No subject)")
            date = headers.get("Date", "Unknown date")

            res += f"{i}. From: {from_addr}\n"
            res += f"   Subject: {subject}\n"
            res += f"   Date: {date}\n"
            res += f"   ID: {message['id']}\n\n"

        print(f"Found and formatted {len(messages)} emails (batched)")
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

        # Batch fetch all draft details in a single HTTP request
        fetched_drafts = {}
        def draft_callback(request_id, response, exception):
            if exception is None:
                fetched_drafts[request_id] = response

        batch = service.new_batch_http_request(callback=draft_callback)
        for d in drafts:
            batch.add(
                service.users().drafts().get(userId="me", id=d["id"]),
                request_id=d["id"],
            )
        batch.execute()

        result_lines = []
        for d in drafts:
            draft_detail = fetched_drafts.get(d["id"], {})
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

        # Batch fetch all email bodies in a single HTTP request
        fetched = {}
        def body_callback(request_id, response, exception):
            if exception is None:
                fetched[request_id] = response

        batch = service.new_batch_http_request(callback=body_callback)
        for email_id in email_ids:
            batch.add(
                service.users().messages().get(
                    userId="me",
                    id=email_id,
                    format="full"
                ),
                request_id=email_id,
            )
        batch.execute()

        result = f"Fetched {len(email_ids)} email(s):\n\n"

        for i, email_id in enumerate(email_ids, 1):
            msg = fetched.get(email_id, {})

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

        print(f"Successfully fetched {len(email_ids)} email bodies (batched)")
        return result

    except HttpError as error:
        print(f"An error occurred: {error}")
        return f"An error occurred: {error}"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return f"An unexpected error occurred: {e}"

# list upcoming events from google calendar
@mcp.tool()
def listUpcomingEvents(context: Context, numEvents: int = 5):
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
        if not JWT_SECRET_KEY:
            print("JWT_SECRET_KEY not configured")
            return None

        encoded_token = ctx.request_context.request.headers.get('Authorization').split(" ")[1]
        payload = jwt.decode(encoded_token, JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get('sub')

        data = load_oauth_data()
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

def _summarize_one_email(client: Groq, from_addr: str, subject: str, date: str, body: str) -> str:
    """Summarize a single email via Groq. Called in parallel from a thread pool."""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": (
                    f"Summarize this email in 1-2 sentences. Be concise.\n"
                    f"From: {from_addr}\nSubject: {subject}\nDate: {date}\n\n{body[:1000]}"
                ),
            }],
            max_tokens=80,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"(Could not summarize: {e})"
@mcp.tool()
def summarizeRecentEmails(context: Context, num_emails: int = 5) -> str:
    """
    Fetch and summarize recent emails from Gmail inbox in one step.

    This is a convenience tool that combines listEmails, getEmailBodies, and summarizeEmail
    into a single operation. Use this when the user asks to summarize their recent emails.

    Args:
        num_emails: Number of recent emails to summarize (default: 5, max: 20)

    Returns:
        Pre-summarized email summaries ready to read aloud
    """
    creds = getGoogleCreds(context)
    if creds == None:
        return "User not authenticated with Google OAuth"

    try:
        t0 = time.time()
        num_emails = min(max(1, num_emails), 20)

        # Step 1: List recent emails to get IDs
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(
            userId="me",
            labelIds=["INBOX"],
            maxResults=num_emails
        ).execute()
        t1 = time.time()
        print(f"⏱️  [MCP-TOOL] summarizeRecentEmails: gmail_list={((t1-t0)*1000):.0f}ms")

        messages = results.get("messages", [])
        if not messages:
            return "No messages found in inbox."

        # Step 2: Batch fetch all email bodies in a single HTTP request
        fetched = {}
        def fetch_callback(request_id, response, exception):
            if exception is None:
                fetched[request_id] = response

        batch = service.new_batch_http_request(callback=fetch_callback)
        for message in messages:
            batch.add(
                service.users().messages().get(
                    userId="me",
                    id=message["id"],
                    format="full"
                ),
                request_id=message["id"],
            )
        batch.execute()
        t_batch = time.time()
        print(f"⏱️  [MCP-TOOL] summarizeRecentEmails: batch_fetch={((t_batch-t1)*1000):.0f}ms ({len(messages)} emails)")

        # Step 3: Extract email data for summarization
        emails_to_summarize = []
        for message in messages:
            msg = fetched.get(message["id"], {})
            headers = {h["name"]: h["value"]
                      for h in msg.get("payload", {}).get("headers", [])}
            from_addr = headers.get("From", "Unknown")
            subject = headers.get("Subject", "(No subject)")
            date = headers.get("Date", "Unknown date")
            body = extract_email_body(msg.get("payload", {})) or "(No content)"
            emails_to_summarize.append((from_addr, subject, date, body))

        # Step 4: Parallel Groq summarization — all emails at once
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        summaries_list = [None] * len(emails_to_summarize)

        with ThreadPoolExecutor(max_workers=len(emails_to_summarize)) as executor:
            futures = {}
            for i, (from_addr, subject, date, body) in enumerate(emails_to_summarize):
                future = executor.submit(_summarize_one_email, groq_client, from_addr, subject, date, body)
                futures[future] = i
            for future in futures:
                idx = futures[future]
                summaries_list[idx] = future.result()

        t_summarize = time.time()
        print(f"⏱️  [MCP-TOOL] summarizeRecentEmails: parallel_summarize={((t_summarize-t_batch)*1000):.0f}ms ({len(messages)} emails)")

        # Step 5: Format pre-summarized results
        result = f"Here are your {len(messages)} most recent emails:\n\n"
        for i, (from_addr, subject, date, body) in enumerate(emails_to_summarize, 1):
            result += f"{i}. From: {from_addr}\n"
            result += f"   Subject: {subject}\n"
            result += f"   Summary: {summaries_list[i-1]}\n\n"

        t2 = time.time()
        print(f"⏱️  [MCP-TOOL] summarizeRecentEmails: TOTAL={((t2-t0)*1000):.0f}ms ({len(messages)} emails)")
        return result

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


# ==================== COMPLIANCE STANDARDS TOOLS ====================
# Tools for querying GDPR, HIPAA, and PCI-DSS compliance standards

@mcp.tool()
def getComplianceOverview(standard: str) -> str:
    """
    Get an overview of a compliance standard (GDPR, HIPAA, or PCI-DSS)
    
    Args:
        standard: Compliance standard name - must be one of: 'gdpr', 'hipaa', 'pci_dss'
    
    Returns:
        JSON string with standard overview including name, region, effective date, and description
    
    Example:
        getComplianceOverview('gdpr')
    """
    try:
        result = get_compliance_overview(standard)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def getComplianceRequirements(standard: str, requirement_id: str = None) -> str:
    """
    Get detailed compliance requirements for a standard
    
    Args:
        standard: Compliance standard name ('gdpr', 'hipaa', 'pci_dss')
        requirement_id: Optional specific requirement ID to retrieve
    
    Returns:
        JSON string with detailed requirements, articles/sections, and implementation guidance
    
    Example:
        getComplianceRequirements('gdpr')
        getComplianceRequirements('pci_dss', '3')
    """
    try:
        # Convert requirement_id to int if it's a number
        if requirement_id and requirement_id.isdigit():
            requirement_id = int(requirement_id)
        
        result = get_compliance_requirements(standard, requirement_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def getComplianceChecklist(standard: str) -> str:
    """
    Get a compliance audit checklist for the specified standard
    
    Args:
        standard: Compliance standard name ('gdpr', 'hipaa', 'pci_dss')
    
    Returns:
        JSON string with checklist items grouped by category for audit preparation
    
    Example:
        getComplianceChecklist('hipaa')
    """
    try:
        result = get_compliance_checklist(standard)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def getPenaltyInformation(standard: str) -> str:
    """
    Get penalty and fine information for non-compliance
    
    Args:
        standard: Compliance standard name ('gdpr', 'hipaa', 'pci_dss')
    
    Returns:
        JSON string with penalty tiers, amounts, and violation types
    
    Example:
        getPenaltyInformation('gdpr')
    """
    try:
        result = get_penalty_information(standard)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def getBreachNotificationRequirements(standard: str) -> str:
    """
    Get breach notification requirements and timelines for a standard
    
    Args:
        standard: Compliance standard name ('gdpr', 'hipaa', 'pci_dss')
    
    Returns:
        JSON string with notification timelines and requirements
    
    Example:
        getBreachNotificationRequirements('hipaa')
    """
    try:
        result = get_breach_notification_requirements(standard)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def crossReferenceComplianceTopic(topic: str) -> str:
    """
    Cross-reference a compliance topic across GDPR, HIPAA, and PCI-DSS
    Shows how each standard addresses the same topic
    
    Args:
        topic: Compliance topic - must be one of:
               'data_encryption', 'access_control', 'audit_logging', 
               'breach_notification', 'data_retention'
    
    Returns:
        JSON string with cross-referenced requirements from all three standards
    
    Example:
        crossReferenceComplianceTopic('data_encryption')
    """
    try:
        result = cross_reference_compliance_topic(topic)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def searchComplianceRequirements(query: str, standards_json: str = None) -> str:
    """
    Search for compliance requirements matching a query across standards
    
    Args:
        query: Search query string
        standards_json: Optional JSON array of standards to search.
                       Example: '["gdpr","hipaa"]'
                       If not provided, searches all standards
    
    Returns:
        JSON string with matching requirements from specified standards
    
    Example:
        searchComplianceRequirements('encryption')
        searchComplianceRequirements('access control', '["gdpr","hipaa"]')
    """
    try:
        standards = None
        if standards_json:
            standards = json.loads(standards_json)
        
        result = search_compliance_requirements(query, standards)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def generateComplianceReport(standards_json: str, include_checklist: bool = True, 
                             include_penalties: bool = True, include_breach_info: bool = True) -> str:
    """
    Generate a comprehensive compliance report for specified standards
    
    Args:
        standards_json: JSON array of standards to include.
                       Example: '["gdpr","hipaa","pci_dss"]'
        include_checklist: Include compliance checklists (default: True)
        include_penalties: Include penalty information (default: True)
        include_breach_info: Include breach notification requirements (default: True)
    
    Returns:
        JSON string with comprehensive compliance report
    
    Example:
        generateComplianceReport('["gdpr","hipaa"]')
        generateComplianceReport('["pci_dss"]', True, True, False)
    """
    try:
        standards = json.loads(standards_json)
        
        result = generate_compliance_report(
            standards=standards,
            include_checklist=include_checklist,
            include_penalties=include_penalties,
            include_breach_info=include_breach_info
        )
        return json.dumps(result, indent=2)
    except json.JSONDecodeError:
        return json.dumps({
            "success": False,
            "error": "Invalid JSON format. Expected array of standard names like ['gdpr','hipaa']"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

# ==================== END COMPLIANCE TOOLS ====================


# ==================== COMPLIANCE CONFIRMATION TOOLS ====================
# Tools for AI to confirm understanding before taking actions

@mcp.tool()
def confirmComplianceUnderstanding(
    user_request: str,
    my_understanding: str,
    planned_action: str,
    standards_involved: str = ""
) -> str:
    """
    Confirm understanding with the user before generating compliance documents or reports.
    
    USE THIS TOOL when a user asks you to create, generate, or analyze compliance information.
    This ensures accuracy and allows the user to correct any misunderstandings.
    
    Args:
        user_request: The exact request from the user (e.g., "Create a HIPAA compliance report")
        my_understanding: Your interpretation of what the user wants
        planned_action: What you plan to do next (e.g., "Generate comprehensive HIPAA report with checklist")
        standards_involved: Compliance standards you'll use (e.g., "HIPAA, GDPR")
    
    Returns:
        JSON string formatted as a confirmation prompt for the user
    
    Example:
        confirmComplianceUnderstanding(
            user_request="I need GDPR and HIPAA compliance docs",
            my_understanding="You need comprehensive compliance documentation for both GDPR and HIPAA standards",
            planned_action="Generate full compliance reports including requirements, checklists, and penalties",
            standards_involved="GDPR, HIPAA"
        )
    
    The user will respond with confirmation or corrections, and you should proceed accordingly.
    """
    try:
        confirmation = {
            "message_type": "confirmation_request",
            "original_request": user_request,
            "my_understanding": my_understanding,
            "planned_action": planned_action,
            "standards_involved": standards_involved,
            "confirmation_prompt": f"""
📋 **Let me confirm I understood correctly:**

**Your Request:** {user_request}

**My Understanding:** {my_understanding}

**What I'll Do:** {planned_action}
{f'**Standards:** {standards_involved}' if standards_involved else ''}

✅ **Is this correct?** 
- Reply "yes" or "confirm" to proceed
- Reply with corrections if I misunderstood something

""",
            "next_steps": [
                "If confirmed: Proceed with planned action",
                "If corrected: Adjust understanding and re-confirm",
                "If unclear: Ask clarifying questions"
            ]
        }
        
        return json.dumps(confirmation, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def summarizeComplianceRequest(
    standards: str,
    information_needed: str,
    output_format: str = "report"
) -> str:
    """
    Summarize what compliance information will be gathered before retrieving it.
    
    Use this to show the user what data you'll collect and in what format.
    
    Args:
        standards: Comma-separated list of standards (e.g., "GDPR, HIPAA, PCI-DSS")
        information_needed: What information to retrieve (e.g., "requirements, penalties, checklists")
        output_format: How the data will be presented (e.g., "report", "checklist", "comparison table")
    
    Returns:
        JSON string with summary of what will be retrieved
    
    Example:
        summarizeComplianceRequest(
            standards="GDPR, HIPAA",
            information_needed="breach notification requirements, penalties",
            output_format="comparison table"
        )
    """
    try:
        standards_list = [s.strip() for s in standards.split(",")]
        info_list = [i.strip() for i in information_needed.split(",")]
        
        summary = {
            "message_type": "request_summary",
            "summary": f"""
📊 **Compliance Information Summary**

**Standards to Query:** {len(standards_list)}
{chr(10).join([f"  • {std}" for std in standards_list])}

**Information to Retrieve:**
{chr(10).join([f"  • {info}" for info in info_list])}

**Output Format:** {output_format}

**Estimated Details:** This will provide comprehensive {', '.join(info_list)} for {len(standards_list)} compliance standard(s).

**Ready to proceed?** I'll gather this information for you.
""",
            "standards_count": len(standards_list),
            "standards": standards_list,
            "information_types": info_list,
            "output_format": output_format
        }
        
        return json.dumps(summary, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def validateComplianceParameters(
    standards: str,
    include_checklist: str = "true",
    include_penalties: str = "true",
    include_breach_info: str = "true"
) -> str:
    """
    Validate parameters before generating a compliance report and show what will be included.
    
    Use this before calling generateComplianceReport to confirm scope with the user.
    
    Args:
        standards: Comma-separated standards (e.g., "gdpr, hipaa, pci_dss")
        include_checklist: Whether to include audit checklists ("true" or "false")
        include_penalties: Whether to include penalty information ("true" or "false")
        include_breach_info: Whether to include breach notification requirements ("true" or "false")
    
    Returns:
        JSON string with validation results and what will be included
    
    Example:
        validateComplianceParameters(
            standards="gdpr, hipaa",
            include_checklist="true",
            include_penalties="true",
            include_breach_info="false"
        )
    """
    try:
        standards_list = [s.strip().lower() for s in standards.split(",")]
        valid_standards = ["gdpr", "hipaa", "pci_dss", "sox"]
        
        # Validate standards
        invalid = [s for s in standards_list if s not in valid_standards]
        
        checklist_bool = include_checklist.lower() == "true"
        penalties_bool = include_penalties.lower() == "true"
        breach_bool = include_breach_info.lower() == "true"
        
        validation = {
            "valid": len(invalid) == 0,
            "standards": {
                "requested": standards_list,
                "valid": [s for s in standards_list if s in valid_standards],
                "invalid": invalid
            },
            "report_scope": {
                "checklist_included": checklist_bool,
                "penalties_included": penalties_bool,
                "breach_notification_included": breach_bool
            },
            "preview": f"""
🔍 **Report Configuration Preview**

**Standards to Include:** {', '.join([s.upper() for s in standards_list if s in valid_standards])}

**Report Will Include:**
{'✅' if checklist_bool else '❌'} Compliance Checklists
{'✅' if penalties_bool else '❌'} Penalty Information
{'✅' if breach_bool else '❌'} Breach Notification Requirements

**Status:** {'✅ Ready to generate' if len(invalid) == 0 else f'❌ Invalid standards: {", ".join(invalid)}'}

{f'**Note:** Invalid standards will be skipped: {", ".join(invalid)}' if invalid else ''}
"""
        }
        
        if invalid:
            validation["message"] = f"Warning: These standards are not recognized: {', '.join(invalid)}"
            validation["available_standards"] = valid_standards
        
        return json.dumps(validation, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


# ==================== END COMPLIANCE CONFIRMATION TOOLS ====================


# ==================== COMPLIANCE MODULE GENERATOR TOOLS ====================
# Secure tools for AI to generate new compliance modules

@mcp.tool()
def listComplianceModules() -> str:
    """
    List all available compliance modules in the system
    
    Returns:
        JSON string with list of all compliance module files and their metadata
    
    Example:
        listComplianceModules()
    """
    try:
        result = list_compliance_modules()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def validateComplianceModule(filename: str, content: str) -> str:
    """
    Validate a compliance module WITHOUT creating the file (dry-run)
    
    ⚠️ ALWAYS CALL THIS FIRST before createComplianceModule()!
    
    This performs comprehensive security validation:
    - Validates filename and path safety (prevents path traversal)
    - Checks Python syntax
    - Scans for dangerous code (eval, exec, os.system, etc.)
    - Validates STANDARD structure
    - Checks required fields
    
    Args:
        filename: Module filename (e.g., 'sox.py', 'iso_27001.py')
                  - Only lowercase letters, numbers, and underscores allowed
                  - Automatically adds .py extension if missing
        content: Complete Python module content with STANDARD constant
                 - Must include: name, region, overview fields
                 - Should follow the same structure as existing modules
    
    Returns:
        JSON string with validation results and preview (no file created)
    
    Example:
        content = ""\"
        '''SOX Compliance Module'''
        
        STANDARD = {
            "name": "Sarbanes-Oxley Act",
            "region": "United States",
            "overview": "Financial reporting compliance",
            "key_requirements": [...]
        }
        \"""
        validateComplianceModule('sox.py', content)
    """
    try:
        result = create_compliance_module_dry_run(filename, content)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def createComplianceModule(filename: str, content: str, allow_overwrite: bool = False) -> str:
    """
    Create a new compliance module file (WRITES TO DISK)
    
    ⚠️ CRITICAL: ALWAYS call validateComplianceModule() first and review results!
    
    This creates an actual .py file in the compliance_modules/ directory.
    The file will be automatically discovered and available for compliance queries.
    
    Security Features:
    - Restricted to compliance_modules/ directory only
    - Automatic backup of existing files (if overwriting)
    - Multiple validation layers
    - Code safety scanning
    - File size limits (500KB max)
    
    Args:
        filename: Module filename (e.g., 'sox.py')
                  Must pass security validation
        content: Complete Python module content with STANDARD constant
                 Must pass syntax and structure validation
        allow_overwrite: If True, allows overwriting existing files
                         (creates backup first)
                         Default: False (prevents accidental overwrites)
    
    Returns:
        JSON string with creation status, file path, and validation results
    
    Workflow:
        1. Call validateComplianceModule() first
        2. Review validation results
        3. If valid, call createComplianceModule()
        4. Verify file was created with listComplianceModules()
    
    Example:
        # Step 1: Validate
        result = validateComplianceModule('sox.py', content)
        # Step 2: Review and confirm validation passed
        # Step 3: Create
        result = createComplianceModule('sox.py', content, False)
    """
    try:
        result = create_compliance_module(filename, content, allow_overwrite)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

# ==================== END COMPLIANCE MODULE GENERATOR TOOLS ====================

# Even better: Use FastMCP's native tool listing if available

@mcp.tool()
def listAvailableTools(context: Context, category: str = "all") -> str:
    """
    List all available MCP tools using FastMCP's native tool registry
    
    Args:
        category: Filter by category (all, gmail, calendar, salesforce, telesign, compliance)
    
    Returns:
        JSON string with all registered tools and their metadata
    """
    try:
        import inspect
        import json
        
        # FastMCP stores tools in mcp.tools or similar
        # Let's access the tool registry directly
        tools_dict = {}
        
        # Get the current module to find all decorated functions
        current_module = inspect.getmodule(inspect.currentframe())
        
        # Find all functions decorated with @mcp.tool()
        for name, obj in inspect.getmembers(current_module):
            if callable(obj) and hasattr(obj, '__name__'):
                # Check if it's a tool by looking for context parameter
                sig = None
                try:
                    sig = inspect.signature(obj)
                    params = list(sig.parameters.keys())
                    
                    # MCP tools have 'context' as first parameter
                    if params and params[0] == 'context':
                        # This is an MCP tool!
                        tool_name = obj.__name__
                        
                        # Extract metadata
                        tool_info = {
                            "name": tool_name,
                            "parameters": []
                        }
                        
                        # Get parameters (skip context)
                        for param_name, param in list(sig.parameters.items())[1:]:
                            param_info = {
                                "name": param_name,
                                "type": str(param.annotation).replace("<class '", "").replace("'>", "") if param.annotation != inspect.Parameter.empty else "Any",
                                "required": param.default == inspect.Parameter.empty
                            }
                            if param.default != inspect.Parameter.empty:
                                param_info["default"] = str(param.default)
                            tool_info["parameters"].append(param_info)
                        
                        # Extract docstring
                        docstring = inspect.getdoc(obj)
                        if docstring:
                            # Get first line as short description
                            lines = docstring.strip().split('\n')
                            tool_info["description"] = lines[0] if lines else ""
                            tool_info["full_docs"] = docstring
                        
                        # Categorize
                        name_lower = tool_name.lower()
                        if any(x in name_lower for x in ['email', 'gmail', 'draft']):
                            cat = 'gmail'
                        elif any(x in name_lower for x in ['calendar', 'event', 'attendee']):
                            cat = 'calendar'
                        elif any(x in name_lower for x in ['salesforce', 'case', 'account', 'contact', 'opportunity', 'soql', 'sosl', 'chatter', 'task']):
                            cat = 'salesforce'
                        elif any(x in name_lower for x in ['sms', 'phone', 'voice', 'verification', 'telesign', 'message', 'batch']):
                            cat = 'telesign'
                        elif any(x in name_lower for x in ['compliance', 'gdpr', 'hipaa', 'pci', 'penalty', 'breach', 'sox']):
                            cat = 'compliance'
                        else:
                            cat = 'utility'
                        
                        if cat not in tools_dict:
                            tools_dict[cat] = []
                        tools_dict[cat].append(tool_info)
                        
                except (ValueError, TypeError):
                    # Not a valid function signature
                    continue
        
        # Filter by category
        if category.lower() != "all":
            if category.lower() in tools_dict:
                tools_dict = {category.lower(): tools_dict[category.lower()]}
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Category '{category}' not found",
                    "available_categories": list(tools_dict.keys())
                }, indent=2)
        
        # Calculate totals
        total = sum(len(v) for v in tools_dict.values())
        
        return json.dumps({
            "success": True,
            "total_tools": total,
            "categories": list(tools_dict.keys()),
            "tools": tools_dict,
            "note": "Tools discovered dynamically at runtime"
        }, indent=2)
        
    except Exception as e:
        import traceback
        return json.dumps({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }, indent=2)


# ==================== COMPLIANCE PROCEDURAL GUIDANCE TOOLS ====================
# Tools for accessing step-by-step procedures, decision trees, and real-world examples

@mcp.tool()
def getGroundedSecurityGuidance(
    user_question: str,
    regulation: str = None,
    guidance_type: str = None,
) -> str:
    """
    Retrieve curated cybersecurity and compliance guidance from local source files.

    Use this tool first when the user asks for guidance, process explanations,
    decision support, or implementation examples. The result is grounded in
    curated files so the model can summarize without inventing policy details.

    Args:
        user_question: User's original question in natural language
        regulation: Optional regulation filter such as GDPR, HIPAA, CCPA, PCI-DSS, or SOX
        guidance_type: Optional hint: procedure, decision_tree, or example

    Returns:
        JSON string containing matched source metadata, response rules, and guidance content
    """
    try:
        result = guidance_catalog.get_guidance(
            user_question=user_question,
            regulation=regulation,
            guidance_type=guidance_type,
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

@mcp.tool()
def getComplianceProcedure(procedure_type: str, regulation: str = None) -> str:
    """
    Get step-by-step compliance procedures for handling data.
    
    Returns detailed, actionable procedures with regulation references,
    compliant/non-compliant examples, and implementation checklists.
    
    🎯 USE THIS WHEN: User asks "How do I...", "What's the process for...", "Steps to..."
    
    Available Procedures:
    - data_collection: How to collect user data compliantly
    - data_storage: How to store data securely  
    - data_sharing: How to share data with third parties
    - data_deletion: How to handle deletion requests
    - breach_response: How to respond to data breaches
    
    Args:
        procedure_type: Type of procedure - one of:
                       'data_collection', 'data_storage', 'data_sharing',
                       'data_deletion', 'breach_response'
        regulation: Optional filter by regulation (e.g., 'GDPR', 'CCPA', 'HIPAA')
                   If provided, highlights requirements for that specific regulation
    
    Returns:
        JSON string with step-by-step procedure including:
        - Title and description
        - Applicable regulations
        - Detailed steps with actions
        - Regulation references for each step
        - Compliant vs non-compliant examples
        - Implementation checklists
    
    Example:
        getComplianceProcedure('data_deletion')
        getComplianceProcedure('data_collection', 'GDPR')
    """
    try:
        procedures = guidance_catalog.store.get_procedures()
        valid_procedures = list(procedures.keys())
        if procedure_type not in valid_procedures:
            return json.dumps({
                "success": False,
                "error": f"Invalid procedure_type. Must be one of: {', '.join(valid_procedures)}",
                "available_procedures": valid_procedures
            }, indent=2)
        
        # Get the procedure
        procedure = procedures[procedure_type]
        
        # If regulation filter is provided, add note
        result = {
            "success": True,
            "procedure_type": procedure_type,
            "procedure": procedure
        }
        
        if regulation:
            result["regulation_filter"] = regulation.upper()
            result["note"] = f"Showing procedure with focus on {regulation.upper()} requirements. All regulations are listed, but {regulation.upper()} is highlighted."
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def getComplianceDecisionTree(scenario: str) -> str:
    """
    Get an interactive decision tree flowchart for making compliance decisions.
    
    Returns a tree structure with yes/no decision points that guide users
    to the correct action. Perfect for real-time decision-making.
    
    🎯 USE THIS WHEN: User asks "Can I...", "Should I...", "Is it ok to..."
    
    Available Decision Trees:
    - email_compliance: "Can I email customer data to this vendor?"
    - data_sharing: "Should I share data with this third party?"
    - data_deletion: "How do I handle this deletion request?"
    - vendor_access: "Should I give this vendor access to our systems?"
    
    Args:
        scenario: Decision tree scenario - one of:
                 'email_compliance', 'data_sharing', 'data_deletion', 'vendor_access'
    
    Returns:
        JSON string with interactive decision tree including:
        - Tree title and description
        - Start node to begin decision process
        - Decision nodes with questions and guidance
        - Possible actions with required steps
        - Quick reference for common scenarios
    
    How to Use the Tree:
        1. Start at the start_node
        2. Answer the question at each node
        3. Follow 'next_node' based on answer  
        4. When you reach an action, follow the steps provided
    
    Example:
        getComplianceDecisionTree('email_compliance')
        # Returns tree with nodes: check requester identity → check authorization → 
        # check data minimization → actions (approve, deny, report phishing, etc.)
    """
    try:
        trees = guidance_catalog.store.get_decision_trees()

        if scenario not in LEGACY_DECISION_TREE_MAP:
            return json.dumps({
                "success": False,
                "error": f"Invalid scenario. Must be one of: {', '.join(LEGACY_DECISION_TREE_MAP.keys())}",
                "available_scenarios": list(LEGACY_DECISION_TREE_MAP.keys())
            }, indent=2)
        
        tree_key = LEGACY_DECISION_TREE_MAP[scenario]
        
        if tree_key not in trees:
            return json.dumps({
                "success": False,
                "error": f"Decision tree '{tree_key}' not found in file"
            }, indent=2)
        
        tree = trees[tree_key]
        
        result = {
            "success": True,
            "scenario": scenario,
            "decision_tree": tree,
            "usage_instructions": {
                "step_1": "Start at the node indicated by 'start_node'",
                "step_2": "Read the question and guidance at each node",
                "step_3": "Based on your situation, follow the appropriate 'next_node' path",
                "step_4": "When you reach an action (no next_node), follow the steps provided",
                "tip": "Use the quick_reference if available for instant answers to common questions"
            }
        }
        
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


@mcp.tool()
def getComplianceExamples(topic: str, show_non_compliant: bool = True) -> str:
    """
    Get real-world examples of compliant vs non-compliant actions.
    
    Returns concrete scenarios with code examples, explanations, and consequences.
    Perfect for training, learning, and understanding what to do (and what NOT to do).
    
    🎯 USE THIS WHEN: User asks "Can you give me an example of...", "Show me how to...",
                      "What's the right way to..."
    
    Available Topics:
    - email_scenarios: Handling customer data requests, marketing emails, vendor requests
    - technical_scenarios: Password storage, logging, API auth, database encryption  
    - process_scenarios: Employee onboarding/termination, consent management
    - data_breach_scenarios: Discovering and responding to breaches
    
    Args:
        topic: Example topic - one of:
              'email_scenarios', 'technical_scenarios', 'process_scenarios', 
              'data_breach_scenarios'
        show_non_compliant: If True (default), includes non-compliant examples
                           If False, shows only compliant examples
                           (Showing both helps users understand contrast)
    
    Returns:
        JSON string with array of scenarios, each including:
        - Scenario description and situation
        - Applicable regulations (GDPR, CCPA, HIPAA, etc.)
        - Compliant response with steps, code examples, and explanation
        - Non-compliant response with examples and consequences (if show_non_compliant=True)
    
    Example:
        getComplianceExamples('technical_scenarios')
        # Returns examples: password hashing (bcrypt vs plaintext),
        # logging (user IDs vs PII), API auth (JWT vs no auth)
        
        getComplianceExamples('email_scenarios', False)
        # Returns only compliant examples without non-compliant counterparts
    """
    try:
        # Validate topic
        examples_by_topic = guidance_catalog.store.get_examples()
        valid_topics = list(examples_by_topic.keys())
        if topic not in valid_topics:
            return json.dumps({
                "success": False,
                "error": f"Invalid topic. Must be one of: {', '.join(valid_topics)}",
                "available_topics": valid_topics
            }, indent=2)
        
        # Get examples for the topic
        examples = examples_by_topic[topic]
        
        # Optionally filter out non-compliant examples
        if not show_non_compliant:
            filtered_examples = []
            for example in examples:
                filtered_example = example.copy()
                if 'non_compliant' in filtered_example or 'non_compliant_response' in filtered_example:
                    # Remove non-compliant parts
                    filtered_example.pop('non_compliant', None)
                    filtered_example.pop('non_compliant_response', None)
                    filtered_example['note'] = "Non-compliant examples hidden (show_non_compliant=False)"
                filtered_examples.append(filtered_example)
            examples = filtered_examples
        
        result = {
            "success": True,
            "topic": topic,
            "examples_count": len(examples),
            "showing_non_compliant": show_non_compliant,
            "examples": examples,
            "usage_tip": "Study both compliant and non-compliant examples to understand the contrast. Code examples are provided where applicable."
        }
        
        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)

# ==================== END COMPLIANCE PROCEDURAL GUIDANCE TOOLS ====================
