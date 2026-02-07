def format_ass_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds % 1) * 100)) % 100
    return f"{hours}:{minutes:02}:{secs:02}.{centis:02}"

def json_to_ass_modern(whisper_json):
    """
    Convert Whisper segments to modern TikTok-style ASS subtitles.
    Shows 3-5 words at a time with key words highlighted in yellow.
    """
    if not whisper_json: 
        print("Debug: json_to_ass_modern received None")
        return ""
    
    def get_val(obj, key):
        if isinstance(obj, dict): return obj.get(key)
        return getattr(obj, key, None)

    # Safely get segments and words list
    segments = get_val(whisper_json, 'segments') or []
    words_data = get_val(whisper_json, 'words') or []

    print(f"Debug: json_to_ass_modern found {len(segments)} segments and {len(words_data)} words")
    
    if not segments and not words_data:
        print("Debug: json_to_ass_modern both segments and words are empty")
        return ""

    # ASS Header with modern styling
    ass_content = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1920",  # Targeting vertical video ref width
        "PlayResY: 1080",  # But wait, usually PlayResY should be height? 
                           # Actually for 9:16 video: 1080x1920. 
                           # To be safe for mixed content, let's stick to standard 1080p ref and let scales handle it? 
                           # No, user wants PERFECT. 
                           # Let's set PlayResY=1920 (likely 1080x1920 content).
        "PlayResY: 1920", 
        "PlayResX: 1080",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        # White text with thin black outline (Outline=2)
        "Style: Default,Impact,90,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,0,2,50,50,200,1",
        # Yellow highlight with thin black outline (Outline=2)
        "Style: Highlight,Impact,90,&H0000FFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,105,105,0,0,1,3,0,2,50,50,200,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]

    header_length = len(ass_content)

    if words_data:
        # Group words into chunks of 3-5 words
        chunk_size = 4
        for i in range(0, len(words_data), chunk_size):
            chunk = words_data[i:i + chunk_size]
            if not chunk: continue
            
            try:
                start_val = get_val(chunk[0], 'start')
                end_val = get_val(chunk[-1], 'end')
                text_list = [get_val(w, 'word') for w in chunk]
                
                if start_val is None or end_val is None: continue

                # DO NOT FORCE START TO 0.00 artificially. 
                # Start time must be respected for sync.
                
                start_str = format_ass_timestamp(start_val)
                end_str = format_ass_timestamp(end_val)
                
                line_text = " ".join([word.strip().upper() for word in text_list if word])
                if line_text:
                    ass_content.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{line_text}")
            except Exception as e:
                print(f"Error grouping words: {e}")
                continue
    else:
        # Fallback to segment-level if words are missing
        for segment in segments:
            try:
                start_val = get_val(segment, 'start')
                end_val = get_val(segment, 'end')
                text_val = get_val(segment, 'text')
                
                if start_val is None or end_val is None or text_val is None: continue

                words = text_val.strip().split()
                if not words: continue
                
                chunk_size = 4
                for i in range(0, len(words), chunk_size):
                    chunk_words = words[i:i + chunk_size]
                    
                    # Interpolate accurate timing within the segment 
                    # This helps sync when word-level timestamps aren't available
                    duration = end_val - start_val
                    word_duration = duration / len(words)
                    
                    chunk_start_idx = i
                    chunk_end_idx = min(len(words), i + chunk_size)
                    
                    chunk_num_words = chunk_end_idx - chunk_start_idx
                    
                    chunk_start = start_val + (chunk_start_idx * word_duration)
                    chunk_end = start_val + (chunk_end_idx * word_duration)
                    
                    start_str = format_ass_timestamp(chunk_start)
                    end_str = format_ass_timestamp(chunk_end)
                    
                    line_text = " ".join([word.upper() for word in chunk_words])
                    if line_text:
                        ass_content.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{line_text}")
            except Exception as e:
                print(f"Error processing segment: {e}")
                continue

    print(f"Debug: json_to_ass_modern generated {len(ass_content) - header_length} subtitle lines")
    return "\n".join(ass_content)

def json_to_ass_karaoke(whisper_json):
    """
    Generate ASS subtitles with Karaoke effect (moving highlight) using \k tags.
    """
    if not whisper_json: return ""

    def get_val(obj, key):
        if isinstance(obj, dict): return obj.get(key)
        return getattr(obj, key, None)

    # 1. Extract all words flatly
    all_words = []
    
    # Try getting 'words' directly (verbose_json)
    words_data = get_val(whisper_json, 'words')
    if words_data:
        all_words = words_data
    else:
        # Fallback: extract from segments if they have 'words'
        segments = get_val(whisper_json, 'segments') or []
        for seg in segments:
            seg_words = get_val(seg, 'words')
            if seg_words:
                all_words.extend(seg_words)
            else:
                # Worst case: split text and interpolate (less accurate)
                # For now let's skip interpolation fallback in karaoke mode to keep it simple,
                # or better: rely on json_to_ass_modern if no word timestamps found?
                pass
    
    if not all_words:
        print("Warning: No word-level timestamps found for Karaoke. Falling back to standard.")
        return json_to_ass_modern(whisper_json)

    # 2. ASS Header
    ass_content = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080", 
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        # Karaoke Style: 
        # Primary (Filled/Sung) = Yellow (&H0000FFFF)
        # Secondary (Unfilled) = White (&H00FFFFFF)
        # Outline = Black (&H00000000)
        "Style: Karaoke,Impact,100,&H0000FFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,0,2,10,10,200,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]

    # 3. Group into lines
    chunk_size = 4 # words per line
    
    for i in range(0, len(all_words), chunk_size):
        chunk = all_words[i:i + chunk_size]
        if not chunk: continue
        
        try:
            # Calculate line start/end
            start_obj = chunk[0]
            end_obj = chunk[-1]
            
            line_start_s = get_val(start_obj, 'start')
            line_end_s = get_val(end_obj, 'end')
            
            if line_start_s is None or line_end_s is None: continue
            
            start_timestamp = format_ass_timestamp(line_start_s)
            end_timestamp = format_ass_timestamp(line_end_s)
            
            # Build Karaoke String
            # {\k10}Word {\k20}Word
            k_text = ""
            current_time = line_start_s
            
            for w in chunk:
                w_start = get_val(w, 'start')
                w_end = get_val(w, 'end')
                w_word = get_val(w, 'word').strip().upper()
                
                # Check for gap before word
                gap = w_start - current_time
                if gap > 0.05: # 50ms tolerance
                    gap_cs = int(gap * 100)
                    k_text += fr"{{\k{gap_cs}}}" 
                    current_time += gap
                
                # Word duration
                dur = w_end - current_time
                dur_cs = int(dur * 100)
                if dur_cs < 1: dur_cs = 1 # Minimum 1cs
                
                k_text += fr"{{\k{dur_cs}}}{w_word} "
                current_time = w_end
            
            ass_content.append(f"Dialogue: 0,{start_timestamp},{end_timestamp},Karaoke,,0,0,0,,{k_text}")
            
        except Exception as e:
            print(f"Error processing karaoke chunk: {e}")
            continue

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
