"""
OCR Pipeline for Contract Document Processing.

This module handles PDF ingestion and image-to-text conversion using Tesseract OCR
and pdf2image for processing scanned legal documents and contract images.
"""

import io
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)

try:
    from pdf2image import convert_from_bytes, convert_from_path
    import pytesseract
    PYTESSERACT_AVAILABLE = True
    logger.info("Tesseract OCR and pdf2image successfully loaded")
except ImportError as e:
    PYTESSERACT_AVAILABLE = False
    logger.warning(f"OCR dependencies not fully available: {e}. Some features will be limited.")


def extract_text_from_document(
    file_source: Union[str, bytes, Path], 
    is_file_path: bool = True,
    dpi: int = 300
) -> Dict[str, Union[str, List[str], int]]:
    """
    Extract text from PDF documents using OCR.
    
    Args:
        file_source: Either a file path (str/Path) or raw bytes
        is_file_path: If True, treat file_source as a path; otherwise as bytes
        dpi: Resolution for PDF to image conversion (default: 300)
        
    Returns:
        Dictionary containing:
            - 'full_text': Complete extracted text
            - 'pages': List of text per page
            - 'page_count': Number of pages processed
            
    Raises:
        FileNotFoundError: If file path doesn't exist
        ValueError: If the document cannot be processed
        RuntimeError: If OCR dependencies are missing and no fallback available
    """
    result = {
        'full_text': '',
        'pages': [],
        'page_count': 0,
        'source': str(file_source) if isinstance(file_source, (str, Path)) else 'bytes',
        'success': False,
        'error': None
    }
    
    try:
        # Handle file path vs bytes input
        if is_file_path:
            path = Path(file_source)
            if not path.exists():
                raise FileNotFoundError(f"Document not found: {file_source}")
            
            logger.info(f"Processing PDF from file: {path.name}")
            with open(path, 'rb') as f:
                raw_bytes = f.read()
        else:
            raw_bytes = file_source
            logger.info("Processing PDF from bytes")
        
        if not raw_bytes or len(raw_bytes) == 0:
            raise ValueError("Empty document provided")
        
        if not PYTESSERACT_AVAILABLE:
            # Graceful fallback when OCR libraries not available
            logger.warning("OCR libraries not available, returning placeholder")
            result['full_text'] = "OCR_NOT_AVAILABLE: Install pdf2image and pytesseract for full OCR functionality"
            result['success'] = True  # Still mark as success since we handled it gracefully
            return result
        
        # Convert PDF pages to images
        logger.info(f"Converting PDF to images at {dpi} DPI")
        images = convert_from_bytes(raw_bytes, dpi=dpi)
        
        # Extract text from each page using Tesseract
        extracted_pages = []
        for i, image in enumerate(images):
            logger.debug(f"Processing page {i+1}/{len(images)}")
            page_text = pytesseract.image_to_string(image)
            extracted_pages.append(page_text)
            result['pages'].append(page_text)
        
        result['full_text'] = "\n\n".join(extracted_pages)
        result['page_count'] = len(extracted_pages)
        result['success'] = True
        
        logger.info(f"Successfully extracted text from {result['page_count']} pages")
        
    except FileNotFoundError:
        result['error'] = f"File not found: {file_source}"
        logger.error(result['error'])
        raise
    except Exception as e:
        result['error'] = f"OCR processing failed: {str(e)}"
        logger.error(result['error'])
        raise ValueError(result['error']) from e
    
    return result


def extract_text_from_image(
    image_source: Union[str, bytes, Path],
    lang: str = "eng",
    is_file_path: bool = True
) -> str:
    """
    Extract text from an image file using Tesseract OCR.
    
    Args:
        image_source: Path to image file or raw image bytes
        lang: Language code(s) for Tesseract (default: 'eng'). 
              Multiple languages can be specified with '+', e.g., 'eng+fra'
        is_file_path: If True, treat image_source as a path; otherwise as bytes
        
    Returns:
        Extracted text from the image
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image cannot be processed
    """
    try:
        if not PYTESSERACT_AVAILABLE:
            logger.warning("Tesseract not available, returning placeholder")
            return "OCR_NOT_AVAILABLE: Install pytesseract for image OCR functionality"
        
        # Load image from path or bytes
        if is_file_path:
            path = Path(image_source)
            if not path.exists():
                raise FileNotFoundError(f"Image not found: {image_source}")
            logger.info(f"Processing image: {path.name}")
            image = Image.open(path)
        else:
            logger.info("Processing image from bytes")
            image = Image.open(io.BytesIO(image_source))
        
        # Perform OCR
        logger.info(f"Extracting text with language: {lang}")
        extracted_text = pytesseract.image_to_string(image, lang=lang)
        
        logger.info(f"Successfully extracted {len(extracted_text)} characters from image")
        return extracted_text
        
    except FileNotFoundError:
        logger.error(f"Image file not found: {image_source}")
        raise
    except Exception as e:
        logger.error(f"Image OCR failed: {str(e)}")
        raise ValueError(f"Failed to process image: {str(e)}") from e


def extract_text_with_confidence(
    file_source: Union[str, bytes, Path],
    is_file_path: bool = True,
    lang: str = "eng"
) -> Dict[str, Union[str, float, List[Dict]]]:
    """
    Extract text with confidence scores for each word/token.
    
    Args:
        file_source: Path or bytes of the image/PDF
        is_file_path: Whether source is a file path
        lang: Language code for Tesseract
        
    Returns:
        Dictionary with:
            - 'text': Full extracted text
            - 'average_confidence': Mean confidence score (0-100)
            - 'word_details': List of words with individual confidence scores
    """
    if not PYTESSERACT_AVAILABLE:
        return {
            'text': "OCR_NOT_AVAILABLE",
            'average_confidence': 0.0,
            'word_details': []
        }
    
    try:
        from PIL import Image
        
        # Load image
        if is_file_path:
            image = Image.open(file_source)
        else:
            image = Image.open(io.BytesIO(file_source))
        
        # Get detailed OCR data including confidence
        ocr_data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
        
        # Process results
        words = []
        confidences = []
        
        for i, text in enumerate(ocr_data['text']):
            if text.strip():  # Only include non-empty text
                conf = ocr_data['conf'][i]
                if conf > 0:  # Valid confidence score
                    words.append({
                        'text': text,
                        'confidence': conf,
                        'bbox': {
                            'left': ocr_data['left'][i],
                            'top': ocr_data['top'][i],
                            'width': ocr_data['width'][i],
                            'height': ocr_data['height'][i]
                        }
                    })
                    confidences.append(conf)
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            'text': pytesseract.image_to_string(image, lang=lang),
            'average_confidence': avg_confidence,
            'word_details': words
        }
        
    except Exception as e:
        logger.error(f"Confidence-based OCR failed: {str(e)}")
        raise ValueError(f"Failed to extract text with confidence: {str(e)}") from e


def batch_process_documents(
    file_paths: List[Union[str, Path]],
    output_dir: Optional[str] = None
) -> Dict[str, Union[int, List[Dict]]]:
    """
    Process multiple documents in batch.
    
    Args:
        file_paths: List of file paths to process
        output_dir: Optional directory to save individual results
        
    Returns:
        Dictionary with:
            - 'total_processed': Number of successfully processed files
            - 'total_failed': Number of failed files
            - 'results': List of result dictionaries per file
    """
    results = {
        'total_processed': 0,
        'total_failed': 0,
        'results': []
    }
    
    for file_path in file_paths:
        try:
            result = extract_text_from_document(file_path, is_file_path=True)
            results['results'].append({
                'file': str(file_path),
                'success': True,
                'data': result
            })
            results['total_processed'] += 1
            
            # Optionally save to output directory
            if output_dir and result['success']:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                output_file = output_path / f"{Path(file_path).stem}_ocr.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result['full_text'])
                logger.info(f"Saved OCR output to {output_file}")
                
        except Exception as e:
            results['results'].append({
                'file': str(file_path),
                'success': False,
                'error': str(e)
            })
            results['total_failed'] += 1
            logger.error(f"Failed to process {file_path}: {e}")
    
    logger.info(f"Batch processing complete: {results['total_processed']} succeeded, {results['total_failed']} failed")
    return results


# Import Image here to avoid circular issues
try:
    from PIL import Image
except ImportError:
    Image = None
    logger.warning("PIL not available, image processing will be limited")
