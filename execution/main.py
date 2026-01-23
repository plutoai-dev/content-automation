import time
import os
import json
import logging
from dotenv import load_dotenv
from services.drive import DriveService
from services.video_analysis import VideoAnalyzer
from services.ai_generation import AIService
from services.renderer import RenderService
from services.subtitle_utils import json_to_srt, json_to_ass
from services.sheets import SheetsService


# Load Config
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add local bin folder to PATH for portable ffmpeg
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bin_dir = os.path.join(project_root, 'bin')
if os.path.exists(bin_dir):
    os.environ["PATH"] += os.pathsep + bin_dir
    print(f"Added local bin directory to PATH: {bin_dir}")

PROCESSED_LOG_FILE = "processed_videos.json"

def load_processed_log():
    if os.path.exists(PROCESSED_LOG_FILE):
        with open(PROCESSED_LOG_FILE, 'r') as f:
            return json.load(f)
    return []

def save_processed_log(log):
    with open(PROCESSED_LOG_FILE, 'w') as f:
        json.dump(log, f)

def main():
    """
    Video Content Engine - GitHub Actions Edition
    Processes pending videos once and exits cleanly.
    Designed for automated execution, not continuous polling.
    """
    print("🎬 Starting Video Content Engine (GitHub Actions Edition)...")
    print(f"⏰ Execution started at: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")

    start_time = time.time()
    processed_count = 0
    failed_count = 0

    try:
        # Initialize services
        drive = DriveService()
        video_analyzer = VideoAnalyzer()
        ai = AIService()
        renderer = RenderService()
        sheets = SheetsService()

        # Get configuration
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        upload_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID_UPLOAD')
        final_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID_FINAL')

        if not all([sheet_id, upload_folder_id, final_folder_id]):
            raise ValueError("Missing required environment variables: GOOGLE_SHEET_ID, GOOGLE_DRIVE_FOLDER_ID_UPLOAD, GOOGLE_DRIVE_FOLDER_ID_FINAL")

        # Load processed IDs from Google Sheets (primary source for GitHub Actions)
        print("📊 Loading processed video tracking from Google Sheets...")
        processed_ids = sheets.get_processed_ids(sheet_id) if sheet_id else []
        if not isinstance(processed_ids, list):
            processed_ids = []
        print(f"📋 Tracking {len(processed_ids)} already processed videos")

        # Get pending videos
        print("🔍 Scanning for new videos in upload folder...")
        files = drive.list_files(upload_folder_id)
        pending_files = []

        for file in files:
            # Skip already processed
            if file['id'] in processed_ids:
                continue
            # Skip output files
            if file['name'].startswith("Final_") or file['name'].startswith("Subtitled_"):
                continue
            pending_files.append(file)

        print(f"📹 Found {len(pending_files)} pending videos to process")

        if not pending_files:
            print("✅ No new videos to process. Exiting successfully.")
            return 0

        # Process videos (limit to prevent timeout)
        max_videos = int(os.getenv('MAX_VIDEOS_PER_RUN', '5'))  # Configurable limit
        videos_to_process = pending_files[:max_videos]

        print(f"🎯 Processing {len(videos_to_process)} videos (max {max_videos} per run)")

        for file in videos_to_process:
            video_start_time = time.time()
            temp_input_path = None
            srt_path = None
            ass_path = None
            final_video_path = None
            subtitled_video_path = None
            frame_path = None
            titled_image_path = None
            intro_video_path = None
            base_name = ""

            try:
                print(f"🎬 Processing: {file['name']}")
                sheets.update_status(sheet_id, f"🔄 Processing: {file['name']}")

                # 1. Download
                original_filename = file['name']
                base_name, _ = os.path.splitext(original_filename)
                temp_input_path = f"temp_input_{base_name}.mp4"

                print(f"⬇️  Downloading video...")
                drive.download_file(file['id'], temp_input_path)

                # 2. Analyze
                print(f"🔍 Analyzing video metadata...")
                sheets.update_status(sheet_id, f"🔍 Analyzing: {file['name']}")
                metadata = video_analyzer.get_metadata(temp_input_path)
                print(f"📊 Metadata: {metadata}")

                if not metadata:
                    print("❌ Could not analyze video, skipping.")
                    failed_count += 1
                    continue

                # 3. Transcribe
                print(f"🎙️  Transcribing audio...")
                sheets.update_status(sheet_id, f"🎙️ Transcribing: {file['name']}")
                transcript = ai.transcribe_audio(temp_input_path)
                transcript_text = transcript.text if transcript else ""

                # Generate subtitles
                ass_content = json_to_ass(transcript) if transcript else None
                ass_path = f"temp_{base_name}.ass"
                srt_content = json_to_srt(transcript) if transcript else None
                srt_path = f"temp_{base_name}.srt"

                # 4. Generate Content Strategy
                print(f"🤖 Generating content strategy...")
                sheets.update_status(sheet_id, f"🤖 Generating strategy: {file['name']}")
                strategy = ai.generate_content_strategy(transcript_text, metadata)
                print(f"📝 Strategy generated: {strategy.get('title', 'N/A')}")

                # 5. Render Pipeline
                print(f"🎨 Rendering subtitles...")
                sheets.update_status(sheet_id, f"🎨 Rendering: {file['name']}")
                subtitled_video_path = f"temp_subtitled_{base_name}.mp4"

                # Burn subtitles
                if ass_content:
                    with open(ass_path, "w", encoding="utf-8") as f:
                        f.write(ass_content)
                    print(f"🔥 Burning ASS subtitles...")
                    renderer.burn_subtitles(temp_input_path, ass_path, subtitled_video_path)
                elif srt_content:
                    with open(srt_path, "w", encoding="utf-8") as f:
                        f.write(srt_content)
                    print(f"🔥 Burning SRT subtitles...")
                    renderer.burn_subtitles(temp_input_path, srt_path, subtitled_video_path)
                else:
                    print("⚠️  No transcription available, copying without subtitles")
                    import shutil
                    shutil.copy(temp_input_path, subtitled_video_path)

                # 6. Handle Portrait Short Intro
                if metadata.get('length_category') == 'short' and metadata.get('orientation') == 'portrait':
                    print(f"📱 Generating intro for short portrait video...")
                    sheets.update_status(sheet_id, f"📱 Generating intro: {file['name']}")

                    # Extract first frame
                    frame_path = f"temp_frame_{base_name}.png"
                    renderer.extract_first_frame(temp_input_path, frame_path)

                    # Create intro video
                    intro_video_path = f"temp_intro_{base_name}.mp4"
                    title_text = strategy.get('title', 'Watch This!')
                    renderer.create_intro_video(frame_path, title_text, intro_video_path)

                    # Merge intro + video
                    final_video_path = f"Final_{base_name}.mp4"
                    print(f"🔗 Merging intro and video...")
                    renderer.merge_videos(intro_video_path, subtitled_video_path, final_video_path)
                else:
                    # Just use subtitled video as final
                    final_video_path = f"Final_{base_name}.mp4"
                    if os.path.exists(subtitled_video_path):
                        os.rename(subtitled_video_path, final_video_path)

                # 7. Upload Final Video
                if final_video_path and os.path.exists(final_video_path):
                    print(f"☁️  Uploading final video...")
                    sheets.update_status(sheet_id, f"☁️ Uploading: {file['name']}")
                    upload_result = drive.upload_file(final_video_path, final_folder_id)

                    if upload_result:
                        # 8. Log to Sheets
                        print(f"📊 Logging to Google Sheets...")
                        platforms_list = ["TikTok", "Instagram Reels", "YouTube Shorts"] if metadata.get('orientation') == 'portrait' else ["YouTube Long-form", "LinkedIn"]

                        strategy_text = f"TITLE: {strategy.get('title', 'N/A')}\n\nCAPTION: {strategy.get('caption', 'N/A')}\n\nHASHTAGS: {strategy.get('hashtags', 'N/A')}"
                        if strategy.get('linkedin_post'):
                            strategy_text += f"\n\nLINKEDIN: {strategy['linkedin_post']}"
                        if strategy.get('tiktok_caption'):
                            strategy_text += f"\n\nTIKTOK: {strategy['tiktok_caption']}"

                        sheets.log_video(
                            sheet_id,
                            file['id'],
                            file.get('webViewLink', 'N/A'),
                            upload_result.get('webViewLink', 'N/A'),
                            platforms_list,
                            strategy_text
                        )

                        processed_count += 1
                        video_time = time.time() - video_start_time
                        print(f"✅ Successfully processed {file['name']} in {video_time:.1f}s")
                    else:
                        print(f"❌ Upload failed for {file['name']}")
                        failed_count += 1
                else:
                    print(f"❌ No final video generated for {file['name']}")
                    failed_count += 1

            except Exception as e:
                print(f"❌ Error processing {file.get('name', 'unknown')}: {e}")
                failed_count += 1

            finally:
                # Cleanup temporary files
                files_to_clean = [
                    temp_input_path, srt_path, ass_path,
                    final_video_path, subtitled_video_path,
                    frame_path, titled_image_path, intro_video_path
                ]
                for p in files_to_clean:
                    if p and os.path.exists(p):
                        try:
                            os.remove(p)
                            print(f"🧹 Cleaned up: {p}")
                        except Exception as cleanup_err:
                            print(f"⚠️  Cleanup warning: Could not delete {p}: {cleanup_err}")

        # Summary
        total_time = time.time() - start_time
        print("
📊 Processing Summary:"        print(f"   ✅ Videos processed: {processed_count}")
        print(f"   ❌ Videos failed: {failed_count}")
        print(f"   ⏱️  Total time: {total_time:.1f}s")
        print(f"   🎯 Success rate: {(processed_count / max(1, processed_count + failed_count) * 100):.1f}%")

        # Update final status
        if sheet_id:
            final_status = f"✅ Completed: {processed_count} processed, {failed_count} failed"
            sheets.update_status(sheet_id, final_status)

        return 0 if failed_count == 0 else 1  # Exit code for GitHub Actions

    except Exception as e:
        print(f"💥 Critical error in main execution: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    main()
