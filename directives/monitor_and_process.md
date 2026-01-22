# Monitor and Process Videos

**Goal**: Continuously monitor the "Upload Completed Videos" folder, process new video files, and output the results.

## Inputs
- **Source Folder**: `1aDgZjfEosshL8o9LBNZGXdG7NBBLqPzU`
- **Configuration**: `.env` file for API keys.

## Steps
1. **Poll**: check the folder every 60 seconds.
2. **Filter**: Only process file types `video/mp4`, `video/quicktime`. Ignore others.
3. **Lock**: Check if the file ID is in `processed_videos.json`. If yes, skip.
4. **Download**: Save to a temporary local path.
5. **Execute Pipeline**:
   - `video_analysis.py` -> Get Metadata.
   - `ai_generation.py` -> Transcribe & Strategize.
   - `renderer.py` -> Render Intro & Subtitles.
6. **Upload**: Save final video to Drive `0AL9nKE7yDZvzUk9PVA`.
7. **Log**: Append row to Google Sheet `1JTJzRwHIFe25MFFmOxofVNbymWUEr9M7VCM3F1zWlfA`.
8. **Clean**: Delete local temp files.

## Error Handling
- If Transcribe fails, log error and skip AI generation (or retry).
- If Render fails, alert user (log to sheet with status FAILED).
