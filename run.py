#!/usr/bin/env python3
"""
Entry point for Image Renamer CLI.

Usage:
    python run.py <image_path_or_directory>                      # Preview mode (1 agent)
    python run.py <image_path_or_directory> --rename             # Actually rename files
    python run.py <image_path_or_directory> --workers 5          # Preview with 5 parallel agents
    python run.py <image_path_or_directory> --rename --workers 5 --timeout 60
"""

import sys
from image_renamer.main import main

if __name__ == '__main__':
    main()
