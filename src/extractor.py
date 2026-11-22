"""
Resume Extraction Module
Extracts text from PDF, DOCX, and TXT files, alongside candidate metadata.
"""
from pathlib import Path
from typing import Dict, Any, List
import io
import PyPDF2
from docx import Document
from src.cleaner import extract_contact_info


def extract_text_from_pdf(file_path_or_bytes) -> str:
    """Extracts text content from a PDF file path or byte stream using PyPDF2."""
    text = ""
    try:
        if isinstance(file_path_or_bytes, (str, Path)):
            with open(file_path_or_bytes, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        else:
            # BytesIO stream
            reader = PyPDF2.PdfReader(file_path_or_bytes)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[Warning] Failed to extract PDF text: {e}")
    return text.strip()


def extract_text_from_docx(file_path_or_bytes) -> str:
    """Extracts text content from a DOCX file path or byte stream using python-docx."""
    text = []
    try:
        doc = Document(file_path_or_bytes)
        for p in doc.paragraphs:
            if p.text.strip():
                text.append(p.text.strip())
        for table in doc.tables:
            for row in table.rows:
                row_str = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
                if row_str:
                    text.append(row_str)
    except Exception as e:
        print(f"[Warning] Failed to extract DOCX text: {e}")
    return "\n".join(text)


def extract_text_from_file(file_path: str | Path) -> str:
    """Determines file type by extension and delegates text extraction."""
    p = Path(file_path)
    suffix = p.suffix.lower()
    
    if suffix == ".pdf":
        return extract_text_from_pdf(p)
    elif suffix in [".docx", ".doc"]:
        return extract_text_from_docx(p)
    elif suffix in [".txt", ".md"]:
        return p.read_text(encoding="utf-8", errors="ignore")
    else:
        return p.read_text(encoding="utf-8", errors="ignore")


def extract_candidate_name(text: str, filename: str) -> str:
    """
    Infers candidate name from the top non-empty lines or from the filename.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:3]:
        # Filter out common header words
        low = line.lower()
        if not any(k in low for k in ["resume", "curriculum", "cv", "page", "contact", "email", "phone"]):
            # If line is short and looks like a name (2 to 4 words)
            words = line.split()
            if 1 <= len(words) <= 4 and all(w.isalpha() for w in words):
                return line.title()
                
    # Fallback to sanitized filename
    clean_name = Path(filename).stem.replace("_", " ").replace("-", " ")
    clean_name = "".join([c for c in clean_name if c.isalpha() or c == " "]).strip()
    return clean_name.title() or "Anonymous Candidate"


def parse_resume_document(file_path: str | Path) -> Dict[str, Any]:
    """
    Parses a single resume document into a comprehensive metadata dictionary.
    """
    p = Path(file_path)
    raw_text = extract_text_from_file(p)
    contact = extract_contact_info(raw_text)
    name = extract_candidate_name(raw_text, p.name)
    
    return {
        "filename": p.name,
        "candidate_name": name,
        "raw_text": raw_text,
        "contact": contact
    }


def load_all_resumes(resumes_dir: str | Path) -> List[Dict[str, Any]]:
    """Loads and parses all supported resume files in a target directory."""
    dir_path = Path(resumes_dir)
    resumes = []
    
    if not dir_path.exists():
        return resumes
        
    supported_extensions = [".pdf", ".docx", ".txt"]
    for file_path in dir_path.iterdir():
        if file_path.suffix.lower() in supported_extensions:
            resumes.append(parse_resume_document(file_path))
            
    return resumes
