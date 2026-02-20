"""
SEO-optimized filename generator from image keywords.
"""

import re
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class SeoFilenameGenerator:
    """Generates SEO-optimized filenames from image keywords."""
    
    MAX_LENGTH = 60  # Maximum filename length (including extension)
    MIN_KEYWORDS = 2  # Minimum keywords needed for renaming
    
    def generate_filename(
        self,
        keywords: List[str],
        original_extension: str,
        directory: Optional[Path] = None
    ) -> str:
        """
        Generate an SEO-optimized filename from keywords.
        
        Args:
            keywords: List of descriptive keywords
            original_extension: Original file extension (with dot, e.g., '.jpg')
            directory: Directory to check for filename collisions (optional)
            
        Returns:
            New SEO-optimized filename with original extension
        """
        if not keywords or len(keywords) < self.MIN_KEYWORDS:
            logger.warning(f"Insufficient keywords for filename generation: {keywords}")
            return self._generate_fallback_filename(original_extension)
        
        # Select best keywords (typically first 4-6)
        selected_keywords = keywords[:6]
        
        # Create base filename
        base_filename = '-'.join(selected_keywords)
        
        # Sanitize: remove special characters, keep only alphanumeric and hyphens
        base_filename = self._sanitize_filename(base_filename)
        
        # Enforce length limit
        max_base_length = self.MAX_LENGTH - len(original_extension)
        if len(base_filename) > max_base_length:
            base_filename = base_filename[:max_base_length].rstrip('-')
        
        # Construct full filename
        filename = f"{base_filename}{original_extension}"
        
        # Check for collisions if directory provided
        if directory:
            filename = self._handle_collision(filename, directory)
        
        logger.debug(f"Generated filename: {filename} (from keywords: {selected_keywords})")
        return filename
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename by removing/replacing invalid characters.
        
        Args:
            filename: Raw filename to clean
            
        Returns:
            Sanitized filename (lowercase, alphanumeric and hyphens only)
        """
        # Convert to lowercase
        filename = filename.lower()
        
        # Replace spaces and underscores with hyphens
        filename = re.sub(r'[\s_]+', '-', filename)
        
        # Remove invalid characters, keep only alphanumeric and hyphens
        filename = re.sub(r'[^a-z0-9\-]', '', filename)
        
        # Clean up multiple consecutive hyphens
        filename = re.sub(r'-+', '-', filename)
        
        # Remove leading/trailing hyphens
        filename = filename.strip('-')
        
        return filename
    
    def _handle_collision(self, filename: str, directory: Path) -> str:
        """
        Handle filename collisions by appending number if needed.
        
        Args:
            filename: Proposed filename
            directory: Directory to check for existing files
            
        Returns:
            Unique filename (with -N suffix if collision detected)
        """
        filepath = directory / filename
        
        if not filepath.exists():
            return filename
        
        # Collision detected - append number
        name_parts = filename.rsplit('.', 1)
        base = name_parts[0]
        ext = f".{name_parts[1]}" if len(name_parts) > 1 else ""
        
        counter = 2
        while (directory / f"{base}-{counter}{ext}").exists():
            counter += 1
        
        new_filename = f"{base}-{counter}{ext}"
        logger.debug(f"Filename collision: {filename} -> {new_filename}")
        
        return new_filename
    
    def _generate_fallback_filename(self, extension: str) -> str:
        """
        Generate a fallback filename when keyword analysis fails.
        
        Args:
            extension: File extension (with dot)
            
        Returns:
            Descriptive fallback filename
        """
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"image-{timestamp}{extension}"
