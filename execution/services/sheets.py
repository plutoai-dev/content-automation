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

    def log_processing_start(self, sheet_id, original_id, original_link, filename):
        """Append a new log entry marked as 'Processing' to lock the file."""
        if not self.service: return
        
        # Use A2:A as the anchor to ensure we fill from the next empty row below the header
        range_name = "'Content Engine'!A2:A"
        
        # Columns: Timestamp, Original Link, Final Link, Platforms, Status, Original ID, Strategy, Duration
        values = [[
            timestamp,
            original_link,
            "Processing...",      # Final Link placeholder
            "Processing...",      # Platforms placeholder
            "Processing",         # Status
            original_id,
            f"Started: {filename}", # Strategy placeholder
            ""                    # Duration placeholder
        ]]
        
        body = {'values': values}
        
        try:
            # Standard append finds the next empty row at the bottom
            self.service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            print(f"🔒 Locked video {filename} in Sheet (appended to next empty row)")
        except Exception as e:
            print(f"Error logging start to sheets: {e}")

    def update_log_completion(self, sheet_id, original_id, final_link, platforms, strategy_content, status="Completed", duration=None):
        """Find the row with original_id and update it with final details."""
        if not self.service: return
        
        # 1. Find the row index (LAST occurrence to avoid overwriting old processed videos)
        ids = self.get_processed_ids(sheet_id)
        try:
            # Find LAST occurrence by reversing the list
            # This ensures we update the most recently added row, not an old one
            reversed_ids = list(reversed(ids))
            reverse_index = reversed_ids.index(original_id)
            # Convert back to original position: len - 1 - reverse_index
            list_index = len(ids) - 1 - reverse_index
            # ids list corresponds to rows 2, 3, 4... (0-indexed in list -> 2-indexed in sheet)
            row_index = list_index + 2 
        except ValueError:
            print(f"⚠️ Could not find row for {original_id} to update")
            return

        # 2. Update the row
        # Range C:H covers: Final Link(C), Platforms(D), Status(E), ID(F), Strategy(G), Duration(H)
        range_name = f"'Content Engine'!C{row_index}:H{row_index}"
        
        values = [[
            final_link,
            ", ".join(platforms) if isinstance(platforms, list) else platforms,
            status,
            original_id,
            strategy_content,
            str(duration) if duration else ""
        ]]
        
        body = {'values': values}
        
        try:
            self.service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            print(f"✅ Updated Sheet row {row_index} directly w/ status {status}")
        except Exception as e:
            print(f"Error updating sheet: {e}")

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
    def update_status(self, sheet_id, status_text, state="Processing"):
        """Overwrite the current status in 'Backend Monitoring' (Col A=State, Col B=Message)."""
        if not self.service: return
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        message = f"[{timestamp}] {status_text}"
        
        range_name = "'Backend Monitoring'!A1:B1"
        body = {'values': [[state, message]]}
        
        try:
            self.service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
        except Exception as e:
            # If sheet doesn't exist, we might need to handle it, but for now just print
            print(f"Error updating status: {e}")
