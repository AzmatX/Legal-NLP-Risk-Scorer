"""
Enhanced Contract Validator for Legal Documents.

This module provides comprehensive validation for contract documents,
checking file integrity, content quality, and format compliance.
"""

import hashlib
import logging
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

    # Size constraints
    MIN_FILE_SIZE = 0  # bytes
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

    # Content constraints
    MIN_TEXT_LENGTH = 20  # characters
    MAX_TEXT_LENGTH = 10_000_000  # 10 million characters

    # Quality thresholds
    MIN_ALPHABETIC_RATIO = 0.3  # At least 30% alphabetic characters
    MAX_SPECIAL_CHAR_RATIO = 0.5  # No more than 50% special characters

    # Supported file types with their magic bytes
    SUPPORTED_FORMATS = {
        '.pdf': {
            'magic_bytes': b'%PDF',
            'mime_types': ['application/pdf'],
            'description': 'Portable Document Format'
        },
        '.docx': {
            'magic_bytes': b'PK\x03\x04',  # ZIP signature
            'mime_types': [
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
],
            'description': 'Microsoft Word Document'
        },
        '.json': {
            'magic_bytes': None,  # Text-based, no magic bytes
            'mime_types': ['application/json'],
            'description': 'JSON Data Format'
        },
        '.txt': {
            'magic_bytes': None,
            'mime_types': ['text/plain'],
            'description': 'Plain Text'
        }
    }

    def __init__(
        self,
        min_text_length: int = 20,
        max_text_length: int = 10_000_000,
        check_file_size: bool = True,
        check_content_quality: bool = True
    ):
        """
        Initialize the contract validator.

        Args:
            min_text_length: Minimum required text length
            max_text_length: Maximum allowed text length
            check_file_size: Whether to validate file size
            check_content_quality: Whether to perform quality checks
        """
        self.min_text_length = min_text_length
        self.max_text_length = max_text_length
        self.check_file_size = check_file_size
        self.check_content_quality = check_content_quality

    def validate(self, file_name: str, text: str) -> bool:
        """
        Validate a contract document.

        Args:
            file_name: Name of the file being validated
            text: Content text to validate

        Returns:
            True if validation passes

        Raises:
            ContractValidationError: If validation fails
        """
        if not file_name:
            raise ContractValidationError(
                "File name is required",
                error_code="MISSING_FILENAME"
            )

        if not text:
            raise ContractValidationError(
                "Contract text is empty",
                error_code="EMPTY_CONTENT"
            )

        # Validate text length
        text_length = len(text.strip())
        if text_length < self.min_text_length:
            raise ContractValidationError(
                f"Contract text must contain at least {self.min_text_length} characters. "
                f"Current length: {text_length}",
                error_code="TEXT_TOO_SHORT"
            )

        if text_length > self.max_text_length:
            raise ContractValidationError(
                f"Contract text exceeds maximum length of {self.max_text_length} characters. "
                f"Current length: {text_length}",
                error_code="TEXT_TOO_LONG"
            )

        # Perform content quality checks
        if self.check_content_quality:
            self._validate_content_quality(text, file_name)

        logger.info(f"Validation successful for {file_name}")
        return True

    def validate_file_path(self, file_path: str) -> dict[str, Any]:
        """
        Validate a file path and return file metadata.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary containing file metadata

        Raises:
            ContractValidationError: If file validation fails
        """
        path = Path(file_path)

        result = {
            'valid': False,
            'file_path': str(path),
            'file_name': path.name,
            'file_size': 0,
            'file_type': path.suffix.lower(),
            'errors': []
        }

        # Check existence
        if not path.exists():
            result['errors'].append(f"File not found: {file_path}")
            raise ContractValidationError(
                f"File not found: {file_path}",
                error_code="FILE_NOT_FOUND"
            )

        # Check if it's a file (not directory)
        if not path.is_file():
            result['errors'].append(f"Path is not a file: {file_path}")
            raise ContractValidationError(
                f"Path is not a file: {file_path}",
                error_code="NOT_A_FILE"
            )

        # Check file size
        try:
            file_size = path.stat().st_size
            result['file_size'] = file_size

            if self.check_file_size:
                if file_size < self.MIN_FILE_SIZE:
                    result['errors'].append("File is empty")
                    raise ContractValidationError(
                        "File is empty",
                        error_code="EMPTY_FILE"
                    )

                if file_size > self.MAX_FILE_SIZE:
                    result['errors'].append(
                        f"File size ({file_size} bytes) exceeds maximum "
                        f"allowed ({self.MAX_FILE_SIZE} bytes)"
                    )
                    raise ContractValidationError(
                        f"File too large: {file_size} bytes",
                        error_code="FILE_TOO_LARGE"
                    )
        except OSError as e:
            result['errors'].append(f"Cannot read file meta {e}")
            raise ContractValidationError(
                f"Cannot read file meta {e}",
                error_code="METADATA_READ_ERROR"
            )

        # Check file type
        file_type = path.suffix.lower()
        if file_type not in self.SUPPORTED_FORMATS:
            result['errors'].append(
                f"Unsupported file type: {file_type}. "
                f"Supported types: {', '.join(self.SUPPORTED_FORMATS.keys())}"
            )
            raise ContractValidationError(
                f"Unsupported file type: {file_type}",
                error_code="UNSUPPORTED_FORMAT"
            )

        result['valid'] = True
        result['file_type_info'] = self.SUPPORTED_FORMATS[file_type]

        logger.info(f"File validation successful: {path.name} ({file_size} bytes)")
        return result

    def validate_file_integrity(self, file_path: str) -> dict[str, Any]:
        """
        Validate file integrity using magic bytes and checksums.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary containing integrity check results
        """
        path = Path(file_path)
        file_type = path.suffix.lower()

        result = {
            'valid': False,
            'file_path': str(path),
            'checksum': None,
            'magic_bytes_match': False,
            'errors': []
        }

        if file_type not in self.SUPPORTED_FORMATS:
            result['errors'].append(f"Unknown file type: {file_type}")
            return result

        format_info = self.SUPPORTED_FORMATS[file_type]

        try:
            # Read first few bytes for magic byte check
            with open(path, 'rb') as f:
                header = f.read(16)

            # Check magic bytes if defined for this format
            if format_info.get('magic_bytes'):
                expected_magic = format_info['magic_bytes']
                if header.startswith(expected_magic):
                    result['magic_bytes_match'] = True
                else:
                    result['errors'].append(
                        f"File header does not match expected format for {file_type}"
                    )

            # Calculate MD5 checksum
            md5_hash = hashlib.md5()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    md5_hash.update(chunk)

            result['checksum'] = md5_hash.hexdigest()
            result['valid'] = len(result['errors']) == 0

        except Exception as e:
            result['errors'].append(f"Integrity check failed: {e}")

        return result

    def _validate_content_quality(self, text: str, file_name: str) -> None:
        """
        Validate content quality metrics.

        Args:
            text: Content text to validate
            file_name: Name of the file for logging

        Raises:
            ContractValidationError: If quality checks fail
        """
        if not text:
            return

        total_chars = len(text)

        # Calculate alphabetic ratio
        alphabetic_count = sum(1 for c in text if c.isalpha())
        alphabetic_ratio = alphabetic_count / total_chars if total_chars > 0 else 0

        if alphabetic_ratio < self.MIN_ALPHABETIC_RATIO:
            logger.warning(
                f"Low alphabetic ratio ({alphabetic_ratio:.2f}) in {file_name}. "
                f"Text may be corrupted or contain excessive noise."
            )

        # Calculate special character ratio
        special_chars = sum(
            1 for c in text
            if not c.isalnum() and not c.isspace()
        )
        special_ratio = special_chars / total_chars if total_chars > 0 else 0

        if special_ratio > self.MAX_SPECIAL_CHAR_RATIO:
            logger.warning(
                f"High special character ratio ({special_ratio:.2f}) in {file_name}. "
                f"Text may contain excessive formatting or corruption."
            )

    def validate_json_structure(self, text: str) -> dict[str, Any]:
        """
        Validate JSON structure for JSON files.

        Args:
            text: JSON text to validate

        Returns:
            Dictionary with validation results
        """
        import json

        result = {
            'valid': False,
            'is_list': False,
            'is_dict': False,
            'keys': [],
            'error': None
        }

        try:
            data = json.loads(text)
            result['valid'] = True
            result['is_list'] = isinstance(data, list)
            result['is_dict'] = isinstance(data, dict)

            if isinstance(data, dict):
                result['keys'] = list(data.keys())
            elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                result['keys'] = list(data[0].keys())

        except json.JSONDecodeError as e:
            result['error'] = f"Invalid JSON: {e}"

        return result

    def get_validation_report(
        self,
        file_path: str,
        text: str | None = None
    ) -> dict[str, Any]:
        """
        Generate a comprehensive validation report.

        Args:
            file_path: Path to the file
            text: Optional text content for additional checks

        Returns:
            Dictionary containing complete validation report
        """
        report = {
            'file_path': file_path,
            'timestamp': None,
            'overall_valid': False,
            'checks': {}
        }

        from datetime import datetime
        report['timestamp'] = datetime.utcnow().isoformat()

        # File path validation
        try:
            file_meta = self.validate_file_path(file_path)
            report['checks']['file_metadata'] = {
                'passed': True,
                'data': file_meta
            }
        except ContractValidationError as e:
            report['checks']['file_metadata'] = {
                'passed': False,
                'error': str(e),
                'error_code': e.error_code
            }
            return report

        # File integrity check
        integrity_result = self.validate_file_integrity(file_path)
        report['checks']['integrity'] = {
            'passed': integrity_result['valid'],
            'checksum': integrity_result['checksum'],
            'magic_bytes_match': integrity_result['magic_bytes_match'],
            'errors': integrity_result['errors']
        }

        # Content validation (if text provided)
        if text:
            try:
                self.validate(Path(file_path).name, text)
                report['checks']['content'] = {
                    'passed': True,
                    'text_length': len(text)
                }

                # JSON structure check if applicable
                if Path(file_path).suffix.lower() == '.json':
                    json_result = self.validate_json_structure(text)
                    report['checks']['json_structure'] = json_result

            except ContractValidationError as e:
                report['checks']['content'] = {
                    'passed': False,
                    'error': str(e),
                    'error_code': e.error_code
                }

        # Determine overall validity
        report['overall_valid'] = all(
            check.get('passed', False)
            for check in report['checks'].values()
        )

        return report
