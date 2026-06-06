import streamlit as st
import subprocess
import os


def stream_transcription(input_path, output_path, base_name):
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

        log_container = st.empty()
        logs = []

        # Stream the output live to the Streamlit UI
        for line in process.stdout:
            if line.strip():
                logs.append(line.strip())
                # Show a live updating terminal window of the last 15 lines (simulates auto-scrolling)
                windowed_logs = "\n".join(logs[-15:])
                log_container.code(windowed_logs, language="bash")

        process.wait()

        # When finished, show the full logs
        if logs:
            log_container.code("\n".join(logs), language="bash")

        if process.returncode == 0 and os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                srt_content = f.read()

            st.download_button(
                label="Download Subtitles (SRT)",
                data=srt_content,
                file_name=os.path.basename(output_path),
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

            return True
        else:
            st.error("Failed to execute transcription.")
            return False

    except Exception as e:
        st.error(f"Failed to execute transcription: {str(e)}")
        return False
