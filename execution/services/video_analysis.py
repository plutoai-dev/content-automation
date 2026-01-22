import ffmpeg
import json

class VideoAnalyzer:
    @staticmethod
    def get_metadata(file_path):
        """Extract metadata from video file."""
        try:
            probe = ffmpeg.probe(file_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            
            if not video_stream:
                return None
                
            width = int(video_stream['width'])
            height = int(video_stream['height'])
            duration = float(video_stream['duration'])
            
            # Determine orientation
            orientation = "landscape" if width >= height else "portrait"
            
            # Determine length category
            length_category = "short" if duration <= 180 else "long"
            
            return {
                "width": width,
                "height": height,
                "duration": duration,
                "orientation": orientation,
                "length_category": length_category
            }
        except Exception as e:
            print(f"Error checking video metadata: {e}")
            return None
