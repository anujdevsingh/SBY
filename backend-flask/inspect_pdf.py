"""Inspect PDF content."""
from pypdf import PdfReader
from pathlib import Path

pdf_path = Path('policies/sby_policy.pdf')
reader = PdfReader(str(pdf_path))

print(f"PDF: {pdf_path.name}")
print(f"Pages: {len(reader.pages)}\n")

for i, page in enumerate(reader.pages, 1):
    text = page.extract_text()
    print(f"=== Page {i} ===")
    print(text[:500])
    print("...\n")
