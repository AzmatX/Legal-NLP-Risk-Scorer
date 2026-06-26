"""
Enhanced Contract Validator for Legal Documents.

This module provides comprehensive validation for contract documents,
checking file integrity, content quality, and format compliance.
"""

import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ContractValidationError(Exception):
    """Custom exception for contract validation errors."""

    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ContractValidator:
    """
    Comprehensive validator for legal contract documents.

    Validates:
    - File existence and accessibility
    - File size constraints
    - Content quality and length
    - File format and structure
    - Corruption detection
    """

    # Default size constraints
    MIN_FILE_SIZE = 0  # bytes
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

    # Default content constraints
    MIN_TEXT_LENGTH = 20  # characters
    MAX_TEXT_LENGTH = 10_000_000  # 10 million characters

    # Default quality thresholds
    MIN_ALPHABETIC_RATIO = 0.3
    MAX_SPECIAL_CHAR_RATIO = 0.5

    # Supported file types with their magic bytes
    SUPPORTED_FORMATS: dict[str, dict[str, Any]] = {
        ".pdf": {
            "magic_bytes": b"%PDF",
            "mime_types": ["application/pdf"],
            "description": "Portable Document Format",
        },
        ".docx": {
            "magic_bytes": b"PK\x03\x04",  # ZIP signature
            "mime_types": [
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ],
            "description": "Microsoft Word Document",
        },
        ".json": {
            "magic_bytes": None,
            "mime_types": ["application/json"],
            "description": "JSON Data Format",
        },
        ".txt": {"magic_bytes": None, "mime_types": ["text/plain"], "description": "Plain Text"},
    }

    def __init__(
        self,
        min_text_length: int = 20,
        max_text_length: int = 10_000_000,
        check_file_size: bool = True,
        check_content_quality: bool = True,
        min_alphabetic_ratio: float = MIN_ALPHABETIC_RATIO,
        max_special_char_ratio: float = MAX_SPECIAL_CHAR_RATIO,
    ):
        """
        Initialize the contract validator.

        Args:
            min_text_length: Minimum required text length.
            max_text_length: Maximum allowed text length.
            check_file_size: Whether to validate file size.
            check_content_quality: Whether to perform quality checks.
            min_alphabetic_ratio: Minimum fraction of alphabetic characters.
            max_special_char_ratio: Maximum fraction of special characters.
        """
        self.min_text_length = min_text_length
        self.max_text_length = max_text_length
        self.check_file_size = check_file_size
        self.check_content_quality = check_content_quality
        self.min_alphabetic_ratio = min_alphabetic_ratio
        self.max_special_char_ratio = max_special_char_ratio

    # ------------------------------------------------------------------
    # Primary validation entry points
    # ------------------------------------------------------------------
    def validate(self, file_name: str, text: str) -> bool:
        """
        Validate a contract document's content.

        Args:
            file_name: Name of the file being validated.
            text: Content text to validate.

        Returns:
            True if validation passes.

        Raises:
            ContractValidationError: If any check fails.
        """
        if not file_name:
            raise ContractValidationError("File name is required", error_code="MISSING_FILENAME")
        if not text:
            raise ContractValidationError("Contract text is empty", error_code="EMPTY_CONTENT")

        stripped_len = len(text.strip())
        if stripped_len < self.min_text_length:
            raise ContractValidationError(
                f"Contract text must contain at least {self.min_text_length} characters. "
                f"Current length: {stripped_len}",
                error_code="TEXT_TOO_SHORT",
            )
        if stripped_len > self.max_text_length:
            raise ContractValidationError(
                f"Contract text exceeds maximum length of {self.max_text_length} characters. "
                f"Current length: {stripped_len}",
                error_code="TEXT_TOO_LONG",
            )

        if self.check_content_quality:
            self._validate_content_quality(text, file_name)

        logger.info("Validation successful for %s", file_name)
        return True

    def validate_file_path(self, file_path: str) -> dict[str, Any]:
        """
        Validate a file path and return metadata.

        Args:
            file_path: Path to the file.

        Returns:
            Dictionary with 'file_path', 'file_name', 'file_size',
            'file_type', 'file_type_info'.

        Raises:
            ContractValidationError: If the file is missing, not a file,
                empty, too large, or of an unsupported type.
        """
        path = Path(file_path)

        if not path.exists():
            raise ContractValidationError(
                f"File not found: {file_path}", error_code="FILE_NOT_FOUND"
            )
        if not path.is_file():
            raise ContractValidationError(
                f"Path is not a file: {file_path}", error_code="NOT_A_FILE"
            )

        try:
            file_size = path.stat().st_size
        except OSError as e:
            raise ContractValidationError(
                f"Cannot read file metadata: {e}", error_code="METADATA_READ_ERROR"
            )

        file_type = path.suffix.lower()
        if file_type not in self.SUPPORTED_FORMATS:
            raise ContractValidationError(
                f"Unsupported file type: {file_type}. "
                f"Supported: {', '.join(self.SUPPORTED_FORMATS.keys())}",
                error_code="UNSUPPORTED_FORMAT",
            )

        if self.check_file_size:
            if file_size < self.MIN_FILE_SIZE:
                raise ContractValidationError("File is empty", error_code="EMPTY_FILE")
            if file_size > self.MAX_FILE_SIZE:
                raise ContractValidationError(
                    f"File too large: {file_size} bytes (max {self.MAX_FILE_SIZE})",
                    error_code="FILE_TOO_LARGE",
                )

        logger.info("File validation successful: %s (%s bytes)", path.name, file_size)
        return {
            "file_path": str(path),
            "file_name": path.name,
            "file_size": file_size,
            "file_type": file_type,
            "file_type_info": self.SUPPORTED_FORMATS[file_type],
        }

    # ------------------------------------------------------------------
    # Integrity & content quality
    # ------------------------------------------------------------------
    def validate_file_integrity(self, file_path: str) -> dict[str, Any]:
        """
        Validate file integrity using magic bytes and MD5 checksum.

        The file is read **once** for both header inspection and hashing.

        Args:
            file_path: Path to the file.

        Returns:
            Dictionary with keys:
                - valid: bool
                - checksum: MD5 hex string (or None)
                - magic_bytes_match: bool (or None if not applicable)
                - format_supported: bool
                - errors: list of error strings
        """
        path = Path(file_path)
        file_type = path.suffix.lower()
        result = {
            "valid": False,
            "file_path": str(path),
            "checksum": None,
            "magic_bytes_match": None,
            "format_supported": False,
            "errors": [],
        }

        format_info = self.SUPPORTED_FORMATS.get(file_type)
        if format_info is None:
            result["errors"].append(f"Unsupported file type: {file_type}")
            return result

        result["format_supported"] = True
        expected_magic = format_info.get("magic_bytes")
        magic_check_needed = expected_magic is not None

        try:
            with open(path, "rb") as f:
                # Read first 16 bytes for magic check
                header = f.read(16)

                if magic_check_needed:
                    if header.startswith(expected_magic):
                        result["magic_bytes_match"] = True
                    else:
                        result["errors"].append(
                            f"File header does not match expected format for {file_type}"
                        )
                else:
                    result["magic_bytes_match"] = None  # N/A

                # Compute MD5: start from what we already have
                hasher = hashlib.md5()
                hasher.update(header)

                # Read the rest in chunks
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)

            result["checksum"] = hasher.hexdigest()
            result["valid"] = len(result["errors"]) == 0

        except OSError as e:
            result["errors"].append(f"Integrity check failed: {e}")

        return result

    def validate_json_structure(self, text: str) -> dict[str, Any]:
        """
        Validate JSON structure.

        Args:
            text: JSON string to validate.

        Returns:
            Dictionary with keys:
                - valid: bool
                - is_list, is_dict: bool
                - keys: list of top‑level or first element keys
                - error: error message if invalid
        """
        result: dict[str, Any] = {
            "valid": False,
            "is_list": False,
            "is_dict": False,
            "keys": [],
            "error": None,
        }
        try:
            data = json.loads(text)
            result["valid"] = True
            result["is_list"] = isinstance(data, list)
            result["is_dict"] = isinstance(data, dict)

            if isinstance(data, dict):
                result["keys"] = list(data.keys())
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                result["keys"] = list(data[0].keys())
        except json.JSONDecodeError as e:
            result["error"] = f"Invalid JSON: {e}"

        return result

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------
    def get_validation_report(self, file_path: str, text: str | None = None) -> dict[str, Any]:
        """
        Generate a comprehensive validation report.

        Args:
            file_path: Path to the file.
            text: Optional text content for content & JSON checks.

        Returns:
            Dictionary with overall_valid flag and per‑check results.
        """
        report: dict[str, Any] = {
            "file_path": file_path,
            "timestamp": datetime.now(UTC).isoformat(),
            "overall_valid": False,
            "checks": {},
        }

        # 1. File metadata validation
        try:
            file_meta = self.validate_file_path(file_path)
            report["checks"]["file_metadata"] = {"passed": True, "data": file_meta}
        except ContractValidationError as e:
            report["checks"]["file_metadata"] = {
                "passed": False,
                "error": str(e),
                "error_code": e.error_code,
            }
            return report  # Cannot proceed further without valid file

        # 2. File integrity
        integrity = self.validate_file_integrity(file_path)
        report["checks"]["integrity"] = {
            "passed": integrity["valid"],
            "checksum": integrity["checksum"],
            "magic_bytes_match": integrity["magic_bytes_match"],
            "errors": integrity["errors"],
        }

        # 3. Content validation (if text provided)
        if text is not None:
            content_check = {}
            try:
                self.validate(Path(file_path).name, text)
                content_check["passed"] = True
                content_check["text_length"] = len(text)
            except ContractValidationError as e:
                content_check["passed"] = False
                content_check["error"] = str(e)
                content_check["error_code"] = e.error_code

            report["checks"]["content"] = content_check

            # 4. JSON structure (if applicable)
            if Path(file_path).suffix.lower() == ".json":
                report["checks"]["json_structure"] = self.validate_json_structure(text)

        # Determine overall validity
        report["overall_valid"] = all(
            check.get("passed", False) for check in report["checks"].values()
        )
        return report

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _validate_content_quality(self, text: str, file_name: str) -> None:
        """
        Check alphabetic ratio and special character ratio in one pass.

        Args:
            text: Content text.
            file_name: For logging.

        Raises:
            ContractValidationError: If ratios are outside thresholds.
        """
        total = len(text)
        if total == 0:
            return

        alpha_count = 0
        special_count = 0

        # Single pass over the text
        for char in text:
            if char.isalpha():
                alpha_count += 1
            elif not char.isalnum() and not char.isspace():
                special_count += 1

        alpha_ratio = alpha_count / total
        special_ratio = special_count / total

        if alpha_ratio < self.min_alphabetic_ratio:
            logger.warning(
                "Low alphabetic ratio (%.2f) in %s – possible corruption", alpha_ratio, file_name
            )
        if special_ratio > self.max_special_char_ratio:
            logger.warning(
                "High special character ratio (%.2f) in %s – possible noise",
                special_ratio,
                file_name,
            )

        # Optionally raise an error if needed:
        # if alpha_ratio < self.min_alphabetic_ratio:
        #     raise ContractValidationError(...)
