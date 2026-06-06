import streamlit as st
import os
import tempfile
import subprocess
import platform

st.set_page_config(page_title="Hinglish Transcriber", layout="wide")


@st.fragment
def reveal_file_button(path):
    os_name = platform.system()
    btn_text = (
        "Reveal in Explorer"
        if os_name == "Windows"
        else "Reveal in Finder" if os_name == "Darwin" else "Open Folder"
    )

    if st.button(btn_text, type="secondary"):
        if os_name == "Windows":
            subprocess.run(["explorer", "/select,", os.path.normpath(path)])
        elif os_name == "Darwin":
            subprocess.run(["open", "-R", path])
        else:
            subprocess.run(["xdg-open", os.path.dirname(path)])


st.title("Hinglish Audio and Video Transcriber")
st.markdown(
    "Upload your Hindi or Hinglish media file (or enter its local path) to generate an SRT subtitle file."
)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Select Media")

    tab1, tab2 = st.tabs(["Enter File Path (Recommended)", "Upload File"])

    uploaded_file = None
    local_file_path = ""

    with tab1:
        st.markdown(
            "**Provides the best experience:** The subtitle will automatically save in the exact same folder as your input file!"
        )
        local_file_path = st.text_input(
            "Absolute File Path",
            placeholder="e.g., /Users/shivamtaneja/Downloads/podcast.wav",
        )
        if local_file_path and os.path.exists(local_file_path):
            st.success("File found!")
        elif local_file_path:
            st.error("File not found. Please double-check the path.")

    with tab2:
        st.markdown(
            "*Note: Web browsers hide the original folder path of uploaded files for security. Uploaded files will save the SRT to the project root unless you specify a custom directory below.*"
        )
        uploaded_file = st.file_uploader(
            "Choose a file", type=["wav", "mp3", "m4a", "flac", "mp4", "mkv", "mov"]
        )

        if uploaded_file is not None:
            file_ext = uploaded_file.name.split(".")[-1].lower()
            if file_ext in ["wav", "mp3", "m4a", "flac"]:
                st.audio(uploaded_file)
            else:
                st.video(uploaded_file)

    st.divider()
    custom_dir = st.text_input(
        "Custom Output Directory (Optional)",
        placeholder="e.g., /Users/shivamtaneja/Downloads",
        help="If left blank, it defaults to the input folder (if using File Path) or project root (if using Upload).",
    )


with col2:
    st.subheader("Transcription Status")

    can_transcribe = (local_file_path and os.path.exists(local_file_path)) or (
        uploaded_file is not None
    )

    if can_transcribe:
        if st.button("Start Transcription", type="primary", use_container_width=True):
            with st.status("Processing your file...", expanded=True) as status:

                input_path = ""
                output_path = ""
                is_temp_input = False
                original_filename = ""

                # Determine paths based on input method
                if local_file_path and os.path.exists(local_file_path):
                    input_path = local_file_path
                    original_filename = os.path.basename(local_file_path)
                    base_name = f"{os.path.splitext(original_filename)[0]}.srt"

                    if custom_dir and os.path.isdir(custom_dir.strip()):
                        output_path = os.path.join(custom_dir.strip(), base_name)
                    else:
                        # Automatically default to the EXACT SAME FOLDER as the input file!
                        output_path = f"{os.path.splitext(local_file_path)[0]}.srt"

                elif uploaded_file is not None:
                    st.write("Saving uploaded file temporarily...")
                    file_ext = uploaded_file.name.split(".")[-1].lower()
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=f".{file_ext}"
                    ) as tmp_in:
                        tmp_in.write(uploaded_file.getvalue())
                        input_path = tmp_in.name
                        is_temp_input = True

                    original_filename = uploaded_file.name
                    base_name = f"{os.path.splitext(original_filename)[0]}.srt"

                    if custom_dir and os.path.isdir(custom_dir.strip()):
                        output_path = os.path.join(custom_dir.strip(), base_name)
                    else:
                        output_path = os.path.abspath(base_name)

                try:
                    st.write(
                        "Running transcription in an isolated process to prevent memory crashes..."
                    )

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
                            file_name=base_name,
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

                        st.session_state["last_output"] = output_path

                    else:
                        status.update(label="An error occurred", state="error")
                        st.error("Failed to execute transcription.")

                except Exception as e:
                    status.update(label="An error occurred", state="error")
                    st.error(f"Failed to execute transcription: {str(e)}")

                finally:
                    # Cleanup temp input file if we used the uploader
                    if is_temp_input and os.path.exists(input_path):
                        os.remove(input_path)

        if st.session_state.get("last_output") and os.path.exists(
            st.session_state["last_output"]
        ):
            reveal_file_button(st.session_state["last_output"])

    else:
        st.info("Please select a file on the left to begin.")
