from pypdf import PdfReader
from docx import Document as DocxDocument

def extract_text(file_field):
    """Extract raw text from an uploaded PDF or DOCX file."""
    name = file_field.name.lower()
    file_field.seek(0)

    if name.endswith('.pdf'):
        reader = PdfReader(file_field)
        return '\n'.join(page.extract_text() or '' for page in reader.pages)

    elif name.endswith('.docx'):
        doc = DocxDocument(file_field)
        return '\n'.join(p.text for p in doc.paragraphs)

    else:
        raise ValueError(f"Unsupported file type: {name}")