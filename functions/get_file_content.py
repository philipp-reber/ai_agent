import os

def get_file_content(working_directory, file_path):
    try:
        working_directory = os.path.abspath(working_directory)
    except:
        return f"Error: Provided {working_directory} not in viable format."
       
    if file_path is not None:
        try:
            file_path = os.path.abspath(os.path.join(working_directory, file_path))
        except:
            return f"Error: Provided {file_path} not in viable format."

        if not file_path.startswith(working_directory):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    
        if not os.path.isfile(file_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'
    else: 
        return f'Error: Please provide a file path to get the contents from'

    MAX_CHARS = 10000

    try:
        with open(file_path, "r") as f:
            file_content_string = f.read()
            if len(file_content_string) > MAX_CHARS:
                file_content_string = file_content_string[:MAX_CHARS]
                return file_content_string + f' "{file_path}" turncated at 10000 characters'
            return file_content_string

    except:
        return f"Error: Failed to read file."