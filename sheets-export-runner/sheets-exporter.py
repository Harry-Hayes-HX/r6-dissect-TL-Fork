from flask import Flask, request, jsonify
import subprocess
import os
import boto3
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

BUCKET_NAME = "tlmrisserver"
EXPORT_FILE = "exported-to-sheets-sheets.txt"
POST_EXPORT_BUCKET = "tlmrisserver/post-exported-data/"

# Initialize AWS S3 client
s3 = boto3.client('s3')

# Path to your service account JSON file
SERVICE_ACCOUNT_FILE = 'service-account-file.json'

# Initialize Google Sheets API client
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

def download_file_from_s3(bucket, key, local_path):
    s3.download_file(bucket, key, local_path)

def upload_file_to_s3(bucket, key, local_path):
    s3.upload_file(local_path, bucket, key)

def list_files_in_s3_bucket(bucket, prefix=""):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [item['Key'] for item in response.get('Contents', [])]

def create_google_sheet_from_files(file_paths):
    spreadsheet = {
        'properties': {
            'title': 'Exported Data'
        }
    }
    spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                                fields='spreadsheetId').execute()
    spreadsheet_id = spreadsheet.get('spreadsheetId')

    for file_path in file_paths:
        with open(file_path, 'r') as file:
            values = [[line.strip()] for line in file.readlines()]
            body = {
                'values': values
            }
            service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='Sheet1',
                valueInputOption='RAW',
                body=body
            ).execute()

    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"

@app.route('/api/runner', methods=['POST'])
def runner():
    # Step 1: Download the export file from S3
    download_file_from_s3(BUCKET_NAME, EXPORT_FILE, EXPORT_FILE)

    # Step 2: Read the contents of the export file
    with open(EXPORT_FILE, 'r') as file:
        exported_files = file.read().splitlines()

    # Step 3: List the contents of the post-exported-data bucket
    post_export_files = list_files_in_s3_bucket(BUCKET_NAME, POST_EXPORT_BUCKET)

    # Step 4: Download files not in the export file
    new_files = [file for file in post_export_files if file not in exported_files]
    local_file_paths = []
    for file in new_files:
        local_path = os.path.basename(file)
        download_file_from_s3(BUCKET_NAME, file, local_path)
        local_file_paths.append(local_path)

    # Step 5: Export the new files to a Google Sheet
    sheet_link = create_google_sheet_from_files(local_file_paths)

    # Step 6: Update the export file and upload it back to S3
    with open(EXPORT_FILE, 'a') as file:
        for file_name in new_files:
            file.write(f"{file_name},{sheet_link}\n")

    upload_file_to_s3(BUCKET_NAME, EXPORT_FILE, EXPORT_FILE)

    # Step 7: Clean up local files
    for file_path in local_file_paths:
        os.remove(file_path)

    return jsonify({'status': 'success', 'sheet_link': sheet_link})

if __name__ == '__main__':
    app.run(port=5003)