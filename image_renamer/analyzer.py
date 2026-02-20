"""
Image analyzer using Gemini CLI to extract descriptive keywords from images.
Uses Gemini 3.0-Flash model (available via authenticated Gemini CLI).
"""

import subprocess
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class GeminiCliAnalyzer:
    """Analyzes images using Gemini CLI with 3.0-Flash model via @file syntax."""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}
    MODEL = "gemini-3.0-flash"  # Explicitly use 3.0-Flash
    
    def __init__(self):
        """Initialize analyzer and verify Gemini CLI availability."""
        self.gemini_available = self._check_gemini_cli()
        if not self.gemini_available:
            logger.error("❌ Gemini CLI not found. Cannot proceed without Gemini CLI authentication.")
            raise RuntimeError("Gemini CLI is required. Please authenticate with: gemini")
    
    def _check_gemini_cli(self) -> bool:
        """Check if Gemini CLI is installed and accessible."""
        try:
            # Use shell=True on Windows to properly inherit PATH environment
            result = subprocess.run(
                'gemini --version',
                capture_output=True,
                text=True,
                timeout=5,
                stdin=subprocess.DEVNULL,
                shell=True
            )
            is_available = result.returncode == 0
            if is_available:
                version = result.stdout.strip()
                logger.info(f"✓ Gemini CLI available: {version}")
            return is_available
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def analyze_image(self, image_path: str) -> Optional[List[str]]:
        """
        Analyze an image using Gemini CLI 3.0-Flash and extract descriptive keywords.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of extracted keywords, or None if analysis fails
        """
        path = Path(image_path)
        
        # Validate file exists and is supported format
        if not path.exists():
            logger.error(f"Image file not found: {image_path}")
            return None
        
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            logger.error(f"Unsupported image format: {path.suffix}")
            return None
        
        # Optimized prompt for SEO filename generation
        prompt = (
            "Analyze this image and identify the most important visual elements. "
            "Provide 5-8 key descriptive words separated by commas that best describe "
            "the image content. Focus on: main objects, setting/location, colors, mood, "
            "and actions. Respond with ONLY the comma-separated keywords, no explanation."
        )
        
        try:
            # Build command - Gemini CLI uses 3.0-Flash/Pro by default for authenticated users
            # No need to specify model explicitly, CLI handles it
            cmd = f'gemini "@{path}" "{prompt}"'
            logger.debug(f"Running: gemini @{path.name} [prompt]")
            
            # Use shell=True to properly inherit PATH environment on Windows
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                stdin=subprocess.DEVNULL,
                shell=True
            )
            
            if result.returncode != 0:
                logger.error(f"Gemini CLI error (exit code {result.returncode})")
                if result.stderr:
                    logger.debug(f"Stderr: {result.stderr}")
                return None
            
            response_text = result.stdout.strip()
            if not response_text and result.stderr:
                response_text = result.stderr.strip()
            
            keywords = self._extract_keywords(response_text)
            
            if not keywords:
                logger.warning(f"No keywords extracted from image: {path.name}")
                return None
            
            logger.info(f"✓ Extracted {len(keywords)} keywords from {path.name}")
            return keywords
            
        except subprocess.TimeoutExpired:
            logger.error(f"Gemini CLI timeout (30s)")
            return None
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return None
    
    def _extract_keywords(self, response_text: str) -> List[str]:
        """
        Extract keywords from Gemini's response.
        
        Handles JSON responses, comma-separated, and newline-separated keyword lists.
        
        Args:
            response_text: Raw response from Gemini CLI
            
        Returns:
            List of cleaned keyword strings
        """
        if not response_text.strip():
            return []
        
        # Try to parse JSON response first
        try:
            import json
            data = json.loads(response_text)
            # If response has a 'response' field, use that
            if isinstance(data, dict) and 'response' in data:
                response_text = data['response']
            elif isinstance(data, dict) and 'keywords' in data:
                response_text = data['keywords']
            else:
                # If it's a string value in JSON, use it
                response_text = str(list(data.values())[0]) if data else ""
        except (json.JSONDecodeError, ValueError, KeyError):
            # Not JSON, continue with text parsing
            pass
        
        # Try comma-separated first
        if ',' in response_text:
            keywords = [kw.strip().lower() for kw in response_text.split(',')]
        else:
            # Try newline-separated
            keywords = [kw.strip().lower() for kw in response_text.split('\n')]
        
        # Clean up: remove empty strings, filter out common articles
        keywords = [
            kw for kw in keywords 
            if kw and len(kw) > 1 and kw not in {'a', 'an', 'the', 'and', 'or', 'but'}
        ]
        
        return keywords[:8]  # Limit to 8 keywords for filename generation


