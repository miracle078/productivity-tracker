from pynput import keyboard, mouse
import requests
import sqlite3
import time
from datetime import datetime

# Configuration
AWS_ENDPOINT = "http://13.56.59.39/api/activity"  # Replace with your server's URL
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
    print(f"Logging event: {event_type} at {timestamp}")
    # Create a new connection for this thread
    conn = sqlite3.connect(LOCAL_DB)
    cursor = conn.cursor()

    # Save the activity
    cursor.execute("INSERT INTO activity_log (timestamp, event_type) VALUES (?, ?)", (timestamp, event_type))
    conn.commit()

    # Close the connection
    conn.close()

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
from pynput import keyboard, mouse
import requests
import sqlite3
import time
import logging
from datetime import datetime

# Configuration
AWS_ENDPOINT = "http://13.56.59.39/api/activity"
LOG_INTERVAL = 60  # Sync data every 60 seconds

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Local database setup
LOCAL_DB = 'local_activity_log.db'
local_conn = sqlite3.connect(LOCAL_DB, check_same_thread=False)
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

def save_to_local_db(event_type):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info("Logging event: %s at %s", event_type, timestamp)
    conn = sqlite3.connect(LOCAL_DB)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO activity_log (timestamp, event_type) VALUES (?, ?)", (timestamp, event_type))
    conn.commit()
    conn.close()

def sync_local_data(batch_size=50):
    local_cursor.execute("SELECT * FROM activity_log")
    rows = local_cursor.fetchall()
    if rows:
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            data_to_send = [{'timestamp': row[1], 'event_type': row[2]} for row in batch if row[2]]
            try:
                response = requests.post(AWS_ENDPOINT, json=data_to_send, timeout=10)
                if response.status_code == 200:
                    synced_ids = [row[0] for row in batch]
                    placeholders = ', '.join('?' for _ in synced_ids)
                    local_cursor.execute(f"DELETE FROM activity_log WHERE id IN ({placeholders})", synced_ids)
                    local_conn.commit()
                    logging.info(f"Synced {len(batch)} offline events to AWS")
                else:
                    logging.warning(f"Failed to sync batch data: {response.status_code}, {response.text}")
            except Exception as e:
                logging.error(f"Error syncing batch data: {e}")


def log_activity(event_type):
    save_to_local_db(event_type)

keyboard_listener = keyboard.Listener(on_press=lambda _: log_activity('keyboard'))
mouse_listener = mouse.Listener(on_click=lambda x, y, button, pressed: log_activity('mouse' if pressed else None))

keyboard_listener.start()
mouse_listener.start()

try:
    while True:
        time.sleep(LOG_INTERVAL)
        sync_local_data()
except KeyboardInterrupt:
    logging.info("Monitoring stopped.")
