#!/usr/bin/env python3
"""Quick test of the Image Renamer tool."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from image_renamer.analyzer import GeminiCliAnalyzer
from image_renamer.renamer import SeoFilenameGenerator

def test_tool():
    """Test the complete image renaming pipeline."""
    print("\n" + "="*60)
    print("  IMAGE RENAMER - GEMINI CLI 3.0-FLASH TEST")
    print("="*60 + "\n")
    
    # Initialize
    print("[1] Initializing Gemini CLI analyzer...")
    analyzer = GeminiCliAnalyzer()
    print("    OK - Analyzer ready\n")
    
    # Analyze image
    image_path = Path(__file__).parent.parent / "Analyze_Images" / "callum-hill-oamw52SCGi0-unsplash.jpg"
    print(f"[2] Analyzing image: {image_path.name}")
    keywords = analyzer.analyze_image(str(image_path))
    
    if not keywords:
        print("    FAILED - No keywords extracted")
        return False
    
    print(f"    OK - Extracted {len(keywords)} keywords:")
    print(f"       {', '.join(keywords)}\n")
    
    # Generate filename
    print("[3] Generating SEO filename...")
    generator = SeoFilenameGenerator()
    new_filename = generator.generate_filename(keywords, '.jpg')
    
    print(f"    Old: {image_path.name}")
    print(f"    New: {new_filename}")
    print(f"    Length: {len(new_filename)} characters\n")
    
    print("="*60)
    print("  SUCCESS - TOOL IS WORKING!")
    print("="*60 + "\n")
    
    print("To rename the image, run:")
    print("  python run.py Analyze_Images/ --rename\n")
    
    return True

if __name__ == '__main__':
    success = test_tool()
    sys.exit(0 if success else 1)
