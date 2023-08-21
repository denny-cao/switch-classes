import os
import datetime as dt
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import dotenv_values
from pathlib import Path
import pytz

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

DIR_PATH = os.path.dirname(os.path.abspath(__file__))

def get_calendar_id():
    '''Return Calendar ID of classes'''

    if not os.path.isfile(os.path.join(DIR_PATH, '.env')):
        print("No '.env' file found. Attempting to get variables from environment.")

        return os.environ["CALENDAR_ID"]
    else:
        config = dotenv_values(os.path.join(DIR_PATH, '.env'))

        return config.get("CALENDAR_ID")

def get_creds_calendar():
    '''Return credentials for Google Calendar API'''

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(os.path.join(DIR_PATH, 'token.json')):
        creds = Credentials.from_authorized_user_file(os.path.join(DIR_PATH, 'token.json'), SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.path.join(DIR_PATH, 'credentials.json'), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(os.path.join(DIR_PATH, 'token.json'), 'w') as token:
            token.write(creds.to_json())
    return creds

def get_current_time_utc():
    '''Return current time in UTC Timezone Aware'''

    return dt.datetime.now(pytz.utc)

def is_ongoing(event):
    '''Return if a given event is currently taking place'''

    now_datetime = get_current_time_utc()

    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))
    start_utc = dt.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z').astimezone(pytz.utc)
    end_utc = dt.datetime.strptime(end, '%Y-%m-%dT%H:%M:%S%z').astimezone(pytz.utc)

    return True if (start_utc <= now_datetime and end_utc > now_datetime) else False

def is_future(event):
    '''Return if a given event has not occurred yet'''

    now_datetime = get_current_time_utc()

    start = event['start'].get('dateTime', event['start'].get('date'))
    start_utc = dt.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z').astimezone(pytz.utc)

    return True if (start_utc > now_datetime) else False

def switch_link(class_name):
    '''Check if class path variable exists and if it does, changes link to that path'''

    CURRENT_COURSE_LINK = None
    class_path = None

    if not os.path.isfile(os.path.join(DIR_PATH, '.env')):
        print("No '.env' file found. Attempting to get variables from environment.")

        class_path = os.environ[class_name] or None
        CURRENT_COURSE_LINK = os.environ['CURRENT_COURSE_LINK'] or None
    else:
        config = dotenv_values(os.path.join(DIR_PATH, '.env'))

        class_path = config.get(class_name) or None
        CURRENT_COURSE_LINK = config.get('CURRENT_COURSE_LINK') or None

    if class_path and CURRENT_COURSE_LINK:
        if not os.path.exists(os.path.expanduser(CURRENT_COURSE_LINK)):
            os.symlink(os.path.expanduser(class_path), os.path.expanduser(CURRENT_COURSE_LINK))
            print(f"Created Symbolic Link to {class_name}")

        elif class_path != os.readlink(os.path.expanduser(CURRENT_COURSE_LINK)):
            os.unlink(os.path.expanduser(CURRENT_COURSE_LINK))
            os.symlink(os.path.expanduser(class_path), os.path.expanduser(CURRENT_COURSE_LINK))
            print(f"Switched current-class to {class_name}")
    else:
        print("Class Path or Current Course Link does not exist!")

def main():
    CALENDAR_ID = get_calendar_id()
    CREDS = get_creds_calendar()

    try:
        service = build('calendar', 'v3', credentials=CREDS)

        now = dt.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        # Call the Calendar API
        events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=now, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        for event in events:
            if is_ongoing(event):
                switch_link(event['description'])
                return
            elif is_future(event):
                print(f"No classes ongoing...")
                return

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
