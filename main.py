import sys
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv


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

    # Call the generate content function to create an output
    generate_content(client, messages, verbose)


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

    if response.function_calls:
        for function_call in response.function_calls:
            print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print("Response:")
        print(response.text)

if __name__ == "__main__":
    main()