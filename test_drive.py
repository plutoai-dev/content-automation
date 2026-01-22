import os
import json
from dotenv import load_dotenv
from execution.services.drive import DriveService

load_dotenv()

def test():
    print("--- START DRIVE DEBUG ---")
    drive = DriveService()
    if not drive.service:
        print("CRITICAL: Drive service could not be initialized (service_account.json missing?)")
        return

    upload_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID_UPLOAD')
    final_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID_FINAL')
    
    print(f"Checking Upload Folder ID: {upload_id}")
    try:
        folder = drive.service.files().get(fileId=upload_id, fields="id, name", supportsAllDrives=True).execute()
        print(f"SUCCESS: Found Upload Folder: {folder.get('name')}")
    except Exception as e:
        print(f"ERROR: Cannot see Upload Folder: {e}")

    print(f"\nChecking Final Folder ID: {final_id}")
    try:
        folder = drive.service.files().get(fileId=final_id, fields="id, name", supportsAllDrives=True).execute()
        print(f"SUCCESS: Found Final Folder: {folder.get('name')}")
    except Exception as e:
        print(f"ERROR: Cannot see Final Folder: {e}")

    print("\n--- Listing ALL accessible files (including Shared Drives) ---")
    try:
        results = drive.service.files().list(
            pageSize=20, 
            fields="files(id, name, mimeType)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        files = results.get('files', [])
        if not files:
            print("Zero files accessible to this service account.")
        else:
            for f in files:
                print(f" - {f['name']} ({f['id']}) [{f['mimeType']}]")
    except Exception as e:
        print(f"ERROR listing files: {e}")
    print("--- END DRIVE DEBUG ---")

if __name__ == "__main__":
    test()
