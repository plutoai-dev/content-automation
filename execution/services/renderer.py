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
            
            # Font setup (reuse logic from before but simpler)
            is_portrait = height > width
            # REDUCED SIZE: 5% for portrait, 4% for landscape (was 8%/6%)
            base_font_size = int(height * 0.05) if is_portrait else int(height * 0.04)
            
            font = None
            try:
                font = ImageFont.truetype("C:\\Windows\\Fonts\\impact.ttf", base_font_size)
            except:
                try:
                    font = ImageFont.truetype("impact.ttf", base_font_size)
                except:
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", base_font_size)
                    except:
                        try:
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", base_font_size)
                        except:
                            font = ImageFont.load_default()

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
                
            # Rendering Lines - GROUPED BACKGROUND STYLE
            if not lines:
                return None

            # 1. Calculate dimensions
            line_height = int(base_font_size * 1.2)
            # Add small spacing between lines, but they are in one group
            line_spacing = 10 
            total_text_height = (len(lines) * line_height) + ((len(lines) - 1) * line_spacing)
            
            max_line_width = 0
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                w = bbox[2] - bbox[0]
                if w > max_line_width:
                    max_line_width = w
            
            # 2. Define Box Dimensions
            padding_x = 40
            padding_y = 30
            
            box_width = max_line_width + (padding_x * 2)
            box_height = total_text_height + (padding_y * 2)
            
            # 3. Center Box on Screen
            center_x = width / 2
            center_y = height / 2
            
            box_x1 = center_x - (box_width / 2)
            box_y1 = center_y - (box_height / 2)
            box_x2 = box_x1 + box_width
            box_y2 = box_y1 + box_height
            
            corner_radius = 20
            
            # 4. Draw Single Grouped Background
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
            
            # 5. Draw Text Lines
            # Text starts at box_y1 + padding_y
            current_y = box_y1 + padding_y
            
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_w = bbox[2] - bbox[0]
                
                # Center text horizontally within the box (and thus screen)
                text_x = center_x - (text_w / 2)
                
                draw.text((text_x, current_y), line, font=font, fill=(0, 0, 0, 255))
                
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
            vf_arg = f"{filter_name}={safe_srt_path_no_quotes}"
            
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
