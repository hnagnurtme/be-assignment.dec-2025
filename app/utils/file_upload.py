import os
import shutil
import uuid
from typing import BinaryIO

from fastapi import UploadFile
from app.core.exceptions import BadRequestException


class FileUploadService:
    """Service to handle file uploads."""

    UPLOAD_DIR = os.path.join("storage", "uploads")
    # Extended list of allowed extensions for better security
    ALLOWED_EXTENSIONS = {
        # Images
        ".jpg", ".jpeg", ".png", ".gif", ".webp",
        # Documents
        ".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx",
        # Archives
        ".zip", ".rar",
        # Code/Data
        ".json", ".xml", ".csv"
    }
    
    @classmethod
    def validate_file(
        cls, 
        file: UploadFile, 
        max_size_mb: int = 5, 
        allowed_extensions: set[str] | None = None
    ) -> None:
        """
        Validate file size and extension.
        
        Args:
            file: The uploaded file.
            max_size_mb: Maximum file size in megabytes.
            allowed_extensions: Set of allowed file extensions (e.g. {'.jpg', '.png'}). 
                                If None, uses default ALLOWED_EXTENSIONS.
        
        Raises:
            BadRequestException: If validation fails.
        """
        # 1. Check extension
        filename = file.filename or ""
        ext = os.path.splitext(filename)[1].lower()
        
        allowed = allowed_extensions or cls.ALLOWED_EXTENSIONS
        if ext not in allowed:
            raise BadRequestException(
                f"File type '{ext}' is not allowed. Allowed types: {', '.join(sorted(allowed))}"
            )

        # 2. Check size (Approximate checks before reading whole content if possible, 
        # but for precise check we rely on content reading in save_file or caller)
        # Here we just validate what we can. Content-Length header is not always reliable.
        # So specific size check is better done during read.
        
        # However, for this implementation, we will check size after reading content 
        # in save_file to be safe and accurate, or allow caller to handle it.
        # But we can check Content-Length header if present as a fast-fail.
        if file.size and file.size > max_size_mb * 1024 * 1024:
             raise BadRequestException(f"File size exceeds {max_size_mb}MB limit")

    @classmethod
    async def save_file(
        cls, 
        file: UploadFile, 
        directory: str = "uploads",
        max_size_mb: int = 5
    ) -> tuple[str, str, int, str]:
        """
        Save uploaded file to disk.
        
        Args:
            file: The uploaded file.
            directory: Subdirectory within storage/ (default: 'uploads').
            max_size_mb: Maximum size in MB.
            
        Returns:
            tuple: (file_path, filename, file_size, content_type)
        """
        # Validate extensions first
        cls.validate_file(file, max_size_mb=max_size_mb)
        
        # Prepare directory
        base_dir = os.path.join("storage", directory)
        os.makedirs(base_dir, exist_ok=True)
        
        # Generate unique filename
        filename = file.filename or "unknown_file"
        file_ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(base_dir, unique_filename)
        
        # Read content
        content = await file.read()
        file_size = len(content)
        
        # Validate size accurately
        if file_size > max_size_mb * 1024 * 1024:
            raise BadRequestException(f"File size exceeds {max_size_mb}MB limit")
        
        # Write to disk
        # Since we already have content in memory, standard write is fine.
        with open(file_path, "wb") as f:
            f.write(content)
            
        return file_path, filename, file_size, file.content_type or "application/octet-stream"

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Delete a file from disk.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            bool: True if deleted, False if file didn't exist.
        """
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
