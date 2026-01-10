import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Tuple
from app.models.schemas import ImageType
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class FileStorageService:
    """Service for managing file storage by category."""
    
    def __init__(self, base_storage_path: str = None):
        """
        Initialize file storage service.
        
        Args:
            base_storage_path: Base directory for storage (default: ./storage)
        """
        self.base_path = Path(base_storage_path or settings.STORAGE_PATH)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create storage directories for all image categories."""
        for image_type in ImageType:
            category_path = self.base_path / image_type.value
            input_path = category_path / "input"
            output_path = category_path / "output"
            
            input_path.mkdir(parents=True, exist_ok=True)
            output_path.mkdir(parents=True, exist_ok=True)
            
        logger.info(f"Storage directories ensured at: {self.base_path}")
    
    def generate_filename(self, original_filename: str = None) -> str:
        """
        Generate unique filename with timestamp and UUID.
        
        Args:
            original_filename: Original filename (optional)
            
        Returns:
            Unique filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        if original_filename:
            # Get extension
            ext = Path(original_filename).suffix or ".png"
            base = Path(original_filename).stem[:20]  # Limit length
            return f"{timestamp}_{base}_{unique_id}{ext}"
        else:
            return f"{timestamp}_{unique_id}.png"
    
    def save_input(self, image_bytes: bytes, image_type: ImageType, original_filename: str = None) -> str:
        """
        Save input image to category-specific directory.
        
        Args:
            image_bytes: Image data
            image_type: Detected image category
            original_filename: Original filename (optional)
            
        Returns:
            Full path to saved file
        """
        filename = self.generate_filename(original_filename)
        file_path = self.base_path / image_type.value / "input" / filename
        
        with open(file_path, 'wb') as f:
            f.write(image_bytes)
        
        logger.info(f"Saved input: {file_path}")
        return str(file_path)
    
    def save_output(self, image_bytes: bytes, image_type: ImageType, input_filename: str) -> str:
        """
        Save output image to category-specific directory.
        Maintains filename relationship with input.
        
        Args:
            image_bytes: Processed image data
            image_type: Detected image category
            input_filename: Input filename to match
            
        Returns:
            Full path to saved file
        """
        # Use same filename as input
        filename = Path(input_filename).name
        file_path = self.base_path / image_type.value / "output" / filename
        
        with open(file_path, 'wb') as f:
            f.write(image_bytes)
        
        logger.info(f"Saved output: {file_path}")
        return str(file_path)
    
    def save_pair(self, input_bytes: bytes, output_bytes: bytes, image_type: ImageType, 
                  original_filename: str = None) -> Tuple[str, str]:
        """
        Save both input and output images with matching names.
        
        Args:
            input_bytes: Original image data
            output_bytes: Processed image data
            image_type: Detected image category
            original_filename: Original filename (optional)
            
        Returns:
            Tuple of (input_path, output_path)
        """
        filename = self.generate_filename(original_filename)
        
        input_path = self.base_path / image_type.value / "input" / filename
        output_path = self.base_path / image_type.value / "output" / filename
        
        with open(input_path, 'wb') as f:
            f.write(input_bytes)
        
        with open(output_path, 'wb') as f:
            f.write(output_bytes)
        
        logger.info(f"Saved pair - Input: {input_path}, Output: {output_path}")
        return str(input_path), str(output_path)
    
    def get_category_stats(self) -> dict:
        """
        Get statistics for each category.
        
        Returns:
            Dictionary with counts per category
        """
        stats = {}
        for image_type in ImageType:
            input_dir = self.base_path / image_type.value / "input"
            output_dir = self.base_path / image_type.value / "output"
            
            input_count = len(list(input_dir.glob("*"))) if input_dir.exists() else 0
            output_count = len(list(output_dir.glob("*"))) if output_dir.exists() else 0
            
            stats[image_type.value] = {
                "input": input_count,
                "output": output_count
            }
        
        return stats
    
    def cleanup_old_files(self, days: int = 7):
        """
        Clean up files older than specified days.
        
        Args:
            days: Number of days to keep files
        """
        import time
        cutoff_time = time.time() - (days * 86400)
        
        deleted_count = 0
        for image_type in ImageType:
            for subdir in ["input", "output"]:
                dir_path = self.base_path / image_type.value / subdir
                if dir_path.exists():
                    for file_path in dir_path.glob("*"):
                        if file_path.stat().st_mtime < cutoff_time:
                            file_path.unlink()
                            deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old files")
        return deleted_count
