# ============================================================
# app/services/parser.py
# Resume parsing: PDF / DOCX -> plain text -> structured dict.
# ============================================================
import io
import logging
import re

import docx
import pdfplumber

logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# Text extraction
# ------------------------------------------------------------
def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file."""
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts).strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file."""
    document = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Route to the correct extractor based on file extension."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    if lower.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    raise ValueError(f"Unsupported file type: {filename}")


# ------------------------------------------------------------
# Lightweight heuristics (regex-based)
# ------------------------------------------------------------
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s\-()]{7,}\d)")
LOCATION_HINTS = [
    "gaza",
    "ramallah",
    "jerusalem",
    "hebron",
    "nablus",
    "amman",
    "cairo",
    "riyadh",
    "dubai",
    "doha",
    "kuwait",
]

SECTION_HEADERS = {
    "summary": ["summary", "profile", "objective", "about"],
    "experience": ["experience", "employment", "work history"],
    "education": ["education", "academic", "qualifications"],
    "skills": ["skills", "technical skills", "competencies"],
}


def detect_sections(text: str) -> dict[str, str]:
    """
    Detect common resume sections by scanning for headers.

    Returns a mapping {section_name: content}.
    """
    lower = text.lower()
    found: dict[str, str] = {}

    for section, keywords in SECTION_HEADERS.items():
        for keyword in keywords:
            idx = lower.find(keyword)
            if idx != -1:
                found[section] = text[idx : idx + 800]
                break

    return found


def parse_resume_text(text: str) -> dict:
    """
    Convert raw resume text into a structured dict.

    This is a heuristic parser. Richer parsing is delegated to the LLM.
    """
    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(text)

    location = None
    lower = text.lower()
    for city in LOCATION_HINTS:
        if city in lower:
            location = city.title()
            break

    sections = detect_sections(text)

    return {
        "raw_text": text,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0).strip() if phone_match else None,
        "location": location,
        "summary": sections.get("summary"),
        "experience": sections.get("experience"),
        "education": sections.get("education"),
        "skills": sections.get("skills"),
        "word_count": len(text.split()),
    }
