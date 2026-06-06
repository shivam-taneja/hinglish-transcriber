#!/usr/bin/env python3
import argparse
import os
import subprocess
import torch
from transformers import pipeline


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
        for i, chunk in enumerate(chunks, start=1):
            start, end = chunk["timestamp"]

            if end is None:
                end = start + 2.0

            f.write(f"{i}\n")
            f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            f.write(f"{chunk['text'].strip()}\n\n")


def main():
    parser = argparse.ArgumentParser(description="Transcribe Audio/Video to Hinglish")
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input audio/video file"
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        help="Path to output SRT file (defaults to same name as input with .srt extension)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' not found.")
        return

    if args.output is None:
        base_name = os.path.splitext(args.input)[0]
        args.output = f"{base_name}.srt"

    audio_path = extract_audio(args.input)

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Loading Oriserve model locally on hardware: {device.upper()}...")

    pipe = pipeline(
        "automatic-speech-recognition",
        model="Oriserve/Whisper-Hindi2Hinglish-Apex",
        device=device,
        torch_dtype=torch.float16,
        chunk_length_s=30,
    )

    print("Transcribing...")
    result = pipe(
        audio_path, return_timestamps=True, generate_kwargs={"language": "hi"}
    )

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    generate_srt(result["chunks"], args.output)

    print(f"Done! SRT saved at: {args.output}")

    if audio_path != args.input and os.path.exists(audio_path):
        os.remove(audio_path)


if __name__ == "__main__":
    main()
