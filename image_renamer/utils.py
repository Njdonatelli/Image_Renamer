"""
Utility functions for file operations and image handling.
"""

import logging
from pathlib import Path
from typing import List, Tuple
from PIL import Image

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}


def discover_images(path: str) -> List[Path]:
    """
    Discover all supported image files in a path.
    
    Args:
        path: File path or directory path
        
    Returns:
        List of Path objects for valid image files
    """
    input_path = Path(path)
    
    # Single file
    if input_path.is_file():
        if input_path.suffix.lower() in SUPPORTED_FORMATS:
            return [input_path]
        else:
            logger.warning(f"File is not a supported image format: {path}")
            return []
    
    # Directory
    if input_path.is_dir():
        images = []
        for ext in SUPPORTED_FORMATS:
            images.extend(input_path.glob(f'*{ext}'))
            images.extend(input_path.glob(f'*{ext.upper()}'))
        # Remove duplicates
        images = list(set(images))
        logger.info(f"Found {len(images)} image(s) in {path}")
        return sorted(images)
    
    logger.error(f"Path not found: {path}")
    return []


def validate_image(image_path: Path) -> bool:
    """
    Validate that file is a readable image.
    
    Args:
        image_path: Path to image file
        
    Returns:
        True if valid image, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception as e:
        logger.warning(f"Invalid image file {image_path.name}: {str(e)}")
        return False


def rename_file(old_path: Path, new_filename: str) -> Tuple[bool, str]:
    """
    Safely rename a file with error handling.
    
    Args:
        old_path: Current file path
        new_filename: New filename (without directory)
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        new_path = old_path.parent / new_filename
        
        # Verify new filename doesn't already exist
        if new_path.exists() and new_path != old_path:
            return False, f"File already exists: {new_filename}"
        
        old_path.rename(new_path)
        logger.info(f"Renamed: {old_path.name} -> {new_filename}")
        return True, new_filename
        
    except Exception as e:
        logger.error(f"Error renaming {old_path.name}: {str(e)}")
        return False, str(e)


def format_summary(
    total: int,
    renamed: int,
    skipped: int,
    errors: int
) -> str:
    """
    Format a summary report of renaming results.
    
    Args:
        total: Total images processed
        renamed: Successfully renamed
        skipped: Skipped (no keywords)
        errors: Failed to rename
        
    Returns:
        Formatted summary string
    """
    summary = f"""
╔════════════════════════════════════════╗
║     Image Renaming Summary Report      ║
╚════════════════════════════════════════╝

  Total images processed:  {total}
  ✓ Successfully renamed:  {renamed}
  ⊘ Skipped (no data):     {skipped}
  ✗ Errors:                {errors}
"""
    return summary
