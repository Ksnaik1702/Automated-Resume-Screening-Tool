"""
Text Preprocessing and Cleaning Module
Handles regex cleaning, URL/phone/email extraction & masking, and punctuation normalization.
"""
import re
from typing import Dict, Any


def clean_text(text: str) -> str:
    """
    Cleans raw resume or job description text for NLP feature extraction.
    
    Steps:
    1. Removes URLs and hyperlinks
    2. Strips bullet points and excessive symbols (preserving +, #, .)
    3. Normalizes whitespace and newlines
    4. Converts to lower case
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove URLs
    cleaned = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    
    # Remove email addresses from raw text (saved separately during extraction)
    cleaned = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' ', cleaned)
    
    # Remove phone numbers (10 digits with optional hyphens/parentheses)
    cleaned = re.sub(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?[\d\-\.\s]{7,13}', ' ', cleaned)
    
    # Remove miscellaneous punctuation except characters meaningful in tech skills (+, #, .)
    cleaned = re.sub(r'[^a-zA-Z0-9\+\#\.\s]', ' ', cleaned)
    
    # Collapse multiple whitespaces into a single space
    cleaned = re.sub(r'\s+', ' ', cleaned).strip().lower()
    
    return cleaned


def extract_contact_info(text: str) -> Dict[str, Any]:
    """
    Extracts contact info (email, phone, LinkedIn/GitHub links) from raw resume text before cleaning.
    """
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    email = email_match.group(0) if email_match else "N/A"
    
    # Phone regex pattern supporting Indian (+91 98765 43210), standard 10-digit, and US formats
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\d{5}[-.\s]?\d{5}|\b\d{10}\b|\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    phone = phone_match.group(0).strip() if phone_match else "N/A"
    
    # LinkedIn / GitHub URLs
    linkedin_match = re.search(r'(linkedin\.com/in/[a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    github_match = re.search(r'(github\.com/[a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    
    return {
        "email": email,
        "phone": phone,
        "linkedin": linkedin_match.group(0) if linkedin_match else "N/A",
        "github": github_match.group(0) if github_match else "N/A"
    }
