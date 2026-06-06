import torch
from transformers import pipeline


def load_model():
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    pipe = pipeline(
        "automatic-speech-recognition",
        model="Oriserve/Whisper-Hindi2Hinglish-Apex",
        device=device,
        torch_dtype=torch.float16,
        chunk_length_s=30,
    )
    return pipe


def transcribe(pipe, audio_path):
    result = pipe(
        audio_path, return_timestamps=True, generate_kwargs={"language": "hi"}
    )
    return result["chunks"]
