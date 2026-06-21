def format_timestamp(seconds):
    if seconds is None:
        return "00:00:00,000"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def split_into_subtitles(chunk, max_words=4):
    text = chunk.get("text", "").strip()
    if not text:
        return []

    timestamps = chunk.get("timestamp", (None, None))
    if isinstance(timestamps, (list, tuple)) and len(timestamps) == 2:
        start, end = timestamps
    else:
        start, end = None, None

    if start is None or end is None:
        return [chunk]

    words = text.split()
    total_words = len(words)

    if total_words <= max_words and not any(w[-1] in ".,?!" for w in words[:-1]):
        return [chunk]

    duration = end - start
    time_per_word = duration / total_words if total_words > 0 else 0

    subtitles = []
    current_words = []
    current_start = start

    for i, word in enumerate(words):
        current_words.append(word)

        is_punctuation = word[-1] in ".,?!"

        if len(current_words) >= max_words or is_punctuation or i == total_words - 1:
            group_text = " ".join(current_words)
            words_processed = i + 1
            group_end = start + (words_processed * time_per_word)

            if group_end > end or i == total_words - 1:
                group_end = end

            subtitles.append(
                {"text": group_text, "timestamp": (current_start, group_end)}
            )

            current_start = group_end
            current_words = []

    return subtitles


def generate_srt(chunks, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        prev_end = 0.0
        subtitle_index = 1

        for original_chunk in chunks:
            text = original_chunk.get("text", "").strip()
            if not text:
                continue

            # 1. Resolve missing timestamps BEFORE splitting
            timestamps = original_chunk.get("timestamp", (None, None))
            if isinstance(timestamps, (list, tuple)) and len(timestamps) == 2:
                start, end = timestamps
            else:
                start, end = None, None

            if start is None:
                start = prev_end

            words_len = len(text.split())

            if end is None:
                # Estimate duration if missing (~0.33 seconds per word)
                end = start + max(2.0, words_len * 0.33)

            if end < start:
                end = start + max(2.0, words_len * 0.33)

            prev_end = end

            # Update the original chunk with resolved timestamps
            original_chunk["timestamp"] = (start, end)

            # 2. Split the resolved chunk
            split_chunks = split_into_subtitles(original_chunk, max_words=4)

            for chunk in split_chunks:
                chunk_text = chunk.get("text", "").strip()
                if not chunk_text:
                    continue

                chunk_start, chunk_end = chunk.get("timestamp", (start, end))

                f.write(f"{subtitle_index}\n")
                f.write(
                    f"{format_timestamp(chunk_start)} --> {format_timestamp(chunk_end)}\n"
                )
                f.write(f"{chunk_text.upper()}\n\n")

                subtitle_index += 1
