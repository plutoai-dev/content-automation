import os
import subprocess
import ffmpeg
from PIL import Image, ImageDraw, ImageFont

class RenderService:
    def __init__(self):
        # Ensure ffmpeg is in path or define path here
        pass

    def extract_first_frame(self, video_path, output_image_path):
        """Extract the first frame of the video."""
        try:
            (
                ffmpeg
                .input(video_path)
                .filter('select', 'gte(n,0)')
                .output(output_image_path, vframes=1)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return output_image_path
        except ffmpeg.Error as e:
            print(f"Frame extraction failed: {e.stderr.decode()}")
            return None

    def create_intro_video(self, image_path, title_text, output_video_path, duration=6):
        """
        Create a 6s static video from image with title using Pillow for text
        and FFmpeg for video generation.
        """
        try:
            # 1. Overlay Text using Pillow
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            W, H = img.size
            
            # Calculate adaptive font size based on image dimensions
            # For portrait videos (9:16), use larger font
            is_portrait = H > W
            base_font_size = 200 if is_portrait else 160
            
            # Use Impact font (same as subtitles) but MUCH BIGGER for title
            try:
                # Try Impact font - the bold, chunky font used in viral videos
                font = ImageFont.truetype("impact.ttf", base_font_size)
            except:
                try:
                    # Fallback to Arial Bold
                    font = ImageFont.truetype("arialbd.ttf", base_font_size)
                except:
                    try:
                        font = ImageFont.truetype("arial.ttf", base_font_size)
                    except:
                        font = ImageFont.load_default()

            # Text wrapping for long titles
            max_width = int(W * 0.85)  # Use 85% of width for better margins
            
            # Split title into lines if too long
            words = title_text.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                line_width = bbox[2] - bbox[0]
                
                if line_width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Calculate total text height with generous line spacing
            line_height = int(base_font_size * 1.2)  # 120% of font size for line height
            total_text_height = len(lines) * line_height
            
            # Darken the image with a semi-transparent overlay for better text visibility
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([0, 0, W, H], fill=(0, 0, 0, 210))  # VERY dark overlay (82% opacity)
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGBA')
            draw = ImageDraw.Draw(img)
            
            # Calculate starting Y position to center text vertically
            y_offset = (H - total_text_height) / 2
            
            # Draw each line of text centered with keyword highlighting
            for line in lines:
                words = line.split()
                
                # Calculate total line width for centering
                word_widths = [draw.textbbox((0, 0), word, font=font)[2] - draw.textbbox((0, 0), word, font=font)[0] for word in words]
                total_line_width = sum(word_widths) + (len(words) - 1) * 30  # Add spacing between words
                
                # Start position for this line
                current_x = (W - total_line_width) / 2
                
                for i, word in enumerate(words):
                    # Determine if this word should be highlighted (more selective)
                    is_important = (
                        (len(word) > 6) or      # Significant long words
                        (word.isupper() and len(word) > 1)  # Intentional ALL CAPS emphasis
                    )
                    
                    # Choose color - clean text without outline
                    text_color = (255, 255, 0, 255) if is_important else (255, 255, 255, 255)  # Yellow or White (RGBA)
                    
                    # Draw text directly on darkened background
                    draw.text((current_x, y_offset), word, font=font, fill=text_color)
                    
                    # Move to next word position
                    word_width = word_widths[i]
                    current_x += word_width + 30  # Add spacing
                
                y_offset += line_height
            
            titled_image_path = image_path.replace(".png", "_titled.png")
            img.convert('RGB').save(titled_image_path)

            # 2. Convert to Video (Loop) + Add Silent Audio
            # Using subprocess for better control over filter_complex
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1', '-t', str(duration), '-i', titled_image_path,
                '-f', 'lavfi', '-t', str(duration), '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac',
                '-shortest',
                output_video_path
            ]
            result = subprocess.run(cmd, capture_output=True, check=True)
            return output_video_path
        except Exception as e:
            print(f"Intro creation failed: {e}")
            if hasattr(e, 'stderr'): print(e.stderr.decode())
            return None

    def burn_subtitles(self, video_path, srt_path, output_path):
        """Burn subtitles (SRT or ASS) into video."""
        try:
            abs_srt_path = os.path.abspath(srt_path)
            # Use 'ass' filter for .ass files, 'subtitles' for .srt
            filter_name = 'ass' if srt_path.endswith('.ass') else 'subtitles'
            
            safe_srt_path = abs_srt_path.replace('\\', '/').replace(':', '\\:')
            
            print(f"Debug: Burning subtitles using {filter_name} filter with path: {safe_srt_path}")
            
            (
                ffmpeg
                .input(video_path)
                .output(output_path, vf=f"{filter_name}='{safe_srt_path}'")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return output_path
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode()
            print(f"Subtitle burn failed: {error_msg}")
            return None
        except Exception as e:
            print(f"Subtitle burn unexpected error: {e}")
            return None

    def merge_videos(self, intro_path, content_path, output_path):
        """Merge intro + content using filter_complex for robust audio handling."""
        try:
            print(f"Merging {intro_path} and {content_path}...")
            # Ensure both files exist
            if not os.path.exists(intro_path):
                print(f"Merge error: Intro path missing: {intro_path}")
                return None
            if not os.path.exists(content_path):
                print(f"Merge error: Content path missing: {content_path}")
                return None

            # Use subprocess for reliable merging with concat filter
            cmd = [
                'ffmpeg', '-y',
                '-i', intro_path,
                '-i', content_path,
                '-filter_complex', '[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]',
                '-map', '[v]',
                '-map', '[a]',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                output_path
            ]
            result = subprocess.run(cmd, capture_output=True, check=True)
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"Merge failed (FFmpeg Error): {e.stderr.decode()}")
            return None
        except Exception as e:
            print(f"Merge failed (Unexpected Error): {e}")
            return None
