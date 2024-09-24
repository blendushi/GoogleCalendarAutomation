from flask import Flask, render_template, redirect, request, url_for, jsonify
import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Flask app setup
app = Flask(__name__)

# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar']
YOUR_CALENDAR_ID = ''
YOUR_TIMEZONE = ''

# Global session start time
START_TIME = None

def get_google_credentials():
    """Retrieve or generate credentials for Google Calendar API."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def add_event_to_google_calendar(description, start_time, end_time):
    """Add event to Google Calendar."""
    creds = get_google_credentials()
    service = build('calendar', 'v3', credentials=creds)
    
    # Convert to RFC3339 format (with 'Z' indicating UTC)
    start_formatted = start_time.isoformat() + 'Z'
    end_formatted = end_time.isoformat() + 'Z'

    event = {
        'summary': description,
        'start': {
            'dateTime': start_formatted,
            'timeZone': YOUR_TIMEZONE,
        },
        'end': {
            'dateTime': end_formatted,
            'timeZone': YOUR_TIMEZONE,
        },
    }

    event = service.events().insert(calendarId=YOUR_CALENDAR_ID, body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

@app.route('/')
def index():
    """Render the main page with session control buttons."""
    global START_TIME
    if START_TIME is None:
        elapsed = None
    else:
        elapsed = (datetime.datetime.utcnow() - START_TIME).total_seconds()
    return render_template('index.html', elapsed=elapsed)

@app.route('/start', methods=['POST'])
def start_session():
    """Start a coding session."""
    global START_TIME
    START_TIME = datetime.datetime.utcnow()
    print(f"Session started at {START_TIME}")
    return redirect(url_for('index'))

@app.route('/end', methods=['POST'])
def end_session():
    """End the coding session and log it to Google Calendar."""
    global START_TIME
    if START_TIME is None:
        return "Error: No session has been started."

    end_time = datetime.datetime.utcnow()
    duration = end_time - START_TIME
    print(f"Session ended at {end_time}. Duration: {duration}.")

    description = request.form.get('description', 'Coding Session')
    add_event_to_google_calendar(description, START_TIME, end_time)
    
    START_TIME = None  # Reset start time for the next session
    return redirect(url_for('index'))

@app.route('/elapsed_time', methods= ['GET'])
def get_elapsed_time():
    # return the elapsed time since the start of the session in seconds 
    global START_TIME
    if START_TIME is None:
        return jsonify({"elapsed": None})
    
    elapsed_seconds = (datetime.datetime.utcnow() - START_TIME).total_seconds()
    return jsonify({"elapsed": elapsed_seconds})

if __name__ == "__main__":
    app.run(debug=True)
