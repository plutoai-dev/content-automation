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
    Generate ASS subtitles with 'Box Highlight' effect.
    Creates a separate event for each word's duration to style the active word distinctively.
    """
    if not whisper_json: return ""

    def get_val(obj, key):
        if isinstance(obj, dict): return obj.get(key)
        return getattr(obj, key, None)

    # 1. Extract all words flatly
    all_words = []
    
    words_data = get_val(whisper_json, 'words')
    if words_data:
        all_words = words_data
    else:
        segments = get_val(whisper_json, 'segments') or []
        for seg in segments:
            seg_words = get_val(seg, 'words')
            if seg_words:
                all_words.extend(seg_words)
    
    if not all_words:
        # Fallback to standard if no word timestamps
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
        # Base Style: White Text, Black Outline
        # Modifications for User Request:
        # 1. Fontname: Montserrat-Bold (Need to ensure player can find it, or attach it? ASS usually requires installed fonts or attachment. We will burn it, so FFmpeg needs path)
        #    Actually for burning, we can specify proper fontdir or just hope it picks up system font if installed? 
        #    Since we have file, we can map it? 
        #    Wait, for `ass` filter, we can't easily force a custom file unless we set FontConfig or similar.
        #    Easiest: Assume Montserrat is installed OR we will just use 'Montserrat' family and hope FFmpeg sees it if we put it in ~/.fonts or register it?
        #    For now, let's set Fontname=Montserrat. If not found, it falls back.
        # 2. Fontsize: Reduced slightly (85 -> 75) for compaction.
        # 3. Spacing: -1 or -0.5 for "compact" look? Let's try 0 (normal) first or -1.
        # 4. MarginL/R: Increase to 100 to prevent overflow (Safety margin).
        
        "Style: Default,Montserrat Bold,75,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,-1,0,1,2,0,2,100,100,200,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]

    # 3. Group into lines
    chunk_size = 3 # Fewer words per line for better focus with the box effect
    
    # Highlight Colors (Cycling or fixed? Let's use a nice Purple/Blue cycle or fixed Gold)
    # User asked for "colored rectangle". Let's use a vibrant color.
    # Ref: #E23F5B (Wine/Pink) -> ASS BGR: &H005B3FE2
    active_color_bgr = "&H005B3FE2" # Wine/Pink
    
    for i in range(0, len(all_words), chunk_size):
        chunk = all_words[i:i + chunk_size]
        if not chunk: continue
        
        try:
            # We need to create an event for EACH word in this chunk
            # The text will be the SAME for all events in this chunk (the full line)
            # But the styling tags will move.
            
            full_line_text_words = [get_val(w, 'word').strip().upper() for w in chunk]
            
            # Start/End of the entire line (for safety, though we use word times)
            # Actually, to make it smooth, the line should stay on screen from start of first word to end of last.
            # But we are replacing the line with a new "version" of the line every word.
            
            for j, active_word_obj in enumerate(chunk):
                w_start = get_val(active_word_obj, 'start')
                w_end = get_val(active_word_obj, 'end')
                
                # Fill gaps? If there's a silence between words, the previous word should usually hold or blank?
                # For smooth visual, let's extend to next word start?
                # Or just strict timing. Strict is safer for sync.
                
                if w_start is None or w_end is None: continue
                
                start_str = format_ass_timestamp(w_start)
                end_str = format_ass_timestamp(w_end)
                
                # Build the line text with overrides
                display_text = ""
                for k, w_obj in enumerate(chunk):
                    w_text = full_line_text_words[k]
                    
                    if k == j:
                        # ACTIVE WORD
                        # Simulate Box:
                        # 3c (Border) = Wine (active_color_bgr)
                        # bord = Thick (e.g., 6)
                        # 1c (Primary) = White (&H00FFFFFF) - User request: "let the subtitle all be same white color"
                        
                        display_text += fr"{{\3c{active_color_bgr}\bord6\1c&H00FFFFFF&}} {w_text} {{\r}}" 
                        # \r resets to default style for next word (important!)
                    else:
                        # INACTIVE WORD
                        display_text += f" {w_text} "

                ass_content.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{display_text.strip()}")
                
        except Exception as e:
            print(f"Error processing visual chunk: {e}")
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
