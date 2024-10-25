import os
from groq import Groq  # Ensure this library is installed and available

# Retrieve the API key from an environment variable
api_key = os.environ.get("GROQ_API_KEY")  # Ensure this matches the variable name used
if not api_key:
    raise ValueError("API key not found. Please set the GROQ_API_KEY environment variable.")

client = Groq(api_key=api_key)

# Generate a chat completion
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="gemma2-9b-it",
)

# Print the response content
print(chat_completion.choices[0].message.content)
