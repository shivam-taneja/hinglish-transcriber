import streamlit as st
import os
import tempfile

st.set_page_config(page_title="Hinglish Transcriber", layout="wide")


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

                # Save the output file permanently in the current directory
                output_path = os.path.abspath(
                    f"{os.path.splitext(uploaded_file.name)[0]}.srt"
                )

                try:
                    st.write(
                        "Running transcription in an isolated process to prevent memory crashes..."
                    )

                    import subprocess

                    process = subprocess.Popen(
                        [
                            "python",
                            "scripts/transcribe.py",
                            "-i",
                            input_path,
                            "-o",
                            output_path,
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                    )

                    # Stream the output live to the Streamlit UI
                    for line in process.stdout:
                        if line.strip():
                            st.write(line.strip())

                    process.wait()

                    if process.returncode == 0 and os.path.exists(output_path):
                        status.update(
                            label=f"Transcription completed! File saved at: {output_path}",
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

                    else:
                        status.update(label="An error occurred", state="error")
                        st.error("Failed to execute transcription.")

                except Exception as e:
                    status.update(label="An error occurred", state="error")
                    st.error(f"Failed to execute transcription: {str(e)}")

                finally:
                    # Cleanup temp input file
                    if os.path.exists(input_path):
                        os.remove(input_path)
    else:
        st.info("Please upload a file on the left to begin.")
