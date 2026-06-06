import streamlit as st
import os
import tempfile
from backend.audio import extract_audio
from backend.transcriber import load_model, transcribe
from backend.utils import generate_srt

st.set_page_config(page_title="Hinglish Transcriber", layout="wide")


@st.cache_resource(show_spinner=False)
def get_model():
    return load_model()


st.title("Hinglish Audio and Video Transcriber")
st.markdown(
    "Upload your Hindi or Hinglish media file to generate an SRT subtitle file locally."
)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Upload Media")
    uploaded_file = st.file_uploader(
        "Choose a file", type=["wav", "mp3", "m4a", "flac", "mp4", "mkv", "mov"]
    )

    if uploaded_file is not None:
        file_ext = uploaded_file.name.split(".")[-1].lower()
        if file_ext in ["wav", "mp3", "m4a", "flac"]:
            st.audio(uploaded_file)
        else:
            st.video(uploaded_file)

with col2:
    st.subheader("Transcription Status")
    if uploaded_file is not None:
        if st.button("Start Transcription", type="primary", use_container_width=True):
            with st.status("Processing your file...", expanded=True) as status:
                st.write("Saving uploaded file temporarily...")
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=f".{file_ext}"
                ) as tmp_in:
                    tmp_in.write(uploaded_file.getvalue())
                    input_path = tmp_in.name

                output_path = f"{os.path.splitext(input_path)[0]}.srt"

                try:
                    st.write("Loading transcription model into memory...")
                    pipe = get_model()

                    st.write("Extracting audio track...")
                    audio_path = extract_audio(input_path)

                    st.write("Transcribing audio content...")
                    chunks = transcribe(pipe, audio_path)

                    st.write("Generating SRT file...")
                    generate_srt(chunks, output_path)

                    status.update(
                        label="Transcription completed successfully!",
                        state="complete",
                        expanded=False,
                    )

                    with open(output_path, "r", encoding="utf-8") as f:
                        srt_content = f.read()

                    st.download_button(
                        label="Download Subtitles (SRT)",
                        data=srt_content,
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}.srt",
                        mime="text/plain",
                        use_container_width=True,
                    )

                    with st.expander("Preview Subtitles"):
                        st.text_area(
                            "Generated SRT Content",
                            value=srt_content,
                            height=300,
                            disabled=True,
                        )

                except Exception as e:
                    status.update(label="An error occurred", state="error")
                    st.error(f"Failed to execute transcription: {str(e)}")

                finally:
                    # Cleanup
                    if (
                        "audio_path" in locals()
                        and audio_path != input_path
                        and os.path.exists(audio_path)
                    ):
                        os.remove(audio_path)
                    if os.path.exists(input_path):
                        os.remove(input_path)
                    if os.path.exists(output_path):
                        os.remove(output_path)
    else:
        st.info("Please upload a file on the left to begin.")
