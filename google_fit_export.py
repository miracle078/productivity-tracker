import os
from datetime import datetime, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pandas as pd

# Define the Google Fit API scopes
SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']

# Map data sources to categories
DATA_SOURCE_CATEGORIES = {
    'merge_active_minutes': 'Active Minutes',
    'merge_activity_segments': 'Activity Segments',
    'merge_calories_expended': 'Calories Expended',
    'merge_heart_minutes': 'Heart Minutes',
    'estimated_steps': 'Steps',
    'merge_step_deltas': 'Steps'
}

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

    daily_aggregates = {}
    step_time_ranges = set()  # To track unique step entries by time ranges

    for source in data_sources.get('dataSource', []):
        source_name = source['dataStreamId']
        category = DATA_SOURCE_CATEGORIES.get(source_name.split(':')[-1], source_name)

        print(f"Processing Data Source: {source_name} ({source.get('dataStreamName', 'Unnamed Source')})")
        dataset = service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=source['dataStreamId'],
            datasetId=dataset_id
        ).execute()

        for point in dataset.get('point', []):
            start_time = int(point['startTimeNanos'])
            end_time = int(point['endTimeNanos'])
            start_date_time = datetime.fromtimestamp(start_time / 1e9, tz=timezone.utc).date()

            data_values = [value.get('intVal') or value.get('fpVal') for value in point['value']]

            if start_date_time not in daily_aggregates:
                daily_aggregates[start_date_time] = {
                    'Steps': 0,
                    'Active Minutes': 0,
                    'Calories Expended': 0,
                    'Heart Minutes': 0,
                    'Activity Segments': 0
                }

            # Deduplicate steps using time ranges
            if category == 'Steps':
                time_range = (start_time, end_time)
                if time_range not in step_time_ranges:
                    daily_aggregates[start_date_time]['Steps'] += sum(value for value in data_values if isinstance(value, int))
                    step_time_ranges.add(time_range)
            elif category in daily_aggregates[start_date_time]:
                daily_aggregates[start_date_time][category] += sum(value for value in data_values if isinstance(value, (int, float)))

    # Print and format daily aggregates
    for day, aggregates in sorted(daily_aggregates.items()):
        print(f"Date: {day}")
        for category, value in aggregates.items():
            print(f"  {category}: {value}")

    return daily_aggregates

def save_to_csv(data):
    """Save the aggregated data to a CSV file."""
    rows = []
    for day, aggregates in sorted(data.items()):
        row = {'Date': day}
        row.update(aggregates)
        rows.append(row)

    df = pd.DataFrame(rows)
    if df.empty:
        print("No data available to save.")
        return

    # Ensure columns are unique by removing redundant source names
    df = df.loc[:, ~df.columns.duplicated()]
    df.to_csv('google_fit_all_data.csv', index=False)
    print("Data saved to google_fit_all_data.csv")

def main():
    # Authenticate and build the service
    creds = authenticate_google_fit()
    service = build('fitness', 'v1', credentials=creds)

    # Fetch the health activity data
    aggregated_data = fetch_google_fit_data(service)
    save_to_csv(aggregated_data)

if __name__ == '__main__':
    main()
