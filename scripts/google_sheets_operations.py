from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
from datetime import datetime,date
import logging

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials/credentials.json'

def get_google_sheets_service():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)



def fetch_google_sheets_records(service, spreadsheet_id):
    """Fetch all Google Sheets records."""
    try:
        sheet_range = 'Sheet1!A1:Z'  # Fetch the entire data range
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_range).execute()
        rows = result.get('values', [])
        
        if not rows:
            logging.info("No records found in Google Sheets.")
            return []

        # Extract headers from the first row
        headers = rows[0]

        records = []
        for row in rows[1:]:
            # Ensure that the row matches the length of headers
            if len(row) != len(headers):
                logging.warning(f"Row length {len(row)} does not match header length {len(headers)}. Skipping row.")
                continue

            # Create a dictionary for each record
            record = dict(zip(headers, row))

            # Normalize 'last_updated' format if present
            if 'last_updated' in record and record['last_updated']:
                last_updated_str = record['last_updated']
                try:
                    # If 'last_updated' is already in the desired format, keep it
                    if isinstance(last_updated_str, str):
                        # Try parsing if it's in the expected format
                        try:
                            record['last_updated'] = datetime.strptime(last_updated_str, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            # Handle cases where the format might be different
                            record['last_updated'] = None
                    elif isinstance(last_updated_str, datetime):
                        record['last_updated'] = last_updated_str.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError as e:
                    logging.error(f"Error parsing 'last_updated' field: {last_updated_str}. Error: {e}")
                    record['last_updated'] = None

            # Normalize other fields if necessary (e.g., handling empty strings)
            for key in list(record.keys()):
                if record[key] == '':
                    record[key] = None  # Or appropriate default value

            records.append(record)

        logging.info(f"Fetched {len(records)} records from Google Sheets.")
        return records
    except Exception as e:
        logging.error(f"Error fetching records from Google Sheets: {e}")
        return []








def update_google_sheets(service, spreadsheet_id, records):
    """Update or insert records into Google Sheets based on EmployeeID and last_updated."""
    try:
        # Retrieve current data from Google Sheets
        sheet_range = 'Sheet1!A2:K'  # Adjust range to fit your data (A to K for 11 columns)
        current_sheet_data = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_range
        ).execute().get('values', [])

        # Convert the current sheet data into a dictionary using EmployeeID as the key
        google_sheet_dict = {}
        for idx, row in enumerate(current_sheet_data):
            if row:
                employee_id = row[0]  # Assuming EmployeeID is the first column
                google_sheet_dict[employee_id] = idx + 2  # Store the row index (+2 because data starts from row 2)

        # Lists to hold rows for update and new records
        rows_to_update = []
        new_records = []

        for record in records:
            employee_id = str(record['EmployeeID'])  # Ensure EmployeeID is treated as string for comparison
            last_updated_mysql = record['last_updated']

            # Convert MySQL last_updated to datetime
            if isinstance(last_updated_mysql, str):
                try:
                    last_updated_mysql = datetime.strptime(last_updated_mysql, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    logging.error(f"Error parsing MySQL timestamp: {last_updated_mysql}")
                    continue

            if employee_id in google_sheet_dict:
                # If record exists in Google Sheets, compare last_updated values
                row_index = google_sheet_dict[employee_id]
                last_updated_google_sheets = current_sheet_data[row_index - 2][10]  # Adjust index for row

                try:
                    # Convert Google Sheets timestamp to a comparable format
                    last_updated_google_sheets = datetime.strptime(last_updated_google_sheets, '%Y-%m-%d %H:%M:%S')
                except (ValueError, IndexError):
                    logging.error(f"Error parsing Google Sheets timestamp: {last_updated_google_sheets}")
                    continue

                # Check if MySQL has more recent updates
                if last_updated_mysql > last_updated_google_sheets:
                    rows_to_update.append({
                        'range': f'Sheet1!A{row_index}:K{row_index}',
                        'values': [list(record.values())]
                    })
            else:
                # If the record doesn't exist in Google Sheets, add it to new records
                new_records.append(list(record.values()))

        # Update existing records
        for update in rows_to_update:
            body = {
                'values': update['values']
            }
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=update['range'],
                valueInputOption='RAW',
                body=body
            ).execute()

        # Append new records if there are any
        if new_records:
            append_range = f'Sheet1!A{len(current_sheet_data) + 2}:K'  # Append to the next available row
            body = {
                'values': new_records
            }
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=append_range,
                valueInputOption='RAW',
                body=body
            ).execute()

        logging.info(f"Updated {len(rows_to_update)} existing records and appended {len(new_records)} new records in Google Sheets.")
    except Exception as e:
        logging.error(f"Error updating Google Sheets: {e}")

