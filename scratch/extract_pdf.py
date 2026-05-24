import sys
import os

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: pypdf not installed. Please install it using pip install pypdf")
    sys.exit(1)

pdf_path = r"C:\Users\34628\Downloads\Proyecto_antigravity\Vortex_Original\Blacksheep_Vortex.pdf"

if not os.path.exists(pdf_path):
    print(f"Error: PDF file not found at {pdf_path}")
    sys.exit(1)

reader = PdfReader(pdf_path)
text = ""
for i, page in enumerate(reader.pages):
    page_text = page.extract_text()
    if page_text:
        text += f"--- Page {i + 1} ---\n{page_text}\n\n"

output_path = r"C:\Users\34628\Downloads\Proyecto_antigravity\scratch\extracted_vortex.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(text)

print(f"Extracted {len(reader.pages)} pages to {output_path}")
