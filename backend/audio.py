import os
import subprocess


def extract_audio(input_file):
    ext = input_file.split(".")[-1].lower()
    if ext in ["wav", "mp3", "m4a", "flac"]:
        return input_file

    print("Video detected. Extracting audio using ffmpeg...")
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_audio = f"{base_name}_temp.wav"

    subprocess.run(
        [
            "ffmpeg",
            "-i",
            input_file,
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            output_audio,
            "-y",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return output_audio
