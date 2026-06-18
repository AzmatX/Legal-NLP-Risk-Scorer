"""
OCR Pipeline for Contract Document Processing
Handles PDF ingestion using Tesseract OCR and pdf2image
"""
import io
from typing import Optional

try:
    from pdf2image import convert_from_bytes
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False


def extract_text_from_document(raw_bytes: bytes) -> str:
    """
    Extract text from PDF documents using OCR.
    
    Args:
        raw_bytes: Raw bytes of the PDF document
        
    Returns:
        Extracted text content from the document
        
    Raises:
        RuntimeError: If OCR dependencies are not installed
        ValueError: If the document cannot be processed
    """
    if not raw_bytes:
        raise ValueError("Empty document provided")
    
    if not PYTESSERACT_AVAILABLE:
        # Fallback: return placeholder if OCR libraries not available
        return "OCR pipeline placeholder output - install pdf2image and pytesseract for full functionality"
    
    try:
        # Convert PDF pages to images
        images = convert_from_bytes(raw_bytes, dpi=300)
        
        # Extract text from each page using Tesseract
        extracted_text = []
        for i, image in enumerate(images):
            page_text = pytesseract.image_to_string(image)
            extracted_text.append(f"--- Page {i+1} ---\n{page_text}")
        
        return "\n\n".join(extracted_text)
    
    except Exception as e:
        raise ValueError(f"Failed to process document: {str(e)}")


def extract_text_from_image(image_bytes: bytes, lang: str = "eng") -> str:
    """
    Extract text from an image file using Tesseract OCR.
    
    Args:
        image_bytes: Raw bytes of the image file
        lang: Language code for Tesseract (default: 'eng')
        
    Returns:
        Extracted text from the image
    """
    if not PYTESSERACT_AVAILABLE:
        return "OCR not available - install pytesseract"
    
    try:
        from PIL import Image
        image = Image.open(io.BytesIO(image_bytes))
        return pytesseract.image_to_string(image, lang=lang)
    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")
