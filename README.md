# Image Renamer - SEO-Optimized Image Filename Generator

An AI-powered image analyzer that uses Google Gemini to extract descriptive keywords from images and automatically rename them with SEO-optimized filenames.

## Features

- **AI-Powered Image Analysis**: Uses Gemini CLI (3.0-Flash/Pro) to analyze image content and extract key descriptors
- **SEO-Optimized Naming**: Generates keyword-rich, hyphen-separated filenames optimized for search visibility
- **Batch Processing**: Process single images or entire directories at once
- **Parallel Processing**: Analyze up to 5 images concurrently for faster batch processing
- **Intelligent Retry Logic**: Automatic retries with exponential backoff for transient failures
- **Configurable Timeouts**: Adjust API call timeout to match your network conditions
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

### Preview Mode (Default - Sequential Processing)
Shows proposed renames without modifying files:

```bash
# Single image
python run.py path/to/image.jpg

# Directory (all images) - processes 1 image at a time
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

### Parallel Processing (up to 5 concurrent agents)
Process multiple images simultaneously for faster batch analysis:

```bash
# Preview with 5 concurrent agents (5x faster)
python run.py path/to/images/ --workers 5

# Rename with 5 concurrent agents
python run.py path/to/images/ --rename --workers 5

# With custom timeout and 3 agents
python run.py path/to/images/ --rename --workers 3 --timeout 45
```

### Command-Line Options

- `--rename` - Actually rename files (default: preview only)
- `--workers N` - Number of concurrent analysis agents (1-5, default: 1)
- `--timeout SECONDS` - API timeout per image in seconds (default: 30)

### Performance Guidelines

| Workers | Processing Time | Use Case |
|---------|-----------------|----------|
| 1 | ~1.5s per image | Single images, slow networks |
| 2-3 | ~0.5-0.75s per image | Small batches (< 50 images) |
| 5 | ~0.3s per image | Large batches (> 50 images) |

**Example**: 386 images at 5 workers ≈ 2-3 minutes with retries

## Workflow

1. **Discovery**: Tool finds all supported images in the specified path
2. **Validation**: Each image is verified as a valid image file
3. **Analysis** (with robustness features):
   - Gemini CLI analyzes each image and extracts 5-8 descriptive keywords
   - **Automatic Retries**: On timeout, automatically retries up to 2 additional times with exponential backoff (2s, 4s delays)
   - **Configurable Timeout**: Adjust per-image timeout with `--timeout` flag for slow networks
   - **Parallel Processing**: Analyze 1-5 images concurrently based on `--workers` setting
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
- Maximum 5 concurrent workers to respect Gemini API rate limits

## Troubleshooting

**"Gemini CLI is not available" error**:
- Ensure `gemini` command is installed and in your system PATH
- Run `gemini --version` to verify installation
- Restart terminal/IDE after installing Gemini CLI

**Frequent API timeouts**:
- Increase timeout with `--timeout 60` or higher (default: 30s)
- Enable retries (automatic) - the tool retries up to 3 times before skipping
- Use 1-2 workers instead of 5 to reduce API load: `--workers 1 --timeout 45`
- Check your internet connection quality and latency to Gemini API servers

**No keywords extracted**:
- Image may be corrupted or unreadable - check file integrity
- Try simplifying the image (clear focus, good lighting)
- Gemini API might be rate-limited - the tool waits and retries automatically
- If persistent, check API quota: `gemini --version`

**Filename collision detected**:
- Tool automatically appends `-2`, `-3`, etc. to duplicate filenames
- This is normal behavior in directories with many similar images

**Performance issues on large batches**:
- Start with `--workers 1` to ensure stability
- Increase to `--workers 3` or `--workers 5` once verified
- Monitor system resources (CPU, memory, network)

## Project Structure

```
Image_Renamer/
├── image_renamer/
│   ├── __init__.py           # Package initialization
│   ├── analyzer.py           # Gemini CLI image analysis with retry logic
│   ├── renamer.py            # SEO filename generation
│   ├── utils.py              # File operations utilities
│   └── main.py               # CLI interface with parallel processing
├── tests/
│   ├── __init__.py           # Test package
│   ├── README.md             # Test documentation
│   ├── test_retry_logic.py   # Retry configuration tests
│   ├── test_parallel_processing.py  # Parallel worker tests
│   ├── test_tool.py          # Integration test (single image)
│   ├── test_rename.py        # Batch rename workflow test
│   └── test_rename.ps1       # PowerShell integration test
├── .gemini/
│   ├── agents/
│   │   └── image-analyzer.md # Subagent for robust image analysis
│   └── settings.json         # Gemini CLI configuration
├── run.py                    # Entry point script
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── Analyze_Images/           # Images directory for batch processing (gitignored)
```

## Testing

The `tests/` directory contains comprehensive tests for all features:

- **test_retry_logic.py** - Validates timeout and retry configuration
- **test_parallel_processing.py** - Tests worker pool management (1-5 agents)
- **test_tool.py** - Integration test with single image analysis
- **test_rename.py** - Full batch rename workflow
- **test_rename.ps1** - PowerShell integration test

See [tests/README.md](tests/README.md) for detailed test documentation and how to run them.

Quick test example:
```bash
python tests/test_retry_logic.py        # No API required
python tests/test_parallel_processing.py # No API required
```

## License

This project is provided as-is for personal use.
