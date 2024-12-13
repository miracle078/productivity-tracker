from pynput import keyboard, mouse
import requests
import sqlite3
import time
from datetime import datetime

# Configuration
AWS_ENDPOINT = "http://your-aws-server/api/activity"  # Replace with your server's URL
LOG_INTERVAL = 60  # Sync data every 60 seconds

# Local database setup
LOCAL_DB = 'local_activity_log.db'
local_conn = sqlite3.connect(LOCAL_DB)
local_cursor = local_conn.cursor()

# Create table to store offline activity logs
local_cursor.execute('''
    CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        event_type TEXT
    )
''')
local_conn.commit()

# Save activity locally
def save_to_local_db(event_type):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    local_cursor.execute("INSERT INTO activity_log (timestamp, event_type) VALUES (?, ?)", (timestamp, event_type))
    local_conn.commit()

# Sync local data to AWS
def sync_local_data():
    local_cursor.execute("SELECT * FROM activity_log")
    rows = local_cursor.fetchall()
    if rows:
        data_to_send = [{'timestamp': row[1], 'event_type': row[2]} for row in rows]
        try:
            response = requests.post(AWS_ENDPOINT, json=data_to_send)
            if response.status_code == 200:
                print(f"Synced {len(rows)} offline events to AWS")
                local_cursor.execute("DELETE FROM activity_log")
                local_conn.commit()
            else:
                print(f"Failed to sync data: {response.status_code}")
        except Exception as e:
            print(f"Error syncing data: {e}")

# Log activity
def log_activity(event_type):
    save_to_local_db(event_type)

# Keyboard and mouse listeners
keyboard_listener = keyboard.Listener(on_press=lambda _: log_activity('keyboard'))
mouse_listener = mouse.Listener(on_click=lambda x, y, button, pressed: log_activity('mouse' if pressed else None))

keyboard_listener.start()
mouse_listener.start()

# Periodic data sync
try:
    while True:
        time.sleep(LOG_INTERVAL)
        sync_local_data()
except KeyboardInterrupt:
    print("Monitoring stopped.")
