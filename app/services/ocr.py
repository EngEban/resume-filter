# ============================================================
# app/services/ocr.py
# OCR for image-based resumes (optional dependency).
# ============================================================
# easyocr + torch are heavy (~2.5 GB). They are optional and
# only loaded if the user has installed requirements-ocr.txt.
#
# If easyocr is not available, all functions in this module
# gracefully degrade by returning an empty string.
# ============================================================
import io
import logging
from typing import Any

logger = logging.getLogger(__name__)


# ---------- Optional import ----------
try:
    import easyocr  # type: ignore[import-not-found]
    import numpy as np
    from PIL import Image

    EASYOCR_AVAILABLE = True
except ImportError:
    easyocr = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]
    Image = None  # type: ignore[assignment]
    EASYOCR_AVAILABLE = False
    logger.info(
        "easyocr not installed. OCR features are disabled. "
        "Install with: pip install -r requirements-ocr.txt"
    )


# ---------- Cached reader ----------
_reader: Any = None


def _get_reader(languages: list[str] | None = None) -> Any:
    """Lazily create and cache an easyocr Reader."""
    global _reader
    if not EASYOCR_AVAILABLE:
        return None
    if _reader is None:
        langs = languages or ["en", "ar"]
        logger.info("Initializing easyocr reader for languages: %s", langs)
        _reader = easyocr.Reader(langs, gpu=False, verbose=False)
    return _reader


# ---------- Public API ----------
def is_available() -> bool:
    """Return True if OCR is available in this environment."""
    return EASYOCR_AVAILABLE


def extract_text_from_image(
    image_bytes: bytes,
    languages: list[str] | None = None,
) -> str:
    """
    Extract text from an image using OCR.

    Returns an empty string if OCR is not available or fails.
    """
    if not EASYOCR_AVAILABLE:
        logger.warning("OCR requested but easyocr is not installed.")
        return ""

    try:
        reader = _get_reader(languages)
        if reader is None:
            return ""

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_np = np.array(image)
        results = reader.readtext(image_np, detail=0, paragraph=True)
        return "\n".join(results).strip()

    except Exception as exc:
        logger.exception("OCR extraction failed: %s", exc)
        return ""


def extract_text_from_pdf_images(
    pdf_bytes: bytes,
    languages: list[str] | None = None,
) -> str:
    """
    Extract text from a scanned PDF (image-based).

    Renders each page to an image and runs OCR on it.
    """
    if not EASYOCR_AVAILABLE:
        logger.warning("OCR requested but easyocr is not installed.")
        return ""

    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        all_text: list[str] = []

        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            page_text = extract_text_from_image(img_bytes, languages)
            if page_text:
                all_text.append(page_text)

        doc.close()
        return "\n\n".join(all_text).strip()

    except Exception as exc:
        logger.exception("Scanned PDF OCR failed: %s", exc)
        return ""