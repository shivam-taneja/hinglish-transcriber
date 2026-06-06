import os
import tempfile
import datetime


def get_input_output_paths(local_file_path, uploaded_file, custom_dir):
    input_path = ""
    output_path = ""
    is_temp_input = False
    base_name = ""

    if local_file_path and os.path.exists(local_file_path):
        input_path = local_file_path
        original_filename = os.path.basename(local_file_path)
        base_name = f"{os.path.splitext(original_filename)[0]}.srt"

        if custom_dir and os.path.isdir(custom_dir.strip()):
            output_path = os.path.join(custom_dir.strip(), base_name)
        else:
            output_path = f"{os.path.splitext(local_file_path)[0]}.srt"

    elif uploaded_file is not None:
        file_ext = uploaded_file.name.split(".")[-1].lower()

        # Save temp file
        tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}")
        tmp_in.write(uploaded_file.getvalue())
        tmp_in.close()

        input_path = tmp_in.name
        is_temp_input = True

        original_filename = uploaded_file.name
        base_name = f"{os.path.splitext(original_filename)[0]}.srt"

        if custom_dir and os.path.isdir(custom_dir.strip()):
            output_path = os.path.join(custom_dir.strip(), base_name)
        else:
            output_path = os.path.abspath(base_name)

    # Prevent overwriting existing files by appending a timestamp
    if output_path and os.path.exists(output_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(output_path)
        output_path = f"{name}_{timestamp}{ext}"

    return input_path, output_path, is_temp_input, base_name


def cleanup_temp_input(input_path, is_temp_input):
    if is_temp_input and os.path.exists(input_path):
        os.remove(input_path)
