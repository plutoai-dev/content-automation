import time
import os
import json
from dotenv import load_dotenv
from services.drive import DriveService
from services.video_analysis import VideoAnalyzer
from services.ai_generation import AIService
from services.renderer import RenderService
from services.subtitle_utils import json_to_srt, json_to_ass
from services.sheets import SheetsService


# Load Config
load_dotenv()

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
    print("Starting Video Content Engine (GitHub Actions Edition)...")
    print(f"Execution started at: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")

    try:
        drive = DriveService()
        video_analyzer = VideoAnalyzer()
        ai = AIService()
        renderer = RenderService()
        sheets = SheetsService()
    except Exception as e:
        print(f"Failed to initialize services: {e}")
        return 1

    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    upload_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID_UPLOAD')
    final_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID_FINAL')

    if not all([sheet_id, upload_folder_id, final_folder_id]):
        print("ERROR: Missing required environment variables")
        return 1

    # Get processed IDs from Google Sheets only (reliable state management)
    print("Loading processed video IDs from Google Sheets...")
    processed_ids = sheets.get_processed_ids(sheet_id) if sheet_id else []
    if not isinstance(processed_ids, list):
        processed_ids = []
    print(f"Tracking {len(processed_ids)} already processed videos.")

    try:
        print("Scanning for new videos in upload folder...")
        files = drive.list_files(upload_folder_id)
        print(f"Found {len(files)} total files in upload folder")

        new_videos_found = 0
        processed_count = 0
        failed_count = 0

        for file in files:
                # Initialization for safety
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
                    # Skip already processed IDs
                    if file['id'] in processed_ids:
                        continue

                    # Skip videos that are actually final outputs (same folder requirement)
                    if file['name'].startswith("Final_") or file['name'].startswith("Subtitled_"):
                        continue

                    new_videos_found += 1
                    print(f"[{new_videos_found}] Processing new file: {file['name']}")
                    sheets.update_status(sheet_id, f"Processing: {file['name']}")
                    
                    # 1. Download
                    original_filename = file['name']
                    base_name, _ = os.path.splitext(original_filename)
                    temp_input_path = f"temp_input_{base_name}.mp4"
                    
                    drive.download_file(file['id'], temp_input_path)
                    
                    # 2. Analyze
                    sheets.update_status(sheet_id, f"Analyzing video: {file['name']}")
                    metadata = video_analyzer.get_metadata(temp_input_path)
                    print(f"Metadata: {metadata}")
                    
                    if not metadata:
                        print("Could not analyze video, skipping.")
                        continue

                    # 3. Transcribe
                    sheets.update_status(sheet_id, f"Transcribing (high quality): {file['name']}")
                    print("Transcribing video...")
                    transcript = ai.transcribe_audio(temp_input_path)
                    transcript_text = transcript.text if transcript else ""
                    
                    # Generate modern ASS subtitles (TikTok style)
                    ass_content = json_to_ass(transcript)
                    ass_path = f"temp_{base_name}.ass"
                    
                    # Also generate SRT as fallback
                    srt_content = json_to_srt(transcript)
                    srt_path = f"temp_{base_name}.srt"
                    
                    # 4. Generate Content Strategy
                    sheets.update_status(sheet_id, "Generating content strategy...")
                    print("Generating content strategy...")
                    strategy = ai.generate_content_strategy(transcript_text, metadata)
                    print(f"Strategy: {strategy}")
                    
                    # 5. Render Pipeline
                    sheets.update_status(sheet_id, "Rendering subtitles...")
                    subtitled_video_path = f"temp_subtitled_{base_name}.mp4"
                    
                    # Use modern ASS subtitles (yellow highlights, bold styling)
                    if ass_content:
                        with open(ass_path, "w", encoding="utf-8") as f:
                            f.write(ass_content)
                        print(f"Burning modern subtitles to {subtitled_video_path}...")
                        renderer.burn_subtitles(temp_input_path, ass_path, subtitled_video_path)
                    elif srt_content:
                        with open(srt_path, "w", encoding="utf-8") as f:
                            f.write(srt_content)
                        print(f"Burning fallback subtitles to {subtitled_video_path}...")
                        renderer.burn_subtitles(temp_input_path, srt_path, subtitled_video_path)
                    else:
                        print("No transcription found/empty SRT. Skipping subtitle burn.")
                        import shutil
                        shutil.copy(temp_input_path, subtitled_video_path)
                    
                    # Step 5b: Handle Portrait Short Intro
                    if metadata['length_category'] == 'short' and metadata['orientation'] == 'portrait':
                        sheets.update_status(sheet_id, "Generating Short Intro frame & animation...")
                        print("Detected Short Portrait Video - Generating Intro...")
                        
                        # Extract First Frame
                        frame_path = f"temp_frame_{base_name}.png"
                        renderer.extract_first_frame(temp_input_path, frame_path)
                        
                        titled_image_path = frame_path.replace(".png", "_titled.png")
                        
                        # Create Intro Video (Static 6s with text)
                        intro_video_path = f"temp_intro_{base_name}.mp4"
                        title_text = strategy.get('title', 'Watch This!')
                        renderer.create_intro_video(frame_path, title_text, intro_video_path)
                        
                        # Merge Intro + Subtitled Video
                        sheets.update_status(sheet_id, "Finalizing merge...")
                        final_video_path = f"Final_{base_name}.mp4"
                        print(f"Merging intro and body to {final_video_path}...")
                        renderer.merge_videos(intro_video_path, subtitled_video_path, final_video_path)
                        
                    else:
                        # Just rename/use the subtitled one as final
                        final_video_path = f"Final_{base_name}.mp4"
                        if os.path.exists(subtitled_video_path):
                            os.rename(subtitled_video_path, final_video_path)
                    
                    # 6. Upload Final
                    if final_video_path and os.path.exists(final_video_path):
                        sheets.update_status(sheet_id, "Uploading finished product...")
                        print(f"Uploading final video: {final_video_path}")
                        upload_result = drive.upload_file(final_video_path, final_folder_id)
                        
                        # 7. Log to Sheets
                        if upload_result:
                            sheets.update_status(sheet_id, "Syncing metadata to logs...")
                            platforms_list = ["TikTok", "Instagram Reels", "YouTube Shorts"] if metadata['orientation'] == 'portrait' else ["YouTube Long-form", "LinkedIn"]
                            
                            strategy_text = f"TITLE: {strategy.get('title', 'N/A')}\n\nCAPTION: {strategy.get('caption', 'N/A')}\n\nHASHTAGS: {strategy.get('hashtags', 'N/A')}"
                            if strategy.get('linkedin_post'): strategy_text += f"\n\nLINKEDIN: {strategy['linkedin_post']}"
                            if strategy.get('tiktok_caption'): strategy_text += f"\n\nTIKTOK: {strategy['tiktok_caption']}"

                            sheets.log_video(sheet_id, file['id'], file.get('webViewLink', 'N/A'), upload_result.get('webViewLink', 'N/A'), platforms_list, strategy_text)

                        print(f"✅ Success! Processed {file['name']}")
                        processed_ids.append(file['id'])
                        processed_count += 1
                    else:
                        print(f"Failed to generate final video for {file['name']}")

                except Exception as e:
                    print(f"❌ Error processing video {file.get('name', 'unknown')}: {e}")
                    failed_count += 1
                    sheets.update_status(sheet_id, f"Failed: {file.get('name', 'unknown')} - {str(e)[:100]}")

                finally:
                    # Comprehensive cleanup
                    files_to_clean = [
                        temp_input_path, srt_path, ass_path,
                        final_video_path, subtitled_video_path,
                        frame_path, titled_image_path, intro_video_path
                    ]
                    for p in files_to_clean:
                        if p and os.path.exists(p):
                            try:
                                os.remove(p)
                            except Exception as cleanup_err:
                                print(f"Cleanup warning: Could not delete {p}: {cleanup_err}")

        # Final summary
        print(f"\n{'='*50}")
        print("EXECUTION SUMMARY")
        print(f"{'='*50}")
        print(f"Total files scanned: {len(files)}")
        print(f"New videos found: {new_videos_found}")
        print(f"Successfully processed: {processed_count}")
        print(f"Failed to process: {failed_count}")
        print(f"Execution completed at: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
        print(f"{'='*50}\n")

        # Update final status
        if processed_count > 0:
            sheets.update_status(sheet_id, f"Completed: {processed_count} videos processed")
        elif new_videos_found == 0:
            sheets.update_status(sheet_id, "No new videos to process")
        else:
            sheets.update_status(sheet_id, f"Completed with {failed_count} failures")

        # Return appropriate exit code
        return 0 if failed_count == 0 else 1

    except Exception as e:
        print(f"❌ Critical error in main execution: {e}")
        if sheet_id:
            try:
                sheets.update_status(sheet_id, f"Critical error: {str(e)[:100]}")
            except:
                pass
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
