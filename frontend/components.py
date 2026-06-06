import streamlit as st
import platform
import subprocess
import os


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


def render_media_selection():
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

    return local_file_path, uploaded_file, custom_dir
