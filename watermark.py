from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from io import BytesIO

def add_watermark(input_pdf, output_pdf, watermark_text):
    # Create watermark
    packet = BytesIO()
    can = canvas.Canvas(packet)
    can.drawString(30, 30, watermark_text)
    can.save()
    packet.seek(0)

    # Read files and merge watermark
    watermark = PdfReader(packet)
    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()

    for page in pdf_reader.pages:
        page.merge_page(watermark.pages[0])
        pdf_writer.add_page(page)

    with open(output_pdf, "wb") as output:
        pdf_writer.write(output)

# Test the function
input_pdf = "sample_input.pdf"   # Path to your input PDF file
output_pdf = "sample_output.pdf" # Path where the output will be saved
watermark_text = "Confidential"  # The watermark text to be added

# Run the watermark function
add_watermark(input_pdf, output_pdf, watermark_text)

print(f"Watermarked PDF saved as '{output_pdf}'")
