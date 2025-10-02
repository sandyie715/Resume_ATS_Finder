import requests
import json

# The URL for the Ollama API endpoint
ollama_url = "http://localhost:11434/api/generate"

# The data payload for the request
payload = {
    "model": "llama3.2:3b",  # Replace with the model you are using, e.g., "gemma:2b"
    "prompt": "Why is the sky blue?",
    "stream": False  # Set to False to get the full response at once
}

try:
    # Send the POST request to the Ollama API
    response = requests.post(ollama_url, json=payload)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

    # Parse the JSON response
    response_data = response.json()
    
    # Print the model's response
    print(response_data['response'])

except requests.exceptions.RequestException as e:
    print(f"Error calling Ollama API: {e}")