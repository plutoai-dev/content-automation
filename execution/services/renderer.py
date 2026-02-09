import os
import subprocess
import ffmpeg
from PIL import Image, ImageDraw, ImageFont

class RenderService:
    def __init__(self):
        # Ensure ffmpeg is in path or define path here
        pass

    def create_intro_overlay(self, title_text, width, height, output_image_path):
        """
        Create a transparent PNG with the title text styled as white blocks with black text.
        Reference: TikTok/Reels style title overlay.
        """
        try:
            # Create transparent image
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Font setup
            is_portrait = height > width
            base_font_size = int(height * 0.05) if is_portrait else int(height * 0.06)
            
            # Use Montserrat-Bold if available, else standard font
            font_path = "assets/fonts/Montserrat-Bold.ttf"
            if not os.path.exists(font_path):
                # Fallback to system fonts or default
                font_path = "arial.ttf" # Or "impact.ttf"
                
            try:
                font = ImageFont.truetype(font_path, base_font_size)
            except IOError:
                font = ImageFont.load_default()
                print("Warning: Could not load requested font. Using default.")

            # Text Wrapping
            max_width = int(width * 0.85) # Keep some padding
            words = title_text.split()
            lines = []
            current_line = []
            
            for word in words:
                # Strip asterisks if present
                clean_word = word.replace('*', '') 
                test_line = ' '.join(current_line + [clean_word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                line_width = bbox[2] - bbox[0]
                
                if line_width <= max_width:
                    current_line.append(clean_word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [clean_word]
                    else:
                        lines.append(clean_word)
                        current_line = []
            if current_line:
                lines.append(' '.join(current_line))
                
            # Rendering Lines - VARIABLE WIDTH STYLE (Hugging Text)
            if not lines:
                return None

            line_height = int(base_font_size * 1.2)
            # Tighter vertical spacing so boxes look connected/grouped
            line_spacing = 5 
            
            # Calculate total height of the text block + padding
            total_text_height = (len(lines) * line_height) + ((len(lines) - 1) * line_spacing)
            
            # Vertical centering
            start_y = (height - total_text_height) / 2
            
            padding_x = 30
            padding_y = 15
            corner_radius = 20
            
            # First Pass: Draw Background Boxes
            current_y = start_y
            
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1] # Actual text height
                
                # Center horizontally
                center_x = width / 2
                text_x = center_x - (text_w / 2)
                
                # Box coords
                # Because we want lines to hug, maybe we standardize height based on line_height?
                # Let's align box vertically with the line slot
                
                box_x1 = text_x - padding_x
                box_y1 = current_y - padding_y
                box_x2 = text_x + text_w + padding_x
                box_y2 = current_y + line_height + padding_y # Use predictable line height for box
                # Maybe slightly reduce bottom padding or overlap?
                # Let's keep it simple: separate boxes that are close.
                
                try:
                    draw.rounded_rectangle(
                        [box_x1, box_y1, box_x2, box_y2],
                        radius=corner_radius,
                        fill=(255, 255, 255, 255)
                    )
                except AttributeError:
                    draw.rectangle(
                        [box_x1, box_y1, box_x2, box_y2],
                        fill=(255, 255, 255, 255)
                    )
                
                current_y += line_height + line_spacing

            # Second Pass: Draw Text (Black, Centered)
            current_y = start_y
            
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_w = bbox[2] - bbox[0]
                
                # Center text horizontally
                text_x = center_x - (text_w / 2)
                
                # Vertical alignment within the line slot
                # Pillow draws text from top-left baseline-ish. 
                # Let's use simple top alignment relative to our calculated slot.
                # Fine-tuning: add a small offset to visually center in the box height?
                text_y_offset = (line_height - (bbox[3]-bbox[1])) / 2
                draw.text((text_x, current_y + text_y_offset), line, font=font, fill=(0, 0, 0, 255))
                
                current_y += line_height + line_spacing
                
            img.save(output_image_path)
            return output_image_path
        except Exception as e:
            print(f"Intro overlay creation failed: {e}")
            return None

    def apply_intro_overlay(self, video_path, overlay_image_path, output_path, duration=6):
        """Overlay the intro image on video for the first N seconds."""
        try:
            # Create input streams
            video_input = ffmpeg.input(video_path)
            overlay_input = ffmpeg.input(overlay_image_path)
            
            # Apply overlay with enablement
            # Note: We must ensure we pick the video stream from the input
            # If the input has no audio, this might fail on audio map, but we assume input has audio.
            
            video_track = video_input.video.overlay(
                overlay_input, 
                x=0, 
                y=0, 
                enable=f'between(t,0,{duration})'
            )
            
            # Pass audio content through (re-encode to AAC to be safe/standard)
            audio_track = video_input.audio
            
            (
                ffmpeg
                .output(
                    video_track, 
                    audio_track, 
                    output_path, 
                    vcodec='libx264', 
                    acodec='aac'
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return output_path
        except ffmpeg.Error as e:
            print(f"Overlay application failed: {e.stderr.decode()}")
            return None

    def burn_subtitles(self, video_path, srt_path, output_path):
        """Burn subtitles (SRT or ASS) into video using proper path escaping."""
        try:
            abs_srt_path = os.path.abspath(srt_path)
            # PROPER WINDOWS PATH ESCAPING FOR FFMPEG FILTERS
            # 1. Replace backward slashes with forward slashes
            # 2. Escape the colon in drive letter
            # 3. Escape spaces even if quoted (safest for filter parser)
            
            # REVERTING TO SIMPLEST params:
            # vf="ass='C\:/Path/To/File.ass'"
            # But with escaping spaces?
            
            safe_srt_path = abs_srt_path.replace('\\', '/').replace(':', '\\\\:')
            
            # Escape single quotes in path if any
            safe_srt_path = safe_srt_path.replace("'", "'\\''") 
            
            # Use filter_name='path'
            # C\:/Users/DeeMindz/Documents/Social\ content\ automation/test_subs.ass
            
            safe_srt_path_no_quotes = abs_srt_path.replace('\\', '/').replace(':', '\\\\:').replace(' ', '\\\\ ').replace("'", "\\'")
            
            filter_name = 'ass' if srt_path.endswith('.ass') else 'subtitles'
            
            print(f"Debug: Burning subtitles using {filter_name} filter with safe path: {safe_srt_path_no_quotes}")
            
            # Construct complex filter argument
            # vf="ass='C\:/path/to/file.ass'"
            # ADDING fontsdir to ensure Montserrat is found
            # Syntax: ass=filename:fontsdir=directory
            
            project_root = os.getcwd()
            fonts_dir = os.path.join(project_root, 'assets', 'fonts').replace('\\', '/').replace(':', '\\\\:')
            
            vf_arg = f"{filter_name}={safe_srt_path_no_quotes}:fontsdir={fonts_dir}"
            
            print(f"Debug: Burning with filter: {vf_arg}")
            
            (
                ffmpeg
                .input(video_path)
                .output(output_path, vf=vf_arg)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return output_path
        except ffmpeg.Error as e:
            print(f"Subtitle burn failed (FFmpeg): {e.stderr.decode()}")
            return None
        except Exception as e:
            print(f"Subtitle burn unexpected error: {e}")
            return None
