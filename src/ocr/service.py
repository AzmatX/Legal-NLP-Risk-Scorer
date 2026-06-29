"""
Optimized OCR Pipeline for Contract Document Processing.
Supports Tesseract, EasyOCR, PaddleOCR with lazy loading & caching.
"""

import hashlib
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

logger = logging.getLogger(__name__)

CACHE_DIR = os.environ.get("OCR_CACHE_DIR", "/tmp/ocr_cache")


class OCRCache:
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, content: bytes) -> str:
        return hashlib.md5(content).hexdigest()

    def get(self, content: bytes) -> dict | None:
        cache_file = self.cache_dir / f"{self._get_cache_key(content)}.json"
        if cache_file.exists():
            try:
                with open(cache_file, encoding="utf-8") as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError, OSError):
                logger.warning("⚠️ Cache read failed – ignoring")
        return None

    def set(self, content: bytes, result: dict) -> None:
        cache_file = self.cache_dir / f"{self._get_cache_key(content)}.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(result, f)
        except OSError:
            logger.warning("⚠️ Cache write failed – continuing without cache")

    def clear(self) -> None:
        """Delete all cached OCR results."""
        for f in self.cache_dir.glob("*.json"):
            try:
                f.unlink()
            except OSError:
                pass
        logger.info("🧹 OCR cache cleared")


ocr_cache = OCRCache()


class OptimizedOCRProcessor:
    def __init__(
        self,
        preferred_engine: str = "auto",
        max_workers: int = 4,
        dpi: int = 300,
        use_cache: bool = True,
    ):
        self.preferred_engine = preferred_engine
        self.max_workers = max_workers
        self.dpi = dpi
        self.use_cache = use_cache

        # Engine availability flags
        self.tesseract_available = False
        self.easyocr_available = False
        self.paddleocr_available = False
        self.pdf2image_available = False

        # Singleton engine instances (lazy loading)
        self._tesseract = None
        self._easyocr_reader = None
        self._paddle_ocr = None

        self._detect_engines()

    def _detect_engines(self) -> None:
        # Tesseract
        try:
            import pytesseract

            pytesseract.get_tesseract_version()
            self.tesseract_available = True
            logger.info("✅ Tesseract available")
        except ImportError:
            logger.info("❌ Tesseract not available")

        # EasyOCR
        try:
            import easyocr  # noqa: F401

            self.easyocr_available = True
            logger.info("✅ EasyOCR available")
        except ImportError:
            logger.info("❌ EasyOCR not available")

        # PaddleOCR
        try:
            import paddleocr  # noqa: F401

            self.paddleocr_available = True
            logger.info("✅ PaddleOCR available")
        except ImportError:
            logger.info("❌ PaddleOCR not available")

        # pdf2image
        try:
            from pdf2image import convert_from_bytes  # noqa: F401

            self.pdf2image_available = True
            logger.info("✅ pdf2image available")
        except ImportError:
            logger.info("❌ pdf2image not available")

    def _get_tesseract(self):
        if self._tesseract is None and self.tesseract_available:
            import pytesseract

            self._tesseract = pytesseract
        return self._tesseract

    def _get_easyocr(self):
        if self._easyocr_reader is None and self.easyocr_available:
            import easyocr

            self._easyocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        return self._easyocr_reader

    def _get_paddleocr(self):
        if self._paddle_ocr is None and self.paddleocr_available:
            from paddleocr import PaddleOCR

            self._paddle_ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        return self._paddle_ocr

    def _select_engine(self) -> str:
        if self.preferred_engine != "auto":
            return self.preferred_engine
        if self.paddleocr_available:
            return "paddleocr"
        if self.easyocr_available:
            return "easyocr"
        if self.tesseract_available:
            return "tesseract"
        return "none"

    def extract_text_from_document(
        self, file_source, is_file_path: bool = True, use_parallel: bool = True
    ) -> dict:
        start_time = time.time()
        result = {
            "full_text": "",
            "pages": [],
            "page_count": 0,
            "success": False,
            "error": None,
            "engine_used": "none",
        }

        try:
            if is_file_path:
                path = Path(file_source)
                if not path.exists():
                    raise FileNotFoundError(f"File not found: {file_source}")
                with open(path, "rb") as f:
                    raw_bytes = f.read()
            else:
                raw_bytes = file_source

            if self.use_cache:
                cached = ocr_cache.get(raw_bytes)
                if cached:
                    return cached

            if not self.pdf2image_available:
                result["full_text"] = "pdf2image not installed. Run: pip install pdf2image"
                result["success"] = True
                return result

            from pdf2image import convert_from_bytes

            images = convert_from_bytes(raw_bytes, dpi=self.dpi)

            engine = self._select_engine()
            result["engine_used"] = engine

            if use_parallel and len(images) > 1:
                pages = self._process_pages_parallel(images, engine)
            else:
                pages = self._process_pages_sequential(images, engine)

            result["pages"] = pages
            result["full_text"] = "\n\n".join(pages)
            result["page_count"] = len(images)
            result["success"] = True
            result["processing_time"] = time.time() - start_time

            if self.use_cache:
                ocr_cache.set(raw_bytes, result)
            return result

        except Exception as e:
            result["error"] = str(e)
            return result

    def _process_pages_parallel(self, images, engine):
        results = [None] * len(images)
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {
                ex.submit(self._process_single_page, img, engine, i): i
                for i, img in enumerate(images)
            }
            for f in as_completed(futures):
                idx = futures[f]
                results[idx] = f.result() if f.exception() is None else f"[ERROR Page {idx + 1}]"
        return results

    def _process_pages_sequential(self, images, engine):
        return [self._process_single_page(img, engine, i) for i, img in enumerate(images)]

    def _process_single_page(self, image, engine, page_idx: int = 0) -> str:
        if engine == "tesseract":
            ocr = self._get_tesseract()
            if ocr:
                return ocr.image_to_string(image, config="--oem 3 --psm 6").strip()
        elif engine == "easyocr":
            reader = self._get_easyocr()
            if reader:
                return "\n".join([res[1] for res in reader.readtext(image)])
        elif engine == "paddleocr":
            ocr = self._get_paddleocr()
            if ocr:
                import numpy as np

                res = ocr.ocr(np.array(image), cls=True)
                if res and res[0]:
                    return "\n".join([line[1][0] for line in res[0]])
        return ""


# Global instance
_default_processor = None


def _get_default_processor() -> OptimizedOCRProcessor:
    global _default_processor
    if _default_processor is None:
        _default_processor = OptimizedOCRProcessor()
    return _default_processor


def extract_text_from_document(file_source, is_file_path: bool = True, dpi: int = 300) -> dict:
    p = _get_default_processor()
    p.dpi = dpi
    return p.extract_text_from_document(file_source, is_file_path)


def clear_ocr_cache() -> None:
    """Clear the OCR cache."""
    ocr_cache.clear()
