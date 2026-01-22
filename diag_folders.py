import os
from dotenv import load_dotenv
from execution.services.drive import DriveService

load_dotenv()

def diag():
    drive = DriveService()
    upload_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID_UPLOAD')
    final_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID_FINAL')
    
    print(f"--- FOLDER DIAGNOSTIC ---")
    print(f"Upload Folder ID: {upload_id}")
    print(f"Final Folder ID:  {final_id}")
    
    # 1. Check Upload Folder
    try:
        folder = drive.service.files().get(fileId=upload_id, fields="id, name, parents", supportsAllDrives=True).execute()
        print(f"\n[UPLOAD FOLDER]")
        print(f"Name: {folder.get('name')}")
        print(f"Parents: {folder.get('parents')}")
    except Exception as e:
        print(f"[ERROR] Cannot access Upload Folder: {e}")

    # 2. Check Final Folder
    try:
        folder = drive.service.files().get(fileId=final_id, fields="id, name, parents", supportsAllDrives=True).execute()
        print(f"\n[FINAL FOLDER]")
        print(f"Name: {folder.get('name')}")
        print(f"Parents: {folder.get('parents')}")
    except Exception as e:
        print(f"[ERROR] Cannot access Final Folder: {e}")

    # 3. List files in Upload Folder and check their parents
    print(f"\n--- Files in Upload Folder ---")
    try:
        files = drive.list_files(upload_id)
        for f in files:
            # Get full metadata including parents
            meta = drive.service.files().get(fileId=f['id'], fields="id, name, parents", supportsAllDrives=True).execute()
            print(f"- {meta['name']} (ID: {meta['id']}) parents: {meta.get('parents')}")
    except Exception as e:
        print(f"Error listing files: {e}")

if __name__ == "__main__":
    diag()
