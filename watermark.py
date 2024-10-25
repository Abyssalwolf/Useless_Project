from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from io import BytesIO

def create_watermark(watermark_text, position, page_width, page_height):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))

    # Define the watermark position
    if position == "bottom_left":
        x, y = 30, 30  # Bottom left corner with margin
    elif position == "bottom_right":
        text_width = can.stringWidth(watermark_text, 'Helvetica', 12)  # Get text width
        x, y = page_width - text_width - 30, 30  # Adjust for text width and margin
    else:
        raise ValueError("Position must be 'bottom_left' or 'bottom_right'.")

    can.drawString(x, y, watermark_text)
    can.save()
    packet.seek(0)
    return packet

def add_watermark(input_pdf, output_pdf, watermark_text, position):
    if position not in ["bottom_left", "bottom_right"]:
        raise ValueError("Position must be 'bottom_left' or 'bottom_right'.")

    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()

    # Get the page dimensions from the first page
    first_page = pdf_reader.pages[0]
    page_width = first_page.mediabox.width
    page_height = first_page.mediabox.height

    # Create watermark based on dimensions
    packet = create_watermark(watermark_text, position, page_width, page_height)
    watermark = PdfReader(packet)

    # Merge watermark onto each page
    for page in pdf_reader.pages:
        page.merge_page(watermark.pages[0])
        pdf_writer.add_page(page)

    with open(output_pdf, "wb") as output:
        pdf_writer.write(output)

# Test the function
input_pdf = "sample_input.pdf"   # Path to your input PDF file
output_pdf = "sample_output.pdf" # Path where the output will be saved
watermark_text = "Confidential and Proprietary Information"  # The watermark text to be added

# Run the watermark function with specified position
add_watermark(input_pdf, output_pdf, watermark_text, position="bottom_right")

print(f"Watermarked PDF saved as '{output_pdf}'")
