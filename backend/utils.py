def format_timestamp(seconds):
    if seconds is None:
        return "00:00:00,000"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(chunks, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        prev_end = 0.0
        subtitle_index = 1

        for chunk in chunks:
            text = chunk.get("text", "").strip()
            if not text:
                continue

            timestamps = chunk.get("timestamp", (None, None))
            if isinstance(timestamps, (list, tuple)) and len(timestamps) == 2:
                start, end = timestamps
            else:
                start, end = None, None

            if start is None:
                start = prev_end

            if end is None:
                end = start + 2.0

            if end < start:
                end = start + 2.0

            prev_end = end

            f.write(f"{subtitle_index}\n")
            f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            f.write(f"{text}\n\n")

            subtitle_index += 1
