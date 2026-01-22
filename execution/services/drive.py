import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

class DriveService:
    def __init__(self):
        self.creds = None
        SCOPES = ['https://www.googleapis.com/auth/drive']
        
        # Try loading from ENV variable first (Content)
        json_creds = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service_account.json')

        if json_creds:
            import json
            info = json.loads(json_creds)
            self.creds = service_account.Credentials.from_service_account_info(
                info, scopes=SCOPES)
            self.service = build('drive', 'v3', credentials=self.creds)
        elif os.path.exists(creds_path):
            self.creds = service_account.Credentials.from_service_account_file(
                creds_path, scopes=SCOPES)
            self.service = build('drive', 'v3', credentials=self.creds)
        else:
            print(f"Warning: {creds_path} not found. Drive service will fail if used.")
            self.service = None

    def list_files(self, folder_id):
        """List video files in a specific folder."""
        if not self.service: return []
        
        query = f"'{folder_id}' in parents and (mimeType contains 'video/')"
        results = self.service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, webViewLink, webContentLink, createdTime, mimeType)",
            orderBy="createdTime desc",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        return results.get('files', [])

    def download_file(self, file_id, destination_path):
        """Download a file from Drive."""
        if not self.service: return
        
        request = self.service.files().get_media(fileId=file_id, supportsAllDrives=True)
        fh = io.FileIO(destination_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")

    def upload_file(self, file_path, folder_id):
        """Upload a file to Drive."""
        if not self.service: return None
        
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        file = self.service.files().create(body=file_metadata,
                                            media_body=media,
                                            supportsAllDrives=True,
                                            fields='id, webViewLink').execute()
        return file
