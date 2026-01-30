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
        # White text with thin black outline (Outline=2)
        "Style: Default,Impact,90,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,2,50,50,200,1",
        # Yellow highlight with thin black outline (Outline=2)
        "Style: Highlight,Impact,90,&H0000FFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,105,105,0,0,1,2,0,2,50,50,200,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]

    # Prefer word-level timestamps for perfect sync
    words_data = []
    if hasattr(whisper_json, 'words') and whisper_json.words:
        words_data = whisper_json.words
    elif isinstance(whisper_json, dict) and whisper_json.get('words'):
        words_data = whisper_json.get('words')
    
    if words_data:
        print(f"Debug: json_to_ass_modern using {len(words_data)} words")
        # Group words into chunks of 3-5 words
        chunk_size = 4
        for i in range(0, len(words_data), chunk_size):
            chunk = words_data[i:i + chunk_size]
            
            # Start time is exactly when the first word of the chunk starts
            # End time is when the last word of the chunk ends
            try:
                start_val = chunk[0].get('start') if isinstance(chunk[0], dict) else chunk[0].start
                end_val = chunk[-1].get('end') if isinstance(chunk[-1], dict) else chunk[-1].end
                text_list = [w.get('word') if isinstance(w, dict) else w.word for w in chunk]
            except:
                continue

            start_str = format_ass_timestamp(start_val)
            end_str = format_ass_timestamp(end_val)
            
            line_text = " ".join([word.strip().upper() for word in text_list])
            ass_content.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{line_text}")
    else:
        # Fallback to segment-level if words are missing
        print("Debug: json_to_ass_modern falling back to segments")
        for segment in segments:
            try:
                start_val = segment.get('start') if isinstance(segment, dict) else segment.start
                end_val = segment.get('end') if isinstance(segment, dict) else segment.end
                text_val = segment.get('text') if isinstance(segment, dict) else segment.text
            except:
                continue

            words = text_val.strip().split()
            chunk_size = 4
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i + chunk_size]
                chunk_duration = (end_val - start_val) / max(1, len(words) / chunk_size)
                chunk_start = start_val + (i / len(words)) * (end_val - start_val)
                chunk_end = min(chunk_start + chunk_duration, end_val)
                
                start_str = format_ass_timestamp(chunk_start)
                end_str = format_ass_timestamp(chunk_end)
                
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
