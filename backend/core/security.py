"""
TARGET-X Security Utilities
Protects backend from malicious filenames, oversized uploads, and directory traversal.
"""

import os
import re
from pathlib import Path
from fastapi import HTTPException
from backend.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE_BYTES


def sanitize_filename(filename: str) -> str:
    """Removes path separators and non-whitelisted characters from upload filenames."""
    name = os.path.basename(filename)
    # Only alphanumeric, dashes, dots, and underscores
    sanitized = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", name)
    return sanitized


def validate_upload(filename: str, file_size: int = None):
    """Validates video extension and size limits."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid video format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    if file_size and file_size > MAX_UPLOAD_SIZE_BYTES:
        max_mb = MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum permitted size of {max_mb}MB"
        )
