from datetime import datetime

def compare_and_sync_records(mysql_records, google_records, last_check_time):
    """Compare records and update based on the latest timestamp and last_check time."""
    if last_check_time.tzinfo is not None:
        last_check_time = last_check_time.replace(tzinfo=None)

    mysql_dict = {r['EmployeeID']: r for r in mysql_records}
    google_dict = {r['EmployeeID']: r for r in google_records}

    to_update_mysql = []
    to_update_google = []

    all_employee_ids = set(mysql_dict.keys()).union(set(google_dict.keys()))

    for emp_id in all_employee_ids:
        mysql_record = mysql_dict.get(emp_id)
        google_record = google_dict.get(emp_id)

        if mysql_record and google_record:
            mysql_last_updated = mysql_record['last_updated']
            if mysql_last_updated:
                if isinstance(mysql_last_updated, str):
                    mysql_last_updated = datetime.strptime(mysql_last_updated, '%Y-%m-%d %H:%M:%S')
            
            google_last_updated = google_record['last_updated']
            if google_last_updated:
                if isinstance(google_last_updated, str):
                    google_last_updated = datetime.strptime(google_last_updated, '%Y-%m-%d %H:%M:%S')

            if google_last_updated and google_last_updated.tzinfo is not None:
                google_last_updated = google_last_updated.replace(tzinfo=None)
            if mysql_last_updated and mysql_last_updated.tzinfo is not None:
                mysql_last_updated = mysql_last_updated.replace(tzinfo=None)

            if mysql_last_updated and google_last_updated:
                if mysql_last_updated > last_check_time or google_last_updated > last_check_time:
                    if mysql_last_updated > google_last_updated:
                        to_update_google.append(mysql_record)
                    elif google_last_updated > mysql_last_updated:
                        to_update_mysql.append(google_record)
            elif mysql_last_updated:
                if mysql_last_updated > last_check_time:
                    to_update_google.append(mysql_record)
            elif google_last_updated:
                if google_last_updated > last_check_time:
                    to_update_mysql.append(google_record)
        elif mysql_record:
            mysql_last_updated = mysql_record['last_updated']
            if mysql_last_updated:
                if isinstance(mysql_last_updated, str):
                    mysql_last_updated = datetime.strptime(mysql_last_updated, '%Y-%m-%d %H:%M:%S')
                if mysql_last_updated.tzinfo is not None:
                    mysql_last_updated = mysql_last_updated.replace(tzinfo=None)
                to_update_google.append(mysql_record)
        elif google_record:
            google_last_updated = google_record['last_updated']
            if google_last_updated:
                if isinstance(google_last_updated, str):
                    google_last_updated = datetime.strptime(google_last_updated, '%Y-%m-%d %H:%M:%S')
                if google_last_updated.tzinfo is not None:
                    google_last_updated = google_last_updated.replace(tzinfo=None)
                to_update_mysql.append(google_record)

    return to_update_mysql, to_update_google
