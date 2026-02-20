"""
Main CLI interface for Image Renamer tool.
Uses Gemini CLI with 3.0-Flash model.
"""

import sys
import logging
from pathlib import Path
from typing import List, Optional

from image_renamer.analyzer import GeminiCliAnalyzer
from image_renamer.renamer import SeoFilenameGenerator
from image_renamer import utils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class ImageRenamerCLI:
    """Command-line interface for batch image renaming with Gemini CLI 3.0-Flash."""
    
    def __init__(self):
        """Initialize CLI with Gemini CLI analyzer."""
        try:
            self.analyzer = GeminiCliAnalyzer()
        except RuntimeError as e:
            logger.error(str(e))
            logger.info("\n📋 To authenticate Gemini CLI, run: gemini")
            logger.info("   Then follow the browser login with your Google account.")
            sys.exit(1)
        
        self.generator = SeoFilenameGenerator()
    
    def run(self, input_path: str, dry_run: bool = True) -> None:
        """
        Run the image renaming process.
        
        Args:
            input_path: Path to image file or directory
            dry_run: If True, show preview without renaming
        """
        # Discover images
        images = utils.discover_images(input_path)
        if not images:
            logger.error(f"No valid images found in: {input_path}")
            return
        
        logger.info(f"\nProcessing {len(images)} image(s)...")
        
        # Analyze and prepare renames
        rename_plan: List[tuple] = []  # (old_path, new_filename, keywords)
        
        for idx, image_path in enumerate(images, 1):
            logger.info(f"[{idx}/{len(images)}] Analyzing: {image_path.name}")
            
            # Validate image
            if not utils.validate_image(image_path):
                logger.warning(f"  Skipping invalid image")
                continue
            
            # Analyze image
            keywords = self.analyzer.analyze_image(str(image_path))
            if not keywords:
                logger.warning(f"  No keywords extracted - skipping")
                continue
            
            # Generate new filename
            new_filename = self.generator.generate_filename(
                keywords,
                image_path.suffix,
                image_path.parent
            )
            
            rename_plan.append((image_path, new_filename, keywords))
        
        # Display preview
        self._show_preview(rename_plan)
        
        # Ask for confirmation if not dry-run
        if not dry_run and rename_plan:
            if not self._confirm_rename(len(rename_plan)):
                logger.info("Rename cancelled by user")
                return
            
            # Execute renames
            self._execute_renames(rename_plan)
    
    def _show_preview(self, rename_plan: List[tuple]) -> None:
        """
        Display preview of proposed renames.
        
        Args:
            rename_plan: List of (old_path, new_filename, keywords) tuples
        """
        if not rename_plan:
            logger.info("\nNo images to rename")
            return
        
        logger.info(f"\n╔════════════════════════════════════════════════════════╗")
        logger.info(f"║         Preview: {len(rename_plan)} image(s) to rename         ║")
        logger.info(f"╚════════════════════════════════════════════════════════╝\n")
        
        for old_path, new_filename, keywords in rename_plan:
            logger.info(f"  {old_path.name}")
            logger.info(f"    ↓ {new_filename}")
            logger.info(f"    Keywords: {', '.join(keywords[:5])}")
            if len(keywords) > 5:
                logger.info(f"              {', '.join(keywords[5:])}")
            logger.info("")
    
    def _confirm_rename(self, count: int) -> bool:
        """
        Ask user for confirmation before renaming.
        
        Args:
            count: Number of files to rename
            
        Returns:
            True if user confirms, False otherwise
        """
        while True:
            response = input(
                f"\nProceed with renaming {count} file(s)? (yes/no): "
            ).strip().lower()
            
            if response in ('yes', 'y'):
                return True
            elif response in ('no', 'n'):
                return False
            else:
                logger.info("Please enter 'yes' or 'no'")
    
    def _execute_renames(self, rename_plan: List[tuple]) -> None:
        """
        Execute the rename operations.
        
        Args:
            rename_plan: List of (old_path, new_filename, keywords) tuples
        """
        renamed_count = 0
        error_count = 0
        
        logger.info("\n✓ Renaming files...")
        
        for old_path, new_filename, keywords in rename_plan:
            success, message = utils.rename_file(old_path, new_filename)
            
            if success:
                renamed_count += 1
            else:
                error_count += 1
                logger.error(f"  Failed to rename {old_path.name}: {message}")
        
        # Show summary
        total = len(rename_plan)
        skipped = 0
        summary = utils.format_summary(total, renamed_count, skipped, error_count)
        logger.info(summary)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m image_renamer.main <image_path_or_directory> [--rename]")
        print("\nOptions:")
        print("  <path>      Path to image file or directory containing images")
        print("  --rename    Actually rename files (default: preview only)")
        sys.exit(1)
    
    input_path = sys.argv[1]
    rename_mode = '--rename' in sys.argv
    
    cli = ImageRenamerCLI()
    cli.run(input_path, dry_run=not rename_mode)


if __name__ == '__main__':
    main()
