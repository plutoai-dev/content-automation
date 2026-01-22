import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

class SheetsService:
    def __init__(self):
        self.creds = None
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        
        # Try loading from ENV variable first (Content)
        json_creds = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service_account.json')
        
        if json_creds:
            import json
            info = json.loads(json_creds)
            self.creds = service_account.Credentials.from_service_account_info(
                info, scopes=SCOPES)
            self.service = build('sheets', 'v4', credentials=self.creds)
        elif os.path.exists(creds_path):
            self.creds = service_account.Credentials.from_service_account_file(
                creds_path, scopes=SCOPES)
            self.service = build('sheets', 'v4', credentials=self.creds)
        else:
            self.service = None

    def log_video(self, sheet_id, original_id, original_link, final_link, platforms, strategy_content="N/A"):
        """Append a new log entry to the Google Sheet."""
        if not self.service: return
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        range_name = "'Content Engine'!A:G"  # Extended to column G for Content Strategy
        
        values = [[
            timestamp,
            original_link,
            final_link,
            ", ".join(platforms) if isinstance(platforms, list) else platforms,
            "Completed",
            original_id,
            strategy_content
        ]]
        
        body = {'values': values}
        
        try:
            self.service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
        except Exception as e:
            print(f"Error logging to sheets: {e}")

    def get_processed_ids(self, sheet_id):
        """Fetch all original file IDs already processed from the sheet."""
        if not self.service: return []
        
        try:
            range_name = "'Content Engine'!F2:F" # All IDs in column F
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            values = result.get('values', [])
            return [row[0] for row in values if row]
        except Exception as e:
            print(f"Error fetching IDs from sheets: {e}")
            return []
