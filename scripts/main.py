import mysql.connector
from googleapiclient.discovery import build
from google.oauth2 import service_account
import time
from datetime import datetime, date
import os
import logging
import json

# Configure logging
logging.basicConfig(filename='sync.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the parent directory to sys.path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MYSQL_CONFIG

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials/credentials.json'
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)
SPREADSHEET_ID = '1EKOj2iuRA3j7s4BrPe2t9CDMrchjjrv1URTK5DxiQlI'

# File to store the last check time
LAST_UPDATE_FILE = 'last_check.txt'

def load_last_update_time():
    if os.path.exists(LAST_UPDATE_FILE):
        with open(LAST_UPDATE_FILE, 'r') as f:
            last_update_time_str = f.read().strip()
            return datetime.fromisoformat(last_update_time_str)
    else:
        return datetime(2020, 1, 1)  # Default to a past date if file does not exist

def save_last_update_time(last_update_time):
    with open(LAST_UPDATE_FILE, 'w') as f:
        f.write(last_update_time.isoformat())

def fetch_updated_records(last_update_time):
    try:
        db = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT * FROM employees
        WHERE last_updated > %s
        """
        cursor.execute(query, (last_update_time,))
        records = cursor.fetchall()
        for row in records:
            for key, value in row.items():
                if isinstance(value, (date, datetime)):
                    row[key] = value.strftime('%Y-%m-%d') 
        cursor.close()
        db.close()
        logging.info(f"Fetched {len(records)} records.")
        return records
    except mysql.connector.Error as err:
        logging.error(f"Error fetching records: {err}")
        return []

def update_google_sheet(service, spreadsheet_id, data):
    sheet_range = 'Sheet1!A2'  # Starting from A2, assuming A1 has headers
    values = [list(item.values()) for item in data]  # Convert data to list of lists
    body = {
        'values': values
    }
    try:
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
            valueInputOption='RAW',
            body=body
        ).execute()
        logging.info(f"{result.get('updatedCells')} cells updated.")
    except Exception as e:
        logging.error(f"Error updating Google Sheets: {e}")

def main():
    last_update_time = load_last_update_time()
    records = fetch_updated_records(last_update_time)
    if records:
        update_google_sheet(service, SPREADSHEET_ID, records)
    last_update_time = datetime.now()  # Update the last update time
    save_last_update_time(last_update_time)
    logging.info("Script run completed.")

if __name__ == "__main__":
    main()

