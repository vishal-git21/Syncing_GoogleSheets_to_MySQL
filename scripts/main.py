import mysql.connector
from googleapiclient.discovery import build
from google.oauth2 import service_account
import time
from datetime import datetime,date
import sys
import os
import logging

# Configure logging
logging.basicConfig(filename='sync.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MYSQL_CONFIG

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials/credentials.json'
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

SPREADSHEET_ID = '1EKOj2iuRA3j7s4BrPe2t9CDMrchjjrv1URTK5DxiQlI'

# Define the last updated time (initially set to January 1, 2020)
last_update_time = datetime(2020, 1, 1)


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

def add_or_update_record_in_sheet(service, spreadsheet_id, records):
    if records:
        try:
            update_google_sheet(service, spreadsheet_id, records)
        except Exception as e:
            logging.error(f"Error updating Google Sheets: {e}")

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
    global last_update_time
    while True:
        records = fetch_updated_records(last_update_time)
        if records:
            add_or_update_record_in_sheet(service, SPREADSHEET_ID, records)
            last_update_time = datetime.now()  # Update the last update time
        time.sleep(60)  # Check every 60 seconds

if __name__ == "__main__":
    main()




