import os

def get_files_info(working_directory, directory=None):
    try:
        working_directory = os.path.abspath(working_directory)
    except:
        return f"Error: Provided {working_directory} not in viable format."
       
    if directory is not None:
        try:
            directory = os.path.abspath(os.path.join(working_directory, directory))
        except:
            return f"Error: Provided {directory} not in viable format."

        if not directory.startswith(working_directory):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    
        if not os.path.isdir(directory):
            return f'Error: "{directory}" is not a directory'
    else: directory = working_directory

    contents = ""
    try:
        for item in os.listdir(directory):
            try:
                name = f"- {item}: "
                size = f"file_size={os.path.getsize(os.path.join(directory, item))} bytes, "
                isfile = "is_dir=True\n"
                if os.path.isfile(os.path.join(directory, item)):
                    isfile = "is_dir=False\n"
                contents += name + size + isfile
            except:
                return f"Error: Trying to access {item} in {directory} failed."
    except: 
        return f"Error: Failed to list the contents of directory {directory}."
    return contents