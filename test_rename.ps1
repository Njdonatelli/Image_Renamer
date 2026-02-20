#!/usr/bin/env powershell
# Test and rename script for Image Renamer

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  IMAGE RENAMER - TEST & RENAME" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Show current state
Write-Host "[1] Current files in Sample_Images/`n"
Get-ChildItem Sample_Images -File | ForEach-Object { Write-Host "    $($_.Name)" }

Write-Host "`n[2] Running rename analysis...`n"

# Run the Python analysis
& .\.venv\Scripts\python.exe -c @"
import sys
from pathlib import Path

sys.path.insert(0, '.')

from image_renamer.analyzer import GeminiCliAnalyzer
from image_renamer.renamer import SeoFilenameGenerator
from image_renamer import utils

sample_dir = Path('Sample_Images')
images = utils.discover_images(str(sample_dir))

analyzer = GeminiCliAnalyzer()
generator = SeoFilenameGenerator()

rename_count = 0

for image_path in images:
    if not utils.validate_image(image_path):
        continue
    
    keywords = analyzer.analyze_image(str(image_path))
    if not keywords:
        continue
    
    new_filename = generator.generate_filename(keywords, image_path.suffix, image_path.parent)
    
    print(f"Renaming: {image_path.name}")
    print(f"      -> {new_filename}")
    print(f"   Keywords: {', '.join(keywords[:4])}\n")
    
    success, msg = utils.rename_file(image_path, new_filename)
    if success:
        rename_count += 1
        print(f"   SUCCESS\n")
    else:
        print(f"   FAILED: {msg}\n")

print(f"Renamed {rename_count} file(s)")
"@

Write-Host "[3] Result - Files in Sample_Images/`n"
Get-ChildItem Sample_Images -File | ForEach-Object { Write-Host "    $($_.Name)" }

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  TEST COMPLETE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green
