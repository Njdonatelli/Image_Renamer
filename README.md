# Image Renamer - SEO-Optimized Image Filename Generator

An AI-powered image analyzer that uses Google Gemini to extract descriptive keywords from images and automatically rename them with SEO-optimized filenames.

## Features

- **AI-Powered Image Analysis**: Uses Gemini CLI (3.0-Flash/Pro) to analyze image content and extract key descriptors
- **SEO-Optimized Naming**: Generates keyword-rich, hyphen-separated filenames optimized for search visibility
- **Batch Processing**: Process single images or entire directories at once
- **Preview Mode**: See proposed renames before actually modifying files
- **Collision Detection**: Automatically handles filename conflicts
- **Multiple Format Support**: Works with JPEG, PNG, WebP, GIF, and BMP images

## Requirements

- Python 3.12+
- Google Gemini CLI installed and authenticated
- Pillow (image validation library)

## Installation

1. **Clone or download this repository**:
   ```bash
   cd Image_Renamer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Gemini CLI is available**:
   ```bash
   gemini --version
   ```
   If not installed, follow Google's Gemini CLI installation guide.

## Usage

### Preview Mode (Default)
Shows proposed renames without modifying files:

```bash
# Single image
python run.py path/to/image.jpg

# Directory (all images)
python run.py path/to/images/
```

### Rename Mode
Actually rename the images:

```bash
# Single image
python run.py path/to/image.jpg --rename

# Directory (all images)
python run.py path/to/images/ --rename
```

## Workflow

1. **Discovery**: Tool finds all supported images in the specified path
2. **Validation**: Each image is verified as a valid image file
3. **Analysis**: Gemini CLI analyzes each image and extracts 5-8 descriptive keywords
4. **Generation**: SEO-optimized filename is created from the keywords:
   - Lowercase letters only
   - Hyphen-separated keywords
   - Under 60 characters total
   - Preserves original file extension
5. **Preview**: All proposed renames are displayed with extracted keywords
6. **Confirmation**: User confirms before any files are renamed
7. **Execution**: Files are renamed in-place in their original directory
8. **Report**: Summary showing success/error counts

## Example

**Input Image**: `DSC_12345.jpg` (landscape photo with mountains and sunset)

**Extracted Keywords**: mountain, sunset, scenic, landscape, clouds, valley, golden-hour

**Generated Filename**: `mountain-sunset-scenic-landscape-clouds-valley.jpg`

## Limitations

- Requires active internet connection for Gemini CLI API calls
- Image analysis quality depends on Gemini's vision model capabilities
- Filenames limited to 60 characters for SEO best practices
- Supports image formats: JPEG, PNG, WebP, GIF, BMP

## Troubleshooting

**"Gemini CLI is not available" error**:
- Ensure `gemini` command is installed and in your system PATH
- Run `gemini --version` to verify installation
- Restart terminal/IDE after installing Gemini CLI

**No keywords extracted**:
- Image may be corrupted or unreadable - check file integrity
- Try simplifying the image (clear focus, good lighting)
- Gemini API might be rate-limited - wait a moment and retry

**Filename collision detected**:
- Tool automatically appends `-2`, `-3`, etc. to duplicate filenames
- This is normal behavior in directories with many similar images

## Project Structure

```
Image_Renamer/
├── image_renamer/
│   ├── __init__.py           # Package initialization
│   ├── analyzer.py           # Gemini CLI image analysis
│   ├── renamer.py            # SEO filename generation
│   ├── utils.py              # File operations utilities
│   └── main.py               # CLI interface
├── run.py                     # Entry point script
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── Sample_Images/             # Test images directory
```

## License

This project is provided as-is for personal use.
