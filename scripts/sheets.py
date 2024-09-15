import mysql.connector
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import date, datetime
import sys
import os
# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MYSQL_CONFIG

def get_sheets_service():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'credentials/credentials.json'
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=credentials)
    return service

def fetch_data_from_mysql():
    # MySQL connection
    db = mysql.connector.connect(**MYSQL_CONFIG)  # Using config.py details
    
    cursor = db.cursor(dictionary=True)
    
    # Query to fetch all data from employees table
    query = "SELECT * FROM employees"
    cursor.execute(query)
    
    result = cursor.fetchall()
    
    # Convert any date or datetime objects to strings
    for row in result:
        for key, value in row.items():
            if isinstance(value, (date, datetime)):
                row[key] = value.strftime('%Y-%m-%d')  # Convert to string format
    
    cursor.close()
    db.close()
    
    return result

def update_google_sheet(service, spreadsheet_id, data):
    sheet_range = 'Sheet1!A2'  # Starting from A2, assuming A1 has headers
    
    values = [list(item.values()) for item in data]  # Convert data to list of lists
    body = {
        'values': values
    }
    
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=sheet_range,
        valueInputOption='RAW',
        body=body
    ).execute()
    
    print(f"{result.get('updatedCells')} cells updated.")
