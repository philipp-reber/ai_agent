import os
import subprocess

def run_python_file(working_directory, file_path):
    try:
        working_directory = os.path.abspath(working_directory)
    except:
        return f"Error: Provided {working_directory} not in viable format."
       
    if file_path is not None:
        try:
            abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
        except:
            return f"Error: Provided {file_path} not in viable format."

        if not abs_file_path.startswith(working_directory):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.exists(abs_file_path):
            return f'Error: File "{file_path}" not found.'

        if file_path[-3:] != ".py" or len(file_path)<3:
            return f'Error: "{file_path}" is not a Python file.'
            
    else: 
        return 'Error: Please provide a file path to get the contents from'
    
    try:
        result = subprocess.run(
            ["python3", abs_file_path], #this is basically the terminal command that will be separated by spaces
            capture_output=True, #needs to be set to true manually in order to catch the output in the result Object
            cwd=working_directory, #saveguard that the script is run from the working_directory
            text=True, #sets the types of the outputs to strings instead of bytes (equal to encoding='utf-8')
            timeout=30 #sets a timeout for safety
        )
        output_parts = []

        if result.stdout: #catch the stdout
            output_parts.append(f"STDOUT:\n{result.stdout.strip()}")
        if result.stderr: #catch the errors
            output_parts.append(f"STDERR:\n{result.stderr.strip()}")
        if result.returncode != 0: #means the programm did not run as expected
            output_parts.append(f"Process exited with code {result.returncode}")
        if not output_parts:
            return "No output produced."

        return "\n".join(output_parts)

    except Exception as e:
        return f"Error: executing Python file: {e}"
