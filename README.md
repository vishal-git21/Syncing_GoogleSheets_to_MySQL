[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/AHFn7Vbn)
# Superjoin Hiring Assignment

### Welcome to Superjoin's hiring assignment! 🚀

### Objective
Build a solution that enables real-time synchronization of data between a Google Sheet and a specified database (e.g., MySQL, PostgreSQL). The solution should detect changes in the Google Sheet and update the database accordingly, and vice versa.

### Problem Statement
Many businesses use Google Sheets for collaborative data management and databases for more robust and scalable data storage. However, keeping the data synchronised between Google Sheets and databases is often a manual and error-prone process. Your task is to develop a solution that automates this synchronisation, ensuring that changes in one are reflected in the other in real-time.

### Requirements:
1. Real-time Synchronisation
  - Implement a system that detects changes in Google Sheets and updates the database accordingly.
   - Similarly, detect changes in the database and update the Google Sheet.
  2.	CRUD Operations
   - Ensure the system supports Create, Read, Update, and Delete operations for both Google Sheets and the database.
   - Maintain data consistency across both platforms.
   
### Optional Challenges (This is not mandatory):
1. Conflict Handling
- Develop a strategy to handle conflicts that may arise when changes are made simultaneously in both Google Sheets and the database.
- Provide options for conflict resolution (e.g., last write wins, user-defined rules).
    
2. Scalability: 	
- Ensure the solution can handle large datasets and high-frequency updates without performance degradation.
- Optimize for scalability and efficiency.

## Submission ⏰
The timeline for this submission is: **Next 2 days**

Some things you might want to take care of:
- Make use of git and commit your steps!
- Use good coding practices.
- Write beautiful and readable code. Well-written code is nothing less than a work of art.
- Use semantic variable naming.
- Your code should be organized well in files and folders which is easy to figure out.
- If there is something happening in your code that is not very intuitive, add some comments.
- Add to this README at the bottom explaining your approach (brownie points 😋)
- Use ChatGPT4o/o1/Github Co-pilot, anything that accelerates how you work 💪🏽. 

Make sure you finish the assignment a little earlier than this so you have time to make any final changes.

Once you're done, make sure you **record a video** showing your project working. The video should **NOT** be longer than 120 seconds. While you record the video, tell us about your biggest blocker, and how you overcame it! Don't be shy, talk us through, we'd love that.

We have a checklist at the bottom of this README file, which you should update as your progress with your assignment. It will help us evaluate your project.

- [ ] My code's working just fine! 🥳
- [ ] I have recorded a video showing it working and embedded it in the README ▶️
- [ ] I have tested all the normal working cases 😎
- [ ] I have even solved some edge cases (brownie points) 💪
- [ ] I added my very planned-out approach to the problem at the end of this README 📜

## Got Questions❓
Feel free to check the discussions tab, you might get some help there. Check out that tab before reaching out to us. Also, did you know, the internet is a great place to explore? 😛

We're available at techhiring@superjoin.ai for all queries. 

All the best ✨.



# Developer's Section

## Approach

## Project Directory Structure

The following is the directory structure for the project:

```
.
├── .github
│   └── .keep
├── __pycache__
├── config.py
├── last_check.txt
├── README.md
├── requirements.txt
├── scripts
│   ├── google_sheets_operations.py
│   ├── main.py
│   ├── mysql_operations.py
│   ├── sync.py
│   └── utils.py
└── sync.log

```
- **.github/**: Contains GitHub-related files and configurations.
  - **.keep**: Placeholder file to ensure the directory is tracked by Git.

- **__pycache__/**: Contains compiled Python files.

- **config.py**: Configuration file for the project.

- **last_check.txt**: Stores the timestamp of the last synchronization.

- **README.md**: This file contains the documentation for the project.

- **requirements.txt**: Lists the Python dependencies for the project.

- **scripts/**: Directory containing Python scripts for various operations.
  - **google_sheets_operations.py**: Script for interacting with Google Sheets.
  - **main.py**: Main script to run the synchronization process.
  - **mysql_operations.py**: Script for interacting with MySQL.
  - **sync.py**: Script for synchronizing data between Google Sheets and MySQL.
  - **utils.py**: Utility functions used in the project.

- **sync.log**: Log file for recording synchronization events and errors.


### Synchronization Logic

1. **Load Last Update Time**:
   - The script begins by loading the last update time from a local file (`last_check.txt`). This timestamp indicates when the last synchronization occurred. If the file does not exist, the script defaults to a past date to ensure all records are processed initially.

2. **Fetch Records**:
   - **From MySQL**: Records are fetched from the MySQL database where the `last_updated` timestamp is greater than the last update time.
   - **From Google Sheets**: Records are fetched from the specified Google Sheets document.

3. **Compare Timestamps**:
   - Both MySQL and Google Sheets records are compared based on their `last_updated` timestamps. To avoid issues with timezone differences, timestamps are converted to naive datetime objects (i.e., without timezone info) before comparison.
   - For each record, the script checks which source has the more recent update:
     - If the MySQL record is more recent, it updates the Google Sheets document.
     - If the Google Sheets record is more recent, it updates the MySQL database.

4. **Update Records**:
   - **MySQL**: Updates are performed using an `INSERT ... ON DUPLICATE KEY UPDATE` query to ensure that records are inserted if they do not exist and updated if they do.
   - **Google Sheets**: Updates are made by writing the modified records back to the Google Sheets document, starting from a specific cell range.

5. **Handle Date and Time Formatting**:
   - Dates are formatted to match the expected format (`'YYYY-MM-DD'`) in Google Sheets.
   - Empty or NULL values are handled appropriately:
     - MySQL: If there is no date value, it is set to `NULL`.
     - Google Sheets: Empty fields are left blank.

6. **Save Last Update Time**:
   - After processing all records and making updates, the current timestamp is saved to `last_check.txt` to serve as the new reference for the next synchronization.

### Error Handling
- **MySQL Errors**: Errors during MySQL operations (e.g., date formatting issues) are logged and handled gracefully.
- **Google Sheets Errors**: Errors during Google Sheets operations (e.g., JSON serialization issues) are logged, and the script attempts to continue with other records.
- All the details of the task are logged onto the sync.txt file

## Google Sheets API Setup

1. **Create a Google Cloud Project**:
   - Create a new project on the [Google Cloud Console](https://console.cloud.google.com/).

2. **Enable Google Sheets API**:
   - Enable the Google Sheets API for the project.

3. **Create Service Account**:
   - Create a service account with the Editor role.
   - Generate a new key file (usually named `credentials.json`).

4. **Share Google Sheets Document**:
   - Share the Google Sheets document with the service account email address to grant access.

## Scheduled Execution

- The script is set up to run regularly using a task scheduler to ensure continuous synchronization between MySQL and Google Sheets.




*Add your video here, and your approach to the problem (optional). Leave some comments for us here if you want, we will be reading this :)*
