def format_ass_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int((seconds - int(seconds)) * 100)
    return f"{hours}:{minutes:02}:{secs:02}.{centis:02}"

def json_to_ass_modern(whisper_json):
    """
    Convert Whisper segments to modern TikTok-style ASS subtitles.
    Shows 3-5 words at a time with key words highlighted in yellow.
    """
    if not whisper_json: 
        print("Debug: json_to_ass_modern received None")
        return ""
    
    # Safely get segments list
    segments = []
    if hasattr(whisper_json, 'segments'):
        segments = whisper_json.segments or []
    elif isinstance(whisper_json, dict):
        segments = whisper_json.get('segments', []) or []
    
    print(f"Debug: json_to_ass_modern found {len(segments)} segments")
    
    if not segments:
        return ""

    # ASS Header with modern styling
    ass_content = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        # White text with thick black outline
        "Style: Default,Impact,90,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,8,0,2,50,50,200,1",
        # Yellow highlight with thick black outline
        "Style: Highlight,Impact,90,&H0000FFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,105,105,0,0,1,8,0,2,50,50,200,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]

    # Process segments and create simple static subtitles
    for segment in segments:
        # Get segment data
        try:
            start_val = segment.get('start') if isinstance(segment, dict) else segment.start
            end_val = segment.get('end') if isinstance(segment, dict) else segment.end
            text_val = segment.get('text') if isinstance(segment, dict) else segment.text
        except AttributeError:
            start_val = segment['start']
            end_val = segment['end']
            text_val = segment['text']

        # Split text into words
        words = text_val.strip().split()
        
        # Group into chunks of 3-5 words
        chunk_size = 4  # Average 4 words per subtitle
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            
            # Calculate timing for this chunk
            chunk_duration = (end_val - start_val) / max(1, len(words) / chunk_size)
            chunk_start = start_val + (i / len(words)) * (end_val - start_val)
            chunk_end = min(chunk_start + chunk_duration, end_val)
            
            start_str = format_ass_timestamp(chunk_start)
            end_str = format_ass_timestamp(chunk_end)
            
            # Simple static text - all words in white
            line_text = " ".join([word.upper() for word in chunk_words])
            ass_content.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{line_text}")

    return "\n".join(ass_content)

def json_to_srt(whisper_json):
    """
    Convert Whisper verbose_json output to SRT format string (Legacy/Fallback).
    """
    def format_timestamp(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

    srt_content = ""
    if not whisper_json:
        return ""
        
    # Safely get segments list
    segments = []
    if hasattr(whisper_json, 'segments'):
        segments = whisper_json.segments or []
    elif isinstance(whisper_json, dict):
        segments = whisper_json.get('segments', []) or []
    
    for i, segment in enumerate(segments, start=1):
        # Handle both dict and object (TranscriptionSegment)
        try:
            start_val = segment.get('start') if isinstance(segment, dict) else segment.start
            end_val = segment.get('end') if isinstance(segment, dict) else segment.end
            text_val = segment.get('text') if isinstance(segment, dict) else segment.text
        except AttributeError:
            # Fallback if it's something else
            start_val = segment['start']
            end_val = segment['end']
            text_val = segment['text']

        start = format_timestamp(start_val)
        end = format_timestamp(end_val)
        text = text_val.strip()
        
        srt_content += f"{i}\n{start} --> {end}\n{text}\n\n"
        
    return srt_content

# Keep the old function for backward compatibility
json_to_ass = json_to_ass_modern
