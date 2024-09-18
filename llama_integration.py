import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch API key from the environment
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# Function to call OpenRouter's Meta LLaMA 3.1 model for name/email extraction
def extract_name_email_with_llama(text):
    if not OPENROUTER_API_KEY:
        raise ValueError("OpenRouter API key not found! Make sure it's set in the environment.")

    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json'
    }

    # Construct the prompt for OpenRouter to extract name and email
    prompt = f"Extract the name and email from the following resume:\n\n{text}"

    # OpenRouter API endpoint (this may need adjustment based on the service you're using)
    url = "https://openrouter.ai/api/v1/chat/completions"

    # Payload for the API request
    data = {
        "model": "meta-llama/llama-3.1-8b-instruct:free",  # Specify the model
        "messages": [
            {"role": "user", "content": prompt}  # The prompt passed to the model
        ]
    }

    # Send the request to OpenRouter
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check if the request was successful
    if response.status_code == 200:
        result = response.json()
        # Extract the content of the first choice
        response_text = result['choices'][0]['message']['content']
        
        # Parse the response text to extract name and email
        name, email = parse_llama_response(response_text)
        return name, email
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return 'N/A', 'N/A'

# Function to parse OpenRouter's response to get name and email
def parse_llama_response(llama_response):
    # Assuming the response will return something like:
    # Name: John Doe
    # Email: johndoe@example.com
    lines = llama_response.splitlines()

    name = 'N/A'
    email = 'N/A'

    # Simple parsing logic based on keywords
    for line in lines:
        if "Name:" in line:
            name = line.split(":", 1)[1].strip()  # Extract the name
        elif "Email:" in line:
            email = line.split(":", 1)[1].strip()  # Extract the email

    return name, email
