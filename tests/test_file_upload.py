import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from fastapi import UploadFile
from app.utils.file_upload import FileUploadService
from app.core.exceptions import BadRequestException

@pytest.mark.asyncio
class TestFileUploadService:

    async def test_validate_file_extension_success(self):
        # Arrange
        file = MagicMock(spec=UploadFile)
        file.filename = "test.jpg"
        file.size = 100
        
        # Act & Assert
        # Should not raise exception
        FileUploadService.validate_file(file)

    async def test_validate_file_extension_failure(self):
        # Arrange
        file = MagicMock(spec=UploadFile)
        file.filename = "test.exe"
        file.size = 100
        
        # Act & Assert
        with pytest.raises(BadRequestException) as exc:
            FileUploadService.validate_file(file)
        assert "File type '.exe' is not allowed" in str(exc.value)

    async def test_validate_custom_allowed_extensions(self):
        # Arrange
        file = MagicMock(spec=UploadFile)
        file.filename = "test.jpg"
        file.size = 100
        allowed = {".png"}
        
        # Act & Assert
        with pytest.raises(BadRequestException):
            FileUploadService.validate_file(file, allowed_extensions=allowed)

    async def test_save_file_success(self):
        # Arrange
        content = b"fake content"
        file = MagicMock(spec=UploadFile)
        file.filename = "test.txt"
        file.size = len(content)
        file.content_type = "text/plain"
        file.read = AsyncMock(return_value=content)
        
        # Act
        file_path, file_name, file_size, file_type = await FileUploadService.save_file(
            file, directory="test_uploads", max_size_mb=1
        )
        
        # Assert
        assert os.path.exists(file_path)
        assert file_name == "test.txt"
        assert file_size == len(content)
        assert file_type == "text/plain"
        
        # Cleanup
        os.remove(file_path)
        os.rmdir(os.path.dirname(file_path))

    async def test_save_file_size_exceeded(self):
        # Arrange
        # 2MB content
        content = b"x" * (2 * 1024 * 1024)
        file = MagicMock(spec=UploadFile)
        file.filename = "large.txt"
        file.size = len(content)
        file.read = AsyncMock(return_value=content)
        
        # Act & Assert
        with pytest.raises(BadRequestException) as exc:
            await FileUploadService.save_file(file, max_size_mb=1)
        assert "File size exceeds 1MB limit" in str(exc.value)

    def test_delete_file(self):
        # Arrange
        path = "test_delete.txt"
        with open(path, "w") as f:
            f.write("test")
            
        # Act
        result = FileUploadService.delete_file(path)
        
        # Assert
        assert result is True
        assert not os.path.exists(path)

    def test_delete_file_not_exist(self):
        # Act
        result = FileUploadService.delete_file("non_existent.txt")
        
        # Assert
        assert result is False
