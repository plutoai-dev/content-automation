import os
from openai import OpenAI
import anthropic
import json

class AIService:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    def transcribe_audio(self, file_path):
        """Transcribe audio using Whisper. Extracts audio first to bypass 25MB limit."""
        temp_audio = f"temp_audio_{os.path.basename(file_path)}.mp3"
        try:
            # Extract audio using FFmpeg
            import subprocess
            cmd = [
                'ffmpeg', '-y', '-i', file_path, 
                '-vn', '-ar', '16000', '-ac', '1', '-ab', '128k', '-f', 'mp3', 
                temp_audio
            ]
            subprocess.run(cmd, capture_output=True, check=True)

            with open(temp_audio, "rb") as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
            
            # Cleanup
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
                
            # Convert Transcription object to dict for robust serialization/processing
            return transcript.model_dump() if hasattr(transcript, 'model_dump') else transcript
        except Exception as e:
            print(f"Transcription failed: {e}")
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            return None

    def generate_content_strategy(self, transcript_text, duration_checks):
        """Generate titles, captions, etc. using Claude."""
        
        prompt = f"""
        Video Context:
        Transcript: {transcript_text[:4000]}... (truncated)
        Duration Category: {duration_checks['length_category']}
        Orientation: {duration_checks['orientation']}

        Task: Generate social media content.
        Output JSON with keys: 'title', 'caption', 'hashtags', 'linkedin_post' (if landscape/long), 'tiktok_caption' (if portrait).
        
        IMPORTANT: For the 'title', wrap 1-2 most important "impact" keywords in asterisks (*) for highlighting. 
        Example: "Watch This *INSANE* Trick" or "How to *FIX* Your *SLEEP*"
        """
        
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.7,
                system="You are a social media expert. Output ONLY valid raw JSON.",
                messages=[{"role": "user", "content": prompt}]
            )
            
            raw_text = message.content[0].text
            # Simple cleanup in case of markdown blocks
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0]
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0]
                
            return json.loads(raw_text.strip())
        except Exception as e:
            print(f"Content generation failed: {e}")
            return {}
