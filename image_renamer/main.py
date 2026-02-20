"""
Main CLI interface for Image Renamer tool.
Uses Gemini CLI with 3.0-Flash model.
Supports parallel image analysis with up to 5 concurrent agents.
"""

import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from image_renamer.analyzer import GeminiCliAnalyzer
from image_renamer.renamer import SeoFilenameGenerator
from image_renamer import utils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Thread lock for thread-safe logging
log_lock = Lock()


class ImageRenamerCLI:
    """Command-line interface for batch image renaming with Gemini CLI 3.0-Flash.
    
    Supports parallel image analysis with configurable number of concurrent agents (1-5).
    """
    
    MAX_WORKERS = 5  # Maximum concurrent image analysis agents
    
    def __init__(self, timeout_secs: Optional[int] = None, workers: int = 1):
        """Initialize CLI with Gemini CLI analyzer.
        
        Args:
            timeout_secs: Timeout in seconds for Gemini CLI calls (default: 30s).
            workers: Number of concurrent analysis agents (default: 1, max: 5).
        """
        # Validate and clamp workers
        self.workers = min(max(workers, 1), self.MAX_WORKERS)
        if workers != self.workers:
            logger.warning(f"Workers clamped to {self.workers} (valid range: 1-{self.MAX_WORKERS})")
        
        try:
            self.analyzer = GeminiCliAnalyzer(timeout_secs=timeout_secs)
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
        
        logger.info(f"\nProcessing {len(images)} image(s) with {self.workers} agent(s)...")
        
        # Analyze images (sequential or parallel)
        if self.workers == 1:
            keyword_map = self._process_images_sequential(images)
        else:
            keyword_map = self._process_images_parallel(images)
        
        # Prepare rename plan from analysis results
        rename_plan: List[tuple] = []  # (old_path, new_filename, keywords)
        
        for image_path in images:
            if image_path not in keyword_map:
                continue
            
            keywords = keyword_map[image_path]
            if not keywords:
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
    
    def _process_images_sequential(self, images: List[Path]) -> Dict[Path, Optional[List[str]]]:
        """
        Process images sequentially (1 agent).
        
        Args:
            images: List of image paths to process
            
        Returns:
            Dictionary mapping image paths to keywords (or None if failed)
        """
        keyword_map = {}
        
        for idx, image_path in enumerate(images, 1):
            logger.info(f"[{idx}/{len(images)}] Analyzing: {image_path.name}")
            
            # Validate image
            if not utils.validate_image(image_path):
                logger.warning(f"  Skipping invalid image")
                keyword_map[image_path] = None
                continue
            
            # Analyze image
            keywords = self.analyzer.analyze_image(str(image_path))
            if not keywords:
                logger.warning(f"  No keywords extracted - skipping")
            
            keyword_map[image_path] = keywords
        
        return keyword_map
    
    def _process_images_parallel(self, images: List[Path]) -> Dict[Path, Optional[List[str]]]:
        """
        Process images in parallel (up to 5 concurrent agents).
        
        Args:
            images: List of image paths to process
            
        Returns:
            Dictionary mapping image paths to keywords (or None if failed)
        """
        keyword_map = {}
        completed = 0
        total = len(images)
        
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            # Submit all image analysis tasks
            futures = {
                executor.submit(self._analyze_image_task, image_path): image_path
                for image_path in images
            }
            
            # Process results as they complete
            for future in as_completed(futures):
                completed += 1
                image_path = futures[future]
                
                try:
                    keywords = future.result(timeout=300)  # 5-minute timeout per task
                    keyword_map[image_path] = keywords
                    
                    with log_lock:
                        status = "✓" if keywords else "⊘"
                        count = len(keywords) if keywords else 0
                        logger.info(f"[{completed}/{total}] {status} {image_path.name} ({count} keywords)")
                
                except Exception as e:
                    keyword_map[image_path] = None
                    with log_lock:
                        logger.error(f"[{completed}/{total}] ✗ {image_path.name}: {str(e)}")
        
        return keyword_map
    
    def _analyze_image_task(self, image_path: Path) -> Optional[List[str]]:
        """
        Task function for parallel image analysis.
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of keywords or None if analysis fails
        """
        # Validate image
        if not utils.validate_image(image_path):
            return None
        
        # Analyze image
        keywords = self.analyzer.analyze_image(str(image_path))
        return keywords
    
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
        print("Usage: python -m image_renamer.main <image_path_or_directory> [--rename] [--timeout SECONDS] [--workers N]")
        print("\nOptions:")
        print("  <path>            Path to image file or directory containing images")
        print("  --rename          Actually rename files (default: preview only)")
        print("  --timeout SECONDS Timeout for Gemini CLI calls in seconds (default: 30)")
        print("  --workers N       Number of concurrent analysis agents (default: 1, max: 5)")
        print("\nExamples:")
        print("  python -m image_renamer.main Analyze_Images/")
        print("  python -m image_renamer.main Analyze_Images/ --rename")
        print("  python -m image_renamer.main Analyze_Images/ --workers 5")
        print("  python -m image_renamer.main Analyze_Images/ --rename --workers 5 --timeout 60")
        sys.exit(1)
    
    input_path = sys.argv[1]
    rename_mode = '--rename' in sys.argv
    
    # Parse timeout argument
    timeout_secs = None
    if '--timeout' in sys.argv:
        try:
            timeout_idx = sys.argv.index('--timeout')
            timeout_secs = int(sys.argv[timeout_idx + 1])
            logger.info(f"Using custom timeout: {timeout_secs}s")
        except (ValueError, IndexError):
            logger.error("Invalid --timeout value. Must be an integer.")
            sys.exit(1)
    
    # Parse workers argument
    workers = 1
    if '--workers' in sys.argv:
        try:
            workers_idx = sys.argv.index('--workers')
            workers = int(sys.argv[workers_idx + 1])
        except (ValueError, IndexError):
            logger.error("Invalid --workers value. Must be an integer between 1 and 5.")
            sys.exit(1)
    
    cli = ImageRenamerCLI(timeout_secs=timeout_secs, workers=workers)
    cli.run(input_path, dry_run=not rename_mode)


if __name__ == '__main__':
    main()
