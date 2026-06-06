import streamlit as st
import os

from frontend.components import reveal_file_button, render_media_selection
from frontend.paths import get_input_output_paths, cleanup_temp_input
from frontend.runner import stream_transcription

st.set_page_config(page_title="Hinglish Transcriber", layout="wide")

st.title("Hinglish Audio and Video Transcriber")
st.markdown(
    "Upload your Hindi or Hinglish media file (or enter its local path) to generate an SRT subtitle file."
)

col1, col2 = st.columns([1, 1])

with col1:
    local_file_path, uploaded_file, custom_dir = render_media_selection()

with col2:
    st.subheader("Transcription Status")

    can_transcribe = (local_file_path and os.path.exists(local_file_path)) or (
        uploaded_file is not None
    )

    if can_transcribe:
        if st.button("Start Transcription", type="primary", use_container_width=True):
            input_path, output_path, is_temp_input, base_name = get_input_output_paths(
                local_file_path, uploaded_file, custom_dir
            )

            with st.status("Processing your file...", expanded=True) as status:
                success = stream_transcription(input_path, output_path, base_name)

                if success:
                    status.update(
                        label=f"Transcription completed! File saved at: {output_path}",
                        state="complete",
                        expanded=False,
                    )
                    st.session_state["last_output"] = output_path
                else:
                    status.update(label="An error occurred", state="error")

            cleanup_temp_input(input_path, is_temp_input)

        if st.session_state.get("last_output") and os.path.exists(
            st.session_state["last_output"]
        ):
            reveal_file_button(st.session_state["last_output"])

    else:
        st.info("Please select a file on the left to begin.")
