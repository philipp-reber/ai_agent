import sys
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.run_python_file import run_python_file
from functions.write_file import write_file

def call_function(function_call_part, verbose=False):
     
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    
    mapping = {
        "get_file_content": get_file_content,
        "get_files_info": get_files_info,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }

    if function_call_part.name not in mapping:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ],
        )
    
    result = mapping[function_call_part.name](working_directory="./calculator", **function_call_part.args)

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": result},
            )
        ],
    )

def main():
    # Load environment variables
    load_dotenv()
    
    # Get prompt from terminal and check for the --verbose command
    verbose = "--verbose" in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    # If the user did not enter anything, make him aware of how to use the tool
    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I build a calculator app?"')
        sys.exit(1)
    
    # Join multiple prompts and print it if --verbose was called
    user_prompt = " ".join(args)
    if verbose:
        print(f"User prompt: {user_prompt}\n")

    # Get the API key from the environment variables and set up a client
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    # Set the messages variable to a list of the enteres prompts
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    # Call the model 20 times maximum to produce the result we want
    for i in range(20):
        new_messages, done, final_text = generate_content(client, messages, verbose)
        messages.extend(new_messages)  
        if done:
            print("Final response:")
            print(final_text)
            break


def generate_content(client, messages, verbose):
    # Set System Prompt for default behaviour of the LLM
    system_prompt = """
        You are a helpful AI coding agent.

        When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

        - List files and directories
        - Read file contents
        - Execute Python files with optional arguments
        - Write or overwrite files

        All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
        
        After using a tool, always wait for the result before summarizing or planning next steps.
        """

    # Declaration of the function schemas for the LLM to understand how to use the provided functions (this does not allow the agent to call the functions yet!)
    schema_get_files_info = types.FunctionDeclaration(
        name="get_files_info",
        description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "directory": types.Schema(
                    type=types.Type.STRING,
                    description="The directory to list files from, relative to the working directory. Has to be provided in all cases!",
                ),
            },
        ),
    )

    schema_get_file_content = types.FunctionDeclaration(
        name="get_file_content",
        description="Lists file content for the specified file path, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The file path to extract the content from, relative to the working directory. If not provided, the function will return an error message.",
                ),
            },
        ),
    )

    schema_write_file = types.FunctionDeclaration(
        name="write_file",
        description="Writes a file with the specified content in the specified file path, constrained to the working directory. If the file does not exist, the file is created. If the file exists, the contents are overwritten.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The file path to write the file to, relative to the working directory. If not provided, the function will return an error message.",
                ),
                "content": types.Schema(
                    type=types.Type.STRING,
                    description="The content that you want to write in the file. If not provided, will create an empty file",
                )
            },
        ),
    )

    schema_run_python_file = types.FunctionDeclaration(
        name="run_python_file",
        description="Runs a Python (.py) file in the specified file path, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The file path to the Python file that should be run, relative to the working directory. If not provided, the function will return an error message.",
                ),
            },
        ),
    )
    
    # Lists the available functions for the model
    available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
    )

    # Extract the response from the model using the client and message from main
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt),
    )        
    
    if verbose:
        prompt_tokens = response.usage_metadata.prompt_token_count
        response_tokens = response.usage_metadata.candidates_token_count
        print(f"Prompt tokens: {prompt_tokens}\nResponse tokens: {response_tokens}")

    new_messages = [] # Gather new_messages as a list to return
    for candidate in response.candidates:
        new_messages.append(candidate.content)

    if response.function_calls:
        for function_call in response.function_calls:
            func_response = call_function(function_call, verbose)
            if not hasattr(func_response, "parts"):
                raise Exception("Missing .parts")
            if not isinstance(func_response.parts, list):
                raise Exception(".parts not a list")
            if not len(func_response.parts) > 0:
                raise Exception(".parts is empty")
            if not hasattr(func_response.parts[0], "function_response"):
                raise Exception("Missing .function_response")
            if not hasattr(func_response.parts[0].function_response, "response"):
                raise Exception("Missing .response")
            if verbose:
                print(f"-> {func_response.parts[0].function_response.response}")
            tool_content = types.Content(
                role="tool",
                parts=[types.Part(function_response=func_response.parts[0].function_response)]
            )
            new_messages.append(tool_content)
        return new_messages, False, None
            
    else:
        # No function call, done!
        return new_messages, True, response.text

if __name__ == "__main__": 
    main()