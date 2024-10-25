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

def chunk_text(text, max_length=1500):
    """Chunk text into manageable parts."""
    chunks = []
    while len(text) > max_length:
        split_index = text.rfind(' ', 0, max_length)  # Find last space within max_length
        chunks.append(text[:split_index])
        text = text[split_index:].strip()  # Remove the processed chunk
    chunks.append(text)  # Append any remaining text
    return chunks

def generate_summary_with_groq(full_text):
    """Generate a summary using the Groq model."""
    if not full_text:
        return "No content found to summarize."
    
    chunks = chunk_text(full_text)  # Chunk the text for processing
    summaries = []

    # Send the extracted text to Groq for summarization
    for chunk in chunks:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Briefly summarize the following text. Focus on key points and condense the information. "
                        "Avoid using special characters and aim for a concise response:\n\n"
                        f"{chunk}"
                    )
                }
            ],
            model="gemma2-9b-it",
            max_tokens=150  # Lower the token limit for shorter summaries
        )
        
        # Extract and append the summary from the response
        summaries.append(response.choices[0].message.content.strip())

    return "\n\n".join(summaries)  # Join all summaries together

# Input PDF file path
input_pdf = "sample_input.pdf"  # Path to your input PDF file

# Run extraction and summarization
full_text = extract_text_from_pdf(input_pdf)
summary = generate_summary_with_groq(full_text)

print("Generated Summary:")
print(summary)
