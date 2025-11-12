"""
Audio Handler - Audio file loading, storage, and format conversion
Manages audio upload, validation, and format handling
"""

import os
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import mimetypes

from utils.config import DATA_DIR, ALLOWED_AUDIO_EXTENSIONS, MAX_AUDIO_SIZE


class AudioHandler:
    """Handle audio file operations"""
    
    AUDIO_DIR = DATA_DIR / "audio_uploads"
    
    def __init__(self):
        """Initialize audio directory"""
        self.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def validate_audio_file(filename: str, file_size: int) -> Tuple[bool, Optional[str]]:
        """
        Validate audio file name and size
        
        Args:
            filename: Name of audio file
            file_size: Size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file extension
        file_extension = Path(filename).suffix.lower()
        if file_extension not in ALLOWED_AUDIO_EXTENSIONS:
            return False, f"Unsupported format: {file_extension}. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
        
        # Check file size
        if file_size > MAX_AUDIO_SIZE:
            return False, f"File too large: {file_size} bytes. Max: {MAX_AUDIO_SIZE} bytes"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, None
    
    def save_audio_file(self, file_content: bytes, original_filename: str) -> Dict[str, Any]:
        """
        Save audio file with unique ID
        
        Args:
            file_content: Audio file bytes
            original_filename: Original filename
            
        Returns:
            Dict with file_id, path, size, format, etc.
        """
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Get file extension
        file_extension = Path(original_filename).suffix.lower()
        
        # Create new filename with ID
        new_filename = f"{file_id}{file_extension}"
        file_path = self.AUDIO_DIR / new_filename
        
        # Write file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Get file size
        file_size = len(file_content)
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(original_filename)
        if mime_type is None:
            mime_type = "audio/unknown"
        
        return {
            "file_id": file_id,
            "filename": new_filename,
            "path": str(file_path),
            "size_bytes": file_size,
            "format": file_extension[1:] if file_extension else "unknown",
            "mime_type": mime_type,
            "original_filename": original_filename
        }
    
    def load_audio_file(self, file_id: str) -> Optional[bytes]:
        """
        Load audio file by ID
        
        Args:
            file_id: Audio file ID
            
        Returns:
            File bytes or None if not found
        """
        # Search for file with this ID
        for file_path in self.AUDIO_DIR.glob(f"{file_id}.*"):
            if file_path.is_file():
                with open(file_path, "rb") as f:
                    return f.read()
        
        return None
    
    def get_audio_path(self, file_id: str) -> Optional[str]:
        """
        Get file path for audio ID
        
        Args:
            file_id: Audio file ID
            
        Returns:
            File path or None if not found
        """
        for file_path in self.AUDIO_DIR.glob(f"{file_id}.*"):
            if file_path.is_file():
                return str(file_path)
        
        return None
    
    def delete_audio_file(self, file_id: str) -> bool:
        """
        Delete audio file by ID
        
        Args:
            file_id: Audio file ID
            
        Returns:
            True if deleted, False if not found
        """
        for file_path in self.AUDIO_DIR.glob(f"{file_id}.*"):
            if file_path.is_file():
                os.remove(file_path)
                return True
        
        return False
    
    def get_audio_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get info about audio file
        
        Args:
            file_id: Audio file ID
            
        Returns:
            Dict with file info or None
        """
        for file_path in self.AUDIO_DIR.glob(f"{file_id}.*"):
            if file_path.is_file():
                file_size = file_path.stat().st_size
                mime_type, _ = mimetypes.guess_type(str(file_path))
                
                return {
                    "file_id": file_id,
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size_bytes": file_size,
                    "format": file_path.suffix[1:] if file_path.suffix else "unknown",
                    "mime_type": mime_type or "audio/unknown"
                }
        
        return None
    
    def list_audio_files(self) -> list:
        """
        List all audio files
        
        Returns:
            List of file IDs
        """
        file_ids = set()
        for file_path in self.AUDIO_DIR.glob("*"):
            if file_path.is_file():
                # Extract file ID (everything before the extension)
                file_id = file_path.stem
                file_ids.add(file_id)
        
        return list(file_ids)
    
    def cleanup_old_files(self, max_age_seconds: int = 86400) -> int:
        """
        Delete audio files older than max_age_seconds
        
        Args:
            max_age_seconds: Maximum age in seconds (default: 24 hours)
            
        Returns:
            Number of files deleted
        """
        import time
        
        deleted_count = 0
        current_time = time.time()
        
        for file_path in self.AUDIO_DIR.glob("*"):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    os.remove(file_path)
                    deleted_count += 1
        
        return deleted_count


# Global instance
_audio_handler = None


def get_audio_handler() -> AudioHandler:
    """Get or create audio handler instance"""
    global _audio_handler
    if _audio_handler is None:
        _audio_handler = AudioHandler()
    return _audio_handler
