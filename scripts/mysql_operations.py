import mysql.connector
import logging
from datetime import datetime, date
import sys
import os
# Configure logging
logging.basicConfig(filename='sync.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MYSQL_CONFIG

def fetch_mysql_records(last_update_time):
    """Fetch all MySQL records updated after the last update time and format date fields."""
    try:
        db = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM employees"
        cursor.execute(query)
        records = cursor.fetchall()
        
        # Format date fields
        formatted_records = []
        for row in records:
            formatted_row = {}
            for key, value in row.items():
                if key == 'EmployeeID':
                    formatted_row[key] = str(value)
                elif isinstance(value, datetime):
                    formatted_row[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, date):
                    formatted_row[key] = value.strftime('%Y-%m-%d')
                else:
                    formatted_row[key] = value
            formatted_records.append(formatted_row)
        
        cursor.close()
        db.close()
        logging.info(f"Fetched and formatted {len(records)} records from MySQL.")
        return formatted_records
    except mysql.connector.Error as err:
        logging.error(f"Error fetching records from MySQL: {err}")
        return []
    
def update_mysql(records):
    """Update existing records or insert new ones into MySQL."""
    try:
        db = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = db.cursor()

        for record in records:
            check_query = "SELECT COUNT(*) FROM employees WHERE EmployeeID = %s"
            cursor.execute(check_query, (record['EmployeeID'],))
            exists = cursor.fetchone()[0]

            if exists:
                update_query = """
                UPDATE employees 
                SET FirstName = %s, LastName = %s, Email = %s, PhoneNumber = %s,
                    Department = %s, Role = %s, Status = %s, StartDate = %s, EndDate = %s,
                    last_updated = %s
                WHERE EmployeeID = %s
                """
                cursor.execute(update_query, (
                    record['FirstName'],
                    record['LastName'],
                    record['Email'],
                    record['PhoneNumber'] if record.get('PhoneNumber') else None,
                    record['Department'] if record.get('Department') else None,
                    record['Role'] if record.get('Role') else None,
                    record['Status'],
                    record['StartDate'] if record.get('StartDate') else None,
                    record['EndDate'] if record.get('EndDate') else None,
                    record['last_updated'],
                    record['EmployeeID']
                ))
                logging.info(f"Updated record for EmployeeID {record['EmployeeID']}.")
            else:
                insert_query = """
                INSERT INTO employees (EmployeeID,FirstName, LastName, Email, PhoneNumber, Department, Role, Status, StartDate, EndDate, last_updated)
                VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    record['EmployeeID'],
                    record['FirstName'],
                    record['LastName'],
                    record['Email'],
                    record['PhoneNumber'] if record.get('PhoneNumber') else None,
                    record['Department'] if record.get('Department') else None,
                    record['Role'] if record.get('Role') else None,
                    record['Status'],
                    record['StartDate'] if record.get('StartDate') else None,
                    record['EndDate'] if record.get('EndDate') else None,
                    record['last_updated']
                ))
                logging.info(f"Inserted new record for EmployeeID {record['EmployeeID']}.")
        db.commit()
        cursor.close()
        db.close()
        logging.info(f"Processed {len(records)} records in MySQL.")
    except mysql.connector.Error as err:
        logging.error(f"Error updating MySQL: {err}")
