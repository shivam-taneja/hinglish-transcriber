#!/usr/bin/env python3
import argparse
import os
import sys

# Add root project directory to sys.path to allow imports when running from scripts/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.audio import extract_audio
from backend.transcriber import load_model, transcribe
from backend.utils import generate_srt


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

    print("Loading Oriserve model locally...")
    pipe = load_model()

    print("Transcribing...")
    chunks = transcribe(pipe, audio_path)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    generate_srt(chunks, args.output)

    print(f"Done! SRT saved at: {args.output}")

    if audio_path != args.input and os.path.exists(audio_path):
        os.remove(audio_path)


if __name__ == "__main__":
    main()
