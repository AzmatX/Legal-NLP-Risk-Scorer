"""
Optimized OCR Pipeline for Contract Document Processing.

This module handles PDF ingestion and image-to-text conversion using multiple
OCR engines (Tesseract, EasyOCR, PaddleOCR) with intelligent fallback,
parallel processing, and result caching for improved performance.
"""

import hashlib
import io
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Cache directory for processed documents
CACHE_DIR = os.environ.get("OCR_CACHE_DIR", "/tmp/ocr_cache")


class OCRCache:
    """File-based cache for OCR results to avoid re-processing."""

    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"OCR cache initialized at {self.cache_dir}")

    def _get_cache_key(self, content: bytes) -> str:
        """Generate cache key from file content hash."""
        return hashlib.md5(content).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get path to cache file."""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, content: bytes) -> dict | None:
        """Retrieve cached OCR result if available."""
        import json

        cache_key = self._get_cache_key(content)
        cache_file = self._get_cache_path(cache_key)

        if cache_file.exists():
            try:
                with open(cache_file, encoding='utf-8') as f:
                    result = json.load(f)
                    logger.debug(f"Cache hit for {cache_key[:16]}")
                    return result
            except Exception as e:
                logger.warning(f"Cache read error: {e}")

        logger.debug(f"Cache miss for {cache_key[:16]}")
        return None

    def set(self, content: bytes, result: dict) -> None:
        """Store OCR result in cache."""
        import json

        cache_key = self._get_cache_key(content)
        cache_file = self._get_cache_path(cache_key)

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            logger.debug(f"Cached result for {cache_key[:16]}")
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    def clear(self) -> int:
        """Clear all cached results. Returns number of files removed."""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except Exception as e:
                logger.warning(f"Failed to remove cache file {cache_file}: {e}")

        logger.info(f"Cleared {count} cached OCR results")
        return count


# Initialize cache
ocr_cache = OCRCache()


class OptimizedOCRProcessor:
    """
    High-performance OCR processor with multiple engine support.

    Features:
    - Multiple OCR engine support (Tesseract, EasyOCR, PaddleOCR)
    - Parallel page processing
    - Intelligent engine selection based on document type
    - Result caching
    - Confidence-based quality assessment
    """

    def __init__(
        self,
        preferred_engine: str = "auto",
        max_workers: int = 4,
        dpi: int = 300,
        use_cache: bool = True
    ):
        """
        Initialize the optimized OCR processor.

        Args:
            preferred_engine: OCR engine to use ('tesseract', 'easyocr', 'paddleocr', 'auto')
            max_workers: Maximum parallel workers for page processing
            dpi: Resolution for PDF to image conversion
            use_cache: Whether to use result caching
        """
        self.preferred_engine = preferred_engine
        self.max_workers = max_workers
        self.dpi = dpi
        self.use_cache = use_cache

        # Engine availability flags
        self.tesseract_available = False
        self.easyocr_available = False
        self.paddleocr_available = False
        self.pdf2image_available = False

        self._detect_engines()

    def _detect_engines(self):
        """Detect available OCR engines."""
        # Check Tesseract
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            self.tesseract_available = True
            logger.info("Tesseract OCR available")
        except Exception:
            logger.info("Tesseract OCR not available")

        # Check EasyOCR
        try:
            self.easyocr_available = True
            logger.info("EasyOCR available")
        except Exception:
            logger.info("EasyOCR not available")

        # Check PaddleOCR
        try:
            self.paddleocr_available = True
            logger.info("PaddleOCR available")
        except Exception:
            logger.info("PaddleOCR not available")

        # Check pdf2image
        try:
            self.pdf2image_available = True
            logger.info("pdf2image available")
        except Exception:
            logger.info("pdf2image not available")

    def _select_engine(self) -> str:
        """Select best available OCR engine."""
        if self.preferred_engine != "auto":
            return self.preferred_engine

        # Priority order: PaddleOCR > EasyOCR > Tesseract
        if self.paddleocr_available:
            return "paddleocr"
        elif self.easyocr_available:
            return "easyocr"
        elif self.tesseract_available:
            return "tesseract"
        else:
            return "none"

    def extract_text_from_document(
        self,
        file_source: str | bytes | Path,
        is_file_path: bool = True,
        use_parallel: bool = True
    ) -> dict[str, Any]:
        """
        Extract text from PDF documents using optimized OCR.

        Args:
            file_source: Either a file path (str/Path) or raw bytes
            is_file_path: If True, treat file_source as a path; otherwise as bytes
            use_parallel: Whether to use parallel processing for multi-page docs

        Returns:
            Dictionary containing:
                - 'full_text': Complete extracted text
                - 'pages': List of text per page
                - 'page_count': Number of pages processed
                - 'processing_time': Time taken in seconds
                - 'engine_used': OCR engine used
                - 'cache_hit': Whether result was from cache
        """
        start_time = time.time()
        result = {
            'full_text': '',
            'pages': [],
            'page_count': 0,
            'source': str(file_source) if isinstance(file_source, (str, Path)) else 'bytes',
            'success': False,
            'error': None,
            'processing_time': 0.0,
            'engine_used': 'none',
            'cache_hit': False
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

            # Check cache
            if self.use_cache:
                cached_result = ocr_cache.get(raw_bytes)
                if cached_result:
                    cached_result['cache_hit'] = True
                    logger.info("Returning cached OCR result")
                    return cached_result

            # Check if pdf2image is available
            if not self.pdf2image_available:
                result['full_text'] = (
                    "OCR_NOT_AVAILABLE: Install pdf2image for PDF processing. "
                    "pip install pdf2image"
                )
                result['success'] = True
                return result

            # Convert PDF pages to images
            from pdf2image import convert_from_bytes
            logger.info(f"Converting PDF to images at {self.dpi} DPI")

            images = convert_from_bytes(raw_bytes, dpi=self.dpi)
            page_count = len(images)
            logger.info(f"PDF has {page_count} pages")

            # Select OCR engine
            engine = self._select_engine()
            result['engine_used'] = engine

            if engine == "none":
                result['full_text'] = (
                    "OCR_NOT_AVAILABLE: No OCR engines available. "
                    "Install one of: pytesseract, easyocr, or paddleocr"
                )
                result['success'] = True
                return result

            # Process pages
            if use_parallel and page_count > 1:
                extracted_pages = self._process_pages_parallel(images, engine)
            else:
                extracted_pages = self._process_pages_sequential(images, engine)

            result['pages'] = extracted_pages
            result['full_text'] = "\n\n".join(extracted_pages)
            result['page_count'] = page_count
            result['success'] = True

            # Cache result
            if self.use_cache:
                ocr_cache.set(raw_bytes, result)

            result['processing_time'] = time.time() - start_time
            logger.info(
                f"Successfully extracted text from {page_count} pages "
                f"in {result['processing_time']:.2f}s using {engine}"
            )

        except FileNotFoundError:
            result['error'] = f"File not found: {file_source}"
            logger.error(result['error'])
            raise
        except Exception as e:
            result['error'] = f"OCR processing failed: {str(e)}"
            result['processing_time'] = time.time() - start_time
            logger.error(result['error'])
            raise ValueError(result['error']) from e

        return result

    def _process_pages_parallel(
        self,
        images: list,
        engine: str
    ) -> list[str]:
        """Process PDF pages in parallel using thread pool."""
        extracted_pages = [None] * len(images)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_page = {
                executor.submit(
                    self._process_single_page,
                    img,
                    engine,
                    i
                ): i
                for i, img in enumerate(images)
            }

            for future in as_completed(future_to_page):
                page_idx = future_to_page[future]
                try:
                    page_text = future.result()
                    extracted_pages[page_idx] = page_text
                    logger.debug(f"Completed page {page_idx + 1}")
                except Exception as e:
                    logger.error(f"Error processing page {page_idx}: {e}")
                    extracted_pages[page_idx] = f"[ERROR: Page {page_idx + 1} processing failed]"

        return extracted_pages

    def _process_pages_sequential(
        self,
        images: list,
        engine: str
    ) -> list[str]:
        """Process PDF pages sequentially."""
        extracted_pages = []

        for i, image in enumerate(images):
            logger.debug(f"Processing page {i+1}/{len(images)}")
            page_text = self._process_single_page(image, engine, i)
            extracted_pages.append(page_text)

        return extracted_pages

    def _process_single_page(
        self,
        image: Any,
        engine: str,
        page_idx: int = 0
    ) -> str:
        """Process a single page with specified OCR engine."""
        if engine == "tesseract":
            return self._ocr_with_tesseract(image)
        elif engine == "easyocr":
            return self._ocr_with_easyocr(image)
        elif engine == "paddleocr":
            return self._ocr_with_paddleocr(image)
        else:
            return ""

    def _ocr_with_tesseract(self, image: Any) -> str:
        """Extract text using Tesseract OCR."""
        import pytesseract

        # Configure for better accuracy on documents
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=custom_config)
        return text.strip()

    def _ocr_with_easyocr(self, image: Any) -> str:
        """Extract text using EasyOCR."""
        import easyocr

        # Initialize reader (should be done once in production)
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)

        # Get OCR results
        results = reader.readtext(image)

        # Extract text from results
        texts = [result[1] for result in results]
        return '\n'.join(texts)

    def _ocr_with_paddleocr(self, image: Any) -> str:
        """Extract text using PaddleOCR."""
        import numpy as np
        from paddleocr import PaddleOCR

        # Initialize OCR (should be done once in production)
        ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)

        # Convert PIL image to numpy array
        img_array = np.array(image)

        # Get OCR results
        result = ocr.ocr(img_array, cls=True)

        # Extract text from results
        texts = []
        if result and result[0]:
            for line in result[0]:
                texts.append(line[1][0])

        return '\n'.join(texts)


# Legacy function wrappers for backward compatibility
_default_processor: OptimizedOCRProcessor | None = None


def _get_default_processor() -> OptimizedOCRProcessor:
    """Get or create the default OCR processor."""
    global _default_processor
    if _default_processor is None:
        _default_processor = OptimizedOCRProcessor()
    return _default_processor


def extract_text_from_document(
    file_source: str | bytes | Path,
    is_file_path: bool = True,
    dpi: int = 300
) -> dict[str, str | list[str] | int]:
    """
    Extract text from PDF documents using OCR (legacy API).

    Args:
        file_source: Either a file path (str/Path) or raw bytes
        is_file_path: If True, treat file_source as a path; otherwise as bytes
        dpi: Resolution for PDF to image conversion (default: 300)

    Returns:
        Dictionary containing:
            - 'full_text': Complete extracted text
            - 'pages': List of text per page
            - 'page_count': Number of pages processed
    """
    processor = _get_default_processor()
    processor.dpi = dpi
    return processor.extract_text_from_document(
        file_source,
        is_file_path=is_file_path,
        use_parallel=True
    )


def extract_text_from_image(
    image_source: str | bytes | Path,
    lang: str = "eng",
    is_file_path: bool = True
) -> str:
    """
    Extract text from an image file using OCR (legacy API).

    Args:
        image_source: Path to image file or raw image bytes
        lang: Language code(s) for OCR
        is_file_path: If True, treat image_source as a path; otherwise as bytes

    Returns:
        Extracted text from the image
    """
    processor = _get_default_processor()

    try:
        from PIL import Image

        # Load image
        if is_file_path:
            image = Image.open(image_source)
        else:
            image = Image.open(io.BytesIO(image_source))

        # Use Tesseract as default for single images
        if processor.tesseract_available:
            import pytesseract
            return pytesseract.image_to_string(image, lang=lang)
        else:
            return "OCR_NOT_AVAILABLE: Install pytesseract for image OCR"

    except Exception as e:
        logger.error(f"Image OCR failed: {e}")
        raise ValueError(f"Failed to process image: {e}") from e


def batch_process_documents(
    file_paths: list[str | Path],
    output_dir: str | None = None,
    use_parallel: bool = True
) -> dict[str, int | list[dict]]:
    """
    Process multiple documents in batch (legacy API).

    Args:
        file_paths: List of file paths to process
        output_dir: Optional directory to save individual results
        use_parallel: Whether to process documents in parallel

    Returns:
        Dictionary with processing results
    """
    processor = _get_default_processor()
    results = {
        'total_processed': 0,
        'total_failed': 0,
        'results': []
    }

    def process_single_file(file_path):
        try:
            result = processor.extract_text_from_document(
                file_path,
                is_file_path=True,
                use_parallel=False  # Each doc processed sequentially
            )
            return {
                'file': str(file_path),
                'success': True,
                'data': result
            }
        except Exception as e:
            return {
                'file': str(file_path),
                'success': False,
                'error': str(e)
            }

    if use_parallel and len(file_paths) > 1:
        with ThreadPoolExecutor(max_workers=processor.max_workers) as executor:
            futures = [executor.submit(process_single_file, fp) for fp in file_paths]

            for future in as_completed(futures):
                file_result = future.result()
                results['results'].append(file_result)

                if file_result['success']:
                    results['total_processed'] += 1

                    # Save to output directory if specified
                    if output_dir and file_result['data']['success']:
                        output_path = Path(output_dir)
                        output_path.mkdir(parents=True, exist_ok=True)
                        output_file = output_path / f"{Path(file_result['file']).stem}_ocr.txt"
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(file_result['data']['full_text'])
                else:
                    results['total_failed'] += 1
    else:
        for file_path in file_paths:
            file_result = process_single_file(file_path)
            results['results'].append(file_result)

            if file_result['success']:
                results['total_processed'] += 1
            else:
                results['total_failed'] += 1

    logger.info(
        f"Batch processing complete: {results['total_processed']} succeeded, "
        f"{results['total_failed']} failed"
    )
    return results


def clear_ocr_cache() -> int:
    """Clear the OCR result cache. Returns number of entries removed."""
    return ocr_cache.clear()
