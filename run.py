#!/usr/bin/env python3
"""
Entry point for Image Renamer CLI.

Usage:
    python run.py <image_path_or_directory>              # Preview mode
    python run.py <image_path_or_directory> --rename     # Actually rename files
"""

import sys
from image_renamer.main import main

if __name__ == '__main__':
    main()
