# parser.py
import pdfplumber
import re

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract raw text from a resume PDF."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def clean_text(text: str) -> str:
    """Remove extra whitespace and blank lines."""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def parse_resume(pdf_path: str) -> str:
    """Main function to parse resume and return clean text."""
    raw = extract_text_from_pdf(pdf_path)
    return clean_text(raw)

def parse_jd(jd_text: str) -> str:
    """Clean and return job description text."""
    return clean_text(jd_text) 
