import logging
import os
from datetime import datetime

def load_last_update_time(file_path='last_check.txt'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            last_update_time_str = f.read().strip()
            return datetime.fromisoformat(last_update_time_str)
    else:
        return datetime(2020, 1, 1)  # Default to a past date if the file does not exist

def save_last_update_time(file_path, last_update_time):
    with open(file_path, 'w') as f:
        f.write(last_update_time.isoformat())
