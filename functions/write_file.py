import os

def write_file(working_directory, file_path, content):
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
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.exists(file_path):
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            except:
                return 'Error: Failed to create filepath'
    else: 
        return 'Error: Please provide a file path to write to'
    
    try:
        with open(file_path, "w") as f:
            f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except:
        return f"Error: Failed to write in file."