from datetime import datetime
import logging
from google_sheets_operations import get_google_sheets_service,fetch_google_sheets_records,update_google_sheets
from mysql_operations import fetch_mysql_records, update_mysql
from sync import compare_and_sync_records
from utils import load_last_update_time, save_last_update_time
import sys
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account

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

# File to store the last check time
LAST_UPDATE_FILE = 'last_check.txt'

def main():
    last_update_time = load_last_update_time()
    mysql_records = fetch_mysql_records(last_update_time)
    google_records = fetch_google_sheets_records(service, SPREADSHEET_ID)
    to_update_mysql, to_update_google = compare_and_sync_records(mysql_records, google_records, last_update_time)

    if to_update_mysql:
        logging.info(f"Updating MySQL with {len(to_update_mysql)} records from Google Sheets.")
        update_mysql(to_update_mysql)

    if to_update_google:
        logging.info(f"Updating Google Sheets with {len(to_update_google)} records from MySQL.")
        update_google_sheets(service, SPREADSHEET_ID, to_update_google)

    save_last_update_time('last_check.txt', datetime.now())
    logging.info("Sync completed successfully.")

if __name__ == '__main__':
    main()
