import os
import sys
import json
from dotenv import load_dotenv

# Setup paths
project_root = os.getcwd()
sys.path.append(os.path.join(project_root, 'execution'))

# Add bin to PATH for ffmpeg
bin_dir = os.path.join(project_root, 'bin')
if os.path.exists(bin_dir):
    os.environ["PATH"] += os.pathsep + bin_dir
    print(f"Added local bin to PATH: {bin_dir}")

from services.renderer import RenderService
from services.subtitle_utils import json_to_ass_karaoke

def debug_subs():
    print("Starting Local Karaoke Subtitle Debugger...")
    
    # 1. Create a Fake Transcript with Word Timestamps
    fake_transcript = {
        "text": "This is a test of the karaoke subtitle system.",
        "segments": [
            {
                "start": 0.5,
                "end": 4.5,
                "text": " This is a test of the karaoke subtitle system.",
                "words": [
                    {"word": "This", "start": 0.5, "end": 0.9},
                    {"word": "is", "start": 0.9, "end": 1.1},
                    {"word": "a", "start": 1.1, "end": 1.3},
                    {"word": "test", "start": 1.3, "end": 1.8},
                    {"word": "of", "start": 1.8, "end": 2.0},
                    {"word": "the", "start": 2.0, "end": 2.2},
                    {"word": "karaoke", "start": 2.2, "end": 3.0},
                    {"word": "subtitle", "start": 3.0, "end": 3.8},
                    {"word": "system.", "start": 3.8, "end": 4.5}
                ]
            }
        ]
    }
    
    # 2. Generate ASS Content
    print("Generating ASS content...")
    ass_content = json_to_ass_karaoke(fake_transcript)
    if not ass_content:
        print("Failed to generate ASS content.")
        return
        
    ass_path = "debug_karaoke.ass"
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)
    print(f"Saved subtitle file: {ass_path}")
    print("--- Preview ---")
    print(ass_path)
    print("---------------")

    # 3. Burn Subtitles
    input_video = "debug_input.mp4"
    if not os.path.exists(input_video):
        print(f"Error: {input_video} not found. Please place a test video in this folder.")
        return
        
    output_video = "debug_subs_result.mp4"
    print(f"Burning subtitles to {output_video}...")
    
    renderer = RenderService()
    result = renderer.burn_subtitles(input_video, ass_path, output_video)
    
    if result and os.path.exists(result):
        print(f"\nSUCCESS! Subtitled video generated at: {os.path.abspath(result)}")
        print("Open this file to see the KARAOKE subtitles in action.")
    else:
        print("\nFailed to burn subtitles.")

if __name__ == "__main__":
    debug_subs()
