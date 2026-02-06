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
            
            # MASSIVE TITLES: Use 8% of height for portrait, 6% for landscape
            # Reduced to fit within center third of screen (TikTok style)
            is_portrait = H > W
            base_font_size = int(H * 0.08) if is_portrait else int(H * 0.06)
            
            # Use Impact font - the bold, chunky font used in viral videos
            font = None
            try:
                # Try finding Impact in standard Windows location
                font = ImageFont.truetype("C:\\Windows\\Fonts\\impact.ttf", base_font_size)
            except:
                try:
                    font = ImageFont.truetype("impact.ttf", base_font_size)
                except:
                    try:
                        # Try Linux standard fonts (Debian/Ubuntu/CloudRun)
                        # fonts-liberation package provides this
                        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", base_font_size)
                    except:
                        try:
                            # Fallback to DejaVu if available
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", base_font_size)
                        except:
                            try:
                                font = ImageFont.truetype("arialbd.ttf", base_font_size)
                            except:
                                print(f"⚠️ Warning: Could not load any requested font. Using default (tiny).")
                                font = ImageFont.load_default()

            # Text wrapping for massive titles
            # Since font is huge, we need to be careful with width
            max_width = int(W * 0.90)  # 5% margin on each side
            
            # 1. Parse keywords (words wrapped in *)
            # We need to preserve the "is_highlighted" state for each word
            words_raw = title_text.split()
            words_struct = [] # List of {'text': word, 'highlight': bool}
            
            for w in words_raw:
                # Check for *word* or *word
                # Simple logic: if * is present, treat as highlight and strip it
                if '*' in w:
                    clean_w = w.replace('*', '')
                    words_struct.append({'text': clean_w, 'highlight': True})
                else:
                    words_struct.append({'text': w, 'highlight': False})

            # 2. Wrap text into lines
            lines = [] # List of lists of word_structs
            current_line = []
                                    
            for w_struct in words_struct:
                # Test with space
                test_line_words = [ws['text'] for ws in current_line] + [w_struct['text']]
                test_line_str = ' '.join(test_line_words)
                
                bbox = draw.textbbox((0, 0), test_line_str, font=font)
                line_width = bbox[2] - bbox[0]
                
                if line_width <= max_width:
                    current_line.append(w_struct)
                else:
                    if current_line:
                        lines.append(current_line)
                        current_line = [w_struct]
                    else:
                        # Word is wider than screen, force split (rare)
                        lines.append([w_struct])
                        current_line = []
            
            if current_line:
                lines.append(current_line)
            
            # Calculate total text height with tight line spacing for impact
            line_height = int(base_font_size * 1.1)
            total_text_height = len(lines) * line_height
            
            # Darken the image significantly for contrast
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([0, 0, W, H], fill=(0, 0, 0, 180))  # 70% opacity black
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGBA')
            draw = ImageDraw.Draw(img)
            
            # Calculate starting Y position to center text vertically
            y_offset = (H - total_text_height) / 2
            
            space_bbox = draw.textbbox((0, 0), " ", font=font)
            space_width = space_bbox[2] - space_bbox[0]

            # Draw each line of text centered
            for line_words in lines:
                # Calculate total width of this line to center it
                full_line_text = ' '.join([ws['text'] for ws in line_words])
                bbox = draw.textbbox((0, 0), full_line_text, font=font)
                line_pixel_width = bbox[2] - bbox[0]
                
                current_x = (W - line_pixel_width) / 2
                
                # Draw words one by one
                for i, w_struct in enumerate(line_words):
                    word_text = w_struct['text']
                    
                    # Colors
                    text_color = (255, 255, 0, 255) if w_struct['highlight'] else (255, 255, 255, 255) # Yellow or White
                    stroke_color = (0, 0, 0, 255)
                    outline_width = int(base_font_size * 0.03)

                    draw.text(
                        (current_x, y_offset), 
                        word_text, 
                        font=font, 
                        fill=text_color,
                        stroke_width=outline_width,
                        stroke_fill=stroke_color
                    )
                    
                    # Advance X
                    w_bbox = draw.textbbox((0, 0), word_text, font=font)
                    w_width = w_bbox[2] - w_bbox[0]
                    current_x += w_width
                    
                    # Add space if not last word
                    if i < len(line_words) - 1:
                        current_x += space_width
                
                y_offset += line_height
            
            titled_image_path = image_path.replace(".png", "_titled.png")
            img.convert('RGB').save(titled_image_path)

            # 2. Convert to Video (Loop) + Add Silent Audio
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
        """Burn subtitles (SRT or ASS) into video using proper path escaping."""
        try:
            abs_srt_path = os.path.abspath(srt_path)
            # PROPER WINDOWS PATH ESCAPING FOR FFMPEG FILTERS
            # 1. Replace backward slashes with forward slashes
            # 2. Escape the colon in drive letter
            # 3. Escape spaces even if quoted (safest for filter parser)
            safe_srt_path = abs_srt_path.replace('\\', '/').replace(':', '\\\\:')
            # safe_srt_path = safe_srt_path.replace(' ', '\\ ') # Try without first if using quotes? No, already failed.
            
            # Actually, let's look at the error again. "Unable to parse original_size".
            # This happens when it thinks the next token is original_size but it isn't?
            # Or it's trying to interpret the path as parameters.
            
            # TRY: Relative path if possible? 
            # No, let's try escaping ' ' -> '\ ' 
            # And REMOVE quotes if I escape spaces?
            # Or keep quotes.
            
            # Let's try minimal request: Just the path, forward slashes, escaped colon.
            # And using os.path.normpath?
            
            # Let's try this:
            # 1. Forward slashes.
            # 2. handle drive letter C: -> /c/ or something? No, ffmpeg expects C:
            # 3. Quote the whole thing.
            
            # REVERTING TO SIMPLEST params:
            # vf="ass='C\:/Path/To/File.ass'"
            # But with escaping spaces?
            
            safe_srt_path = abs_srt_path.replace('\\', '/').replace(':', '\\\\:')
            
            # Escape single quotes in path if any
            safe_srt_path = safe_srt_path.replace("'", "'\\''") 
            
            # Use filter_name='path'
            # But I'll try to use the raw string directly without `filename=` key (it was breaking before with implicit key too).
            
            # CRITICAL: If I use subprocess directly I control the list.
            # output_path, vf=...
            
            # Let's try escaping spaces.
            # safe_srt_path = safe_srt_path.replace(' ', '\\\\\\ ') # Escape for shell AND filter?
            
            # OK, let's try a different approach.
            # Change directory to the subtitle location during execution? No.
            
            # Let's try escaping space with a single backslash inside the quote?
            # No, '...' treats \ as literal mostly.
            
            # Let's try WITHOUT quotes, but heavily escaped.
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
