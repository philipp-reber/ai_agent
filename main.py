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
    # Extract the response from the model using the client and message from main
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
    )        
    print("Response:")
    print(response.text)
    if verbose:
        prompt_tokens = response.usage_metadata.prompt_token_count
        response_tokens = response.usage_metadata.candidates_token_count
        print(f"Prompt tokens: {prompt_tokens}\nResponse tokens: {response_tokens}")


if __name__ == "__main__":
    main()