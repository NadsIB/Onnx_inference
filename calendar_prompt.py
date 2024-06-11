import os.path
import parsedatetime
import pendulum
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define the required Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.readonly']
prompt = "Are you available at 3pm today?"


def authenticate():
    """Authenticate and return a Google Calendar service object."""
    creds = None
    # Check if token.json file exists
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None

def extract_time_from_prompt(prompt):
    """Extract date and time from the given prompt using parsedatetime."""
    cal = parsedatetime.Calendar()
    time_struct, _ = cal.parse(prompt)
    dt = pendulum.datetime(*time_struct[:6])
    print(f"Extracted DateTime: {dt}")  # Debug statement
    return dt

def convert_to_local_time(dt):
    """Convert the extracted UTC time to local time zone."""
    local_tz = pendulum.local_timezone()
    local_time = dt.in_tz(local_tz)
    print(f"Local DateTime: {local_time}")  # Debug statement
    return local_time

def extract_event_details(service, start_time, end_time):
    """Retrieve events from the Google Calendar within the specified time range."""
    events_result = service.events().list(
        calendarId='primary', timeMin=start_time.isoformat(), timeMax=end_time.isoformat(),
        singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def generate_response(prompt, events):
    """Generate responses based on the calendar events."""
    if not events:
        return ["Yes, I'm available at that time."]

    event = events[0]
    event_summary = event['summary']
    responses = [
        f"No, I'm not available. I have {event_summary}.",
        f"I have {event_summary} scheduled on my calendar. But, I can skip it."
    ]
    return responses

def calendar_chat_response(prompt):
    """Main function to authenticate, check calendar, and generate responses."""
    service = authenticate()
    if not service:
        print("Failed to authenticate Google Calendar.")
        return

    time_to_check1 = extract_time_from_prompt(prompt)
    time_to_check = convert_to_local_time(time_to_check1)
    start_time = time_to_check
    end_time = time_to_check.add(hours=1)

    events = extract_event_details(service, start_time, end_time)
    responses = generate_response(prompt, events)

    for response in responses:
        print(response)

calendar_chat_response(prompt)

