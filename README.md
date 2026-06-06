# Hinglish Audio/Video Transcriber

A fully local, command-line transcription tool that converts Hindi/Hinglish audio and video files into SRT subtitles. It is optimized for Apple Silicon (M-series chips) using PyTorch's MPS backend and runs the `Oriserve/Whisper-Hindi2Hinglish-Apex` model.

## Features

- **100% Local:** No API keys or internet connection required after the initial model download.
- **Hardware Accelerated:** Uses Apple Metal Performance Shaders (MPS) for fast transcription on M-series chips.
- **Memory Efficient:** Processes audio in 30-second chunks to prevent out-of-memory crashes on large files.
- **Universal Input:** Accepts `.wav`, `.mp3`, `.m4a`, `.flac`, and automatically extracts audio from video files (like `.mp4`).

## Prerequisites

- Python 3.9 or higher
- `ffmpeg` installed on your system:
  - **Mac:** `brew install ffmpeg`
  - **Linux (Ubuntu/Debian):** `sudo apt update && sudo apt install ffmpeg`
  - **Windows:** Install via Winget (`winget install ffmpeg`) or download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)

## Installation

1. Create and activate a virtual environment:

   **Mac/Linux:**

   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

   **Windows:**

   ```cmd
   python -m venv env
   env\Scripts\activate
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```plaintext
.
├── backend/           # Core transcription logic modules
│   ├── audio.py
│   ├── transcriber.py
│   └── utils.py
├── env/               # Virtual environment (ignored in git)
├── requirements.txt   # Required Python dependencies
├── scripts/
│   └── transcribe.py  # The main transcription CLI script
├── app.py             # Streamlit web UI
└── README.md
```

## Usage

### Web UI (Recommended)

You can launch the interactive web interface using Streamlit:

```bash
streamlit run app.py
```

This will open a browser window where you can easily upload your audio/video files, preview them, and download the generated subtitles.

### Command Line Interface

You can run the script from the root directory of the project. It requires an input path (`-i`). If an output path (`-o`) is not provided, it will save the subtitle file in the same directory as the input file, but with a `.srt` extension.

#### Transcribe an Audio File

```bash
python scripts/transcribe.py -i audio.wav -o audio.srt
```

### Transcribe a Video File

```bash
python scripts/transcribe.py -i video.mp4 -o video_subs.srt
```

### Using Absolute Paths (External Drives)

```bash
python scripts/transcribe.py -i /Volumes/MyDrive/lecture.mp4 -o ~/Desktop/lecture.srt
```

## Notes

- The first time you run the script, it will download the ~1.6GB model from Hugging Face. Subsequent runs will load it instantly from your local cache.
- Temporary files generated during video extraction are automatically cleaned up after the transcription is complete.
