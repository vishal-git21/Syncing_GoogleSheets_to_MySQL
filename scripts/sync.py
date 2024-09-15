from sheets import get_sheets_service, fetch_data_from_mysql, update_google_sheet

def main():
    # Google Sheets service
    service = get_sheets_service()
    
    # Google Sheet ID
    spreadsheet_id = '1EKOj2iuRA3j7s4BrPe2t9CDMrchjjrv1URTK5DxiQlI'
    
    # Fetch data from MySQL
    mysql_data = fetch_data_from_mysql()
    
    # Update Google Sheets with MySQL data
    update_google_sheet(service, spreadsheet_id, mysql_data)

if __name__ == '__main__':
    main()
