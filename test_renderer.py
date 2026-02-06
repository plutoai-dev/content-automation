import os
import sys
from PIL import Image

import os
import sys
from PIL import Image

# Add execution directory to path
project_root = os.getcwd() # c:\Users\DeeMindz\Documents\Social content automation
sys.path.append(os.path.join(project_root, 'execution'))

# Add bin to PATH for ffmpeg
bin_dir = os.path.join(project_root, 'bin')
if os.path.exists(bin_dir):
    os.environ["PATH"] += os.pathsep + bin_dir
    print(f"Added local bin to PATH: {bin_dir}")

from services.renderer import RenderService

def test_renderer():
    print("Testing Renderer Service...")
    service = RenderService()
    
    # Create dummy assets
    if not os.path.exists("test_frame.png"):
        img = Image.new('RGB', (1080, 1920), color = 'blue')
        img.save('test_frame.png')
        print("Created dummy frame")

    # Test 1: Intro Creation
    print("\n[1] Testing Intro Creation (Massive Title)...")
    try:
        output = service.create_intro_video(
            "test_frame.png", 
            "THIS IS A MASSIVE TEST TITLE FOR VIRAL CONTENT", 
            "test_intro.mp4"
        )
        if output and os.path.exists(output):
            print(f"✅ Intro created successfully: {output}")
            print("Please verify visually that text is huge.")
        else:
            print("❌ Intro creation returned None or file missing")
    except Exception as e:
        print(f"❌ Intro creation crashed: {e}")

    # Test 2: Subtitle Burning (Fake run)
    # We need a dummy video. Let's use the intro as the input video for burning!
    print("\n[2] Testing Subtitle Burning...")
    
    # Create dummy ASS file
    ass_content = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Impact,90,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,2,50,50,200,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:02.00,Default,,0,0,0,,TESTING SUBTITLES
"""
    with open("test_subs.ass", "w") as f:
        f.write(ass_content)

    try:
        if os.path.exists("test_intro.mp4"):
            output_sub = service.burn_subtitles("test_intro.mp4", "test_subs.ass", "test_subs_output.mp4")
            if output_sub and os.path.exists(output_sub):
                print(f"✅ Subtitles burnt successfully: {output_sub}")
            else:
                print("❌ Subtitle burn returned None or file missing")
        else:
            print("Skipping subtitle test (intro creation failed)")
    except Exception as e:
        print(f"❌ Subtitle burn crashed: {e}")

if __name__ == "__main__":
    test_renderer()
