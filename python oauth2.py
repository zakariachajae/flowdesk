from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
import os

# Scopes required for the Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_credentials():
    """Load credentials from file and refresh if needed."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)  # Ensure this port matches your registered URI
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def create_google_meet_event(creds, summary, description, start_time, end_time, attendees_emails):
    from googleapiclient.discovery import build
    service = build('calendar', 'v3', credentials=creds)

    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'America/Los_Angeles',
        },
        'conferenceData': {
            'createRequest': {
                'requestId': 'sample123',
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet'
                },
                'status': {
                    'statusCode': 'success'
                }
            }
        },
        'attendees': [{'email': email} for email in attendees_emails],
        'reminders': {
            'useDefault': True,
        },
    }

    event = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1,
        fields='id,hangoutLink'
    ).execute()

    print('Event created:', event.get('htmlLink'))
    print('Google Meet Link:', event.get('hangoutLink'))

if __name__ == '__main__':
    creds = get_credentials()
    create_google_meet_event(
        creds,
        summary='Meeting Title',
        description='Meeting Description',
        start_time='2024-10-01T10:00:00-07:00',
        end_time='2024-10-01T11:00:00-07:00',
        attendees_emails=['example@example.com']
    )
