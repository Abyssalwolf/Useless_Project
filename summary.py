import os
from PyPDF2 import PdfReader
from api_key import key
from groq import Groq  # Ensure this library is available and imported

# Set up your Groq API client with an API key from environment variables
client = Groq(api_key=os.environ.get(key))  # Ensure your key is set in the environment

def extract_text_from_pdf(input_pdf):
    """Extract text from each page of the PDF."""
    pdf_reader = PdfReader(input_pdf)
    full_text = ""
    for page in pdf_reader.pages:
        full_text += page.extract_text() or ""
    return full_text

def generate_summary_with_groq(full_text):
    """Generate a summary using the Groq model."""
    if not full_text:
        return "No content found to summarize."

    # Send the extracted text to Groq for summarization
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Summarize the following text:\n\n{full_text}"
            }
        ],
        model="gemma2-9b-it",
        max_tokens=150  # Adjust as needed based on desired summary length
    )
    
    # Extract and return the summary from the response
    return response.choices[0].message.content.strip()
