import os
import sys
import time
from dotenv import load_dotenv

# Setup paths
project_root = os.getcwd()
sys.path.append(os.path.join(project_root, 'execution'))

# Add bin to PATH for ffmpeg
bin_dir = os.path.join(project_root, 'bin')
if os.path.exists(bin_dir):
    os.environ["PATH"] += os.pathsep + bin_dir
    print(f"Added local bin to PATH: {bin_dir}")

from services.drive import DriveService
from services.renderer import RenderService
from services.video_analysis import VideoAnalyzer

def debug_intro():
    print("Starting Local Intro Debugger...")
    load_dotenv()
    
    # 1. Init Services
    try:
        drive = DriveService()
        renderer = RenderService()
        analyzer = VideoAnalyzer()
    except Exception as e:
        print(f"Failed to initialize services: {e}")
        return

    # 2. Get Config
    upload_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID_UPLOAD')
    if not upload_folder_id:
        print("Missing GOOGLE_DRIVE_FOLDER_ID_UPLOAD in .env")
        return

    # 4. Download / Check Local
    temp_input = "debug_input.mp4"
    
    if os.path.exists(temp_input):
        print(f"Found local file: {temp_input} (Skipping Drive download)")
    else:
        # 3. Find a video
        print("Scanning Drive for videos...")
        files = drive.list_files(upload_folder_id)
        
        video_file = None
        for f in files:
            if f['name'].lower().endswith(('.mp4', '.mov')):
                video_file = f
                break
                
        if not video_file:
            print("No videos found in Upload folder (and no 'debug_input.mp4' found locally).")
            print("TIP: Copy a video to this folder and rename it 'debug_input.mp4' to test locally without Drive.")
            return

        print(f"Found video: {video_file['name']}")
        print("Downloading video (this may take a moment)...")
        drive.download_file(video_file['id'], temp_input)

    # 5. Extract Metadata (Simulated)
    width = 1080
    height = 1920
    print(f"Assuming Portrait dims: {width}x{height}")

    # 6. Create Intro Overlay
    print("Generating Intro Overlay Image...")
    overlay_path = "debug_intro_overlay.png"
    
    # Use a long-ish title to test wrapping and size and highlighting
    test_title = "THIS IS A *TEST* OF THE *OVERLAY* INTRO SYSTEM"
    
    renderer.create_intro_overlay(test_title, width, height, overlay_path)
    
    if not os.path.exists(overlay_path):
        print("Failed to generate overlay image.")
        return
        
    # 7. Apply Overlay
    print("Applying Overlay to Video...")
    final_output = "debug_intro_result.mp4"
    renderer.apply_intro_overlay(temp_input, overlay_path, final_output)
    
    if os.path.exists(final_output):
        print(f"\nSUCCESS! Intro generated at: {os.path.abspath(final_output)}")
        print("Open this file to see the title OVERLAY on the video (first 6s).")
    else:
        print("\nFailed to generate final video.")

if __name__ == "__main__":
    debug_intro()
