#!/usr/bin/env python3
"""Non-interactive test of the rename functionality."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from image_renamer.analyzer import GeminiCliAnalyzer
from image_renamer.renamer import SeoFilenameGenerator
from image_renamer import utils

def test_rename():
    """Test the complete rename workflow."""
    print("\n" + "="*60)
    print("  TESTING IMAGE RENAME")
    print("="*60 + "\n")
    
    # Discover images
    sample_dir = Path(__file__).parent.parent / "Analyze_Images"
    images = utils.discover_images(str(sample_dir))
    
    if not images:
        print("ERROR: No images found in Analyze_Images/")
        return False
    
    print(f"[1] Found {len(images)} image(s)\n")
    
    # Initialize tools
    analyzer = GeminiCliAnalyzer()
    generator = SeoFilenameGenerator()
    
    rename_plan = []
    
    # Process each image
    for idx, image_path in enumerate(images, 1):
        print(f"[{idx}] Analyzing: {image_path.name}")
        
        # Validate
        if not utils.validate_image(image_path):
            print("    -> Invalid image, skipping")
            continue
        
        # Analyze
        keywords = analyzer.analyze_image(str(image_path))
        if not keywords:
            print("    -> No keywords extracted, skipping")
            continue
        
        # Generate new filename
        new_filename = generator.generate_filename(
            keywords,
            image_path.suffix,
            image_path.parent
        )
        
        rename_plan.append((image_path, new_filename, keywords))
        print(f"    -> New name: {new_filename}")
        print(f"    -> Keywords: {', '.join(keywords[:4])}")
    
    print(f"\n[2] Preview: {len(rename_plan)} file(s) to rename\n")
    
    if not rename_plan:
        print("No files to rename")
        return False
    
    # Show preview
    for old_path, new_filename, keywords in rename_plan:
        print(f"    {old_path.name}")
        print(f"    -> {new_filename}")
    
    # Execute renames
    print(f"\n[3] Executing {len(rename_plan)} rename(s)...\n")
    
    renamed_count = 0
    for old_path, new_filename, keywords in rename_plan:
        success, message = utils.rename_file(old_path, new_filename)
        if success:
            print(f"    OK: {old_path.name} -> {new_filename}")
            renamed_count += 1
        else:
            print(f"    FAILED: {old_path.name} ({message})")
    
    # Report
    print("\n" + "="*60)
    print(f"  RENAME COMPLETE: {renamed_count}/{len(rename_plan)} successful")
    print("="*60 + "\n")
    
    # Verify
    print("[4] Verifying renamed files...\n")
    current_files = list(Path(sample_dir).glob('*'))
    for f in current_files:
        if f.is_file():
            print(f"    {f.name}")
    
    return renamed_count == len(rename_plan)

if __name__ == '__main__':
    success = test_rename()
    sys.exit(0 if success else 1)
