import os
import sys
import json
import ffmpeg
from dotenv import load_dotenv

# Setup paths
project_root = os.getcwd()
sys.path.append(os.path.join(project_root, 'execution'))

# Add bin to PATH for ffmpeg
bin_dir = os.path.join(project_root, 'bin')
if os.path.exists(bin_dir):
    os.environ["PATH"] += os.pathsep + bin_dir

from services.renderer import RenderService
from services.subtitle_utils import json_to_ass_karaoke

def debug_preview():
    print("Starting Combined Preview Generation...")
    
    # 1. Setup Input
    input_video = "debug_input.mp4"
    if not os.path.exists(input_video):
        print(f"Input {input_video} not found. Generating dummy video...")
        try:
            # Generate video with silent audio
            video_input = ffmpeg.input('color=c=blue:s=1080x1920:d=10', f='lavfi')
            audio_input = ffmpeg.input('anullsrc=channel_layout=stereo:sample_rate=44100', f='lavfi', t=10)
            
            (
                ffmpeg
                .output(video_input, audio_input, input_video, vcodec='libx264', acodec='aac')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            print("Dummy video generated.")
        except ffmpeg.Error as e:
            print(f"Failed to generate dummy video: {e.stderr.decode()}")
            return
        except Exception as e:
            print(f"Failed to generate dummy video (unknown error): {e}")
            return
    
    # 2. Services
    renderer = RenderService()
    
    # 3. Generate Intro Overlay (White Box, Rounded, Small Font)
    print("1. Generating Intro Overlay...")
    overlay_path = "debug_final_intro.png"
    intro_title = "WATCH THIS VIDEO TO SEE NEW *MONTSERRAT* FONT AND COMPACT SUBTITLES!"
    
    # Assume portrait for test
    width = 1080
    height = 1920
    
    renderer.create_intro_overlay(intro_title, width, height, overlay_path)
    if not os.path.exists(overlay_path):
        print("Failed to generate intro image.")
        return

    # 4. Generate Subtitles (Wine Color, Box Highlight)
    print("2. Generating Karaoke Subtitles...")
    fake_transcript = {
        "text": "This is a combined test of the new intro and wine subtitles.",
        "segments": [
            {
                "start": 0.5,
                "end": 5.5,
                "text": " This is a combined test of the new intro and wine subtitles.",
                "words": [
                    {"word": "This", "start": 0.5, "end": 0.8},
                    {"word": "is", "start": 0.8, "end": 1.0},
                    {"word": "a", "start": 1.0, "end": 1.2},
                    {"word": "combined", "start": 1.2, "end": 1.8},
                    {"word": "test", "start": 1.8, "end": 2.2},
                    {"word": "of", "start": 2.2, "end": 2.5},
                    {"word": "the", "start": 2.5, "end": 2.8},
                    {"word": "new", "start": 2.8, "end": 3.2},
                    {"word": "intro", "start": 3.2, "end": 3.8},
                    {"word": "and", "start": 3.8, "end": 4.0},
                    {"word": "wine", "start": 4.0, "end": 4.5},
                    {"word": "subtitles.", "start": 4.5, "end": 5.5}
                ]
            }
        ]
    }
    ass_content = json_to_ass_karaoke(fake_transcript)
    ass_path = "debug_final_subs.ass"
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

    # 5. Apply Both (Complex Filter or Two Steps)
    # create_intro_overlay just makes the image. apply_intro_overlay applies it.
    # burn_subtitles burns subs.
    # To do both, we can chain: Video -> Burn Subs -> Apply Intro (Intro on top of subs? Or subs on top of intro?)
    # Usually intro title overlay is at center/top, subs at bottom. They shouldn't overlap.
    # Let's do: Video -> Apply Intro Overlay -> Burn Subtitles (Subs usually on top of everything)
    
    temp_video_with_intro = "temp_preview_intro.mp4"
    final_output = "debug_preview_all.mp4"
    
    print("3. Applying Intro Overlay to Video...")
    renderer.apply_intro_overlay(input_video, overlay_path, temp_video_with_intro)
    
    if os.path.exists(temp_video_with_intro):
        print("4. Burning Subtitles into Video...")
        renderer.burn_subtitles(temp_video_with_intro, ass_path, final_output)
        
        if os.path.exists(final_output):
            print(f"\nSUCCESS! Preview generated at: {os.path.abspath(final_output)}")
            
            # Clean up temp
            os.remove(temp_video_with_intro)
        else:
            print("Failed to burn subtitles.")
    else:
        print("Failed to apply intro overlay.")

if __name__ == "__main__":
    debug_preview()
