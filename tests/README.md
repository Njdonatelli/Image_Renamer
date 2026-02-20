# Image Renamer Test Suite

This directory contains comprehensive tests for the Image Renamer tool, covering retry logic, timeout handling, parallel processing, and the complete rename workflow.

## Test Files

### `test_retry_logic.py`
Tests the retry logic and timeout configuration without requiring Gemini API calls.

**What it tests:**
- Default timeout (30s)
- Custom timeout configuration
- Retry parameters (MAX_RETRIES=2, RETRY_DELAY=2s)
- Exponential backoff strategy

**Run:**
```bash
python tests/test_retry_logic.py
```

**Expected output:**
- [+] All retry logic tests passed
- Displays retry strategy summary

---

### `test_parallel_processing.py`
Tests the parallel processing configuration and worker pool management.

**What it tests:**
- Default single worker (1 agent)
- Multiple worker configuration (up to 5)
- Worker clamping (validates 1-5 range)
- Processing methods existence
- MAX_WORKERS constant (5)

**Run:**
```bash
python tests/test_parallel_processing.py
```

**Expected output:**
- [+] All parallel processing tests passed
- Displays parallel processing capabilities summary

---

### `test_tool.py`
Quick integration test of the complete image renaming pipeline (requires Gemini CLI).

**What it tests:**
- Gemini CLI analyzer initialization
- Image analysis and keyword extraction
- SEO filename generation
- Complete pipeline workflow

**Run:**
```bash
python tests/test_tool.py
```

**Requires:**
- Gemini CLI authenticated
- `Analyze_Images/callum-hill-oamw52SCGi0-unsplash.jpg` present

**Expected output:**
- [+] Analyzer ready
- [+] Keywords extracted
- [+] Filename generated

---

### `test_rename.py`
Full workflow test for the rename functionality (requires Gemini CLI).

**What it tests:**
- Image discovery from `Analyze_Images/`
- Image validation
- Batch analysis with keyword extraction
- Filename generation for each image
- Rename execution

**Run:**
```bash
python tests/test_rename.py
```

**Requires:**
- Gemini CLI authenticated
- Images in `Analyze_Images/` directory

**Expected output:**
- List of discovered images
- Analysis results for each image
- Rename preview
- Success/failure counts

**Note:** This test actually renames files. Use with caution on production images.

---

### `test_rename.ps1`
PowerShell test script for the complete rename workflow.

**What it tests:**
- Image discovery and validation
- Batch analysis via Python
- Rename execution
- File verification before/after

**Run:**
```powershell
.\tests\test_rename.ps1
```

**Requires:**
- PowerShell 5.1+
- Gemini CLI authenticated
- Python venv activated or `.venv` accessible
- Images in `Analyze_Images/` directory

**Note:** This test actually renames files. Use with caution on production images.

---

## Running All Tests

```bash
# Run all quick tests (no API calls)
python tests/test_retry_logic.py
python tests/test_parallel_processing.py

# Run integration tests (requires Gemini CLI)
python tests/test_tool.py
python tests/test_rename.py

# Run PowerShell test
.\tests\test_rename.ps1
```

---

## Test Dependencies

- **Retry/Parallel tests:** No external dependencies
- **Tool/Rename tests:** Requires:
  - Gemini CLI installed and authenticated
  - Images in `Analyze_Images/` directory
  - Pillow library (PIL)

---

## Test Results Expectations

| Test | Requires API | File Modification | Time |
|------|-------------|-------------------|------|
| `test_retry_logic.py` | [NO] | [NO] | <1s |
| `test_parallel_processing.py` | [NO] | [NO] | <1s |
| `test_tool.py` | [API] | [NO] | ~30-60s |
| `test_rename.py` | [API] | [YES] | Minutes |
| `test_rename.ps1` | [API] | [YES] | Minutes |

---

## Troubleshooting Tests

**"Gemini CLI timeout" in test_tool.py or test_rename.py:**
- Network latency to Gemini API is high
- Increase timeout: `--timeout 60` in production
- This is expected behavior - retry logic handles it

**"No keywords extracted":**
- Image may be corrupted
- Gemini API rate-limited (wait and retry)
- API quota exceeded (check with `gemini --version`)

**"Analyzer failed to initialize":**
- Gemini CLI not installed: `gemini --version`
- Not authenticated: Run `gemini` and complete browser login
- PATH not updated after installation: Restart terminal

---

## Notes for Contributors

- Quick tests (retry/parallel) should run in <1 second each
- Integration tests should complete in <2 minutes for complete Analyze_Images (386 images)
- Tests use standard Python unittest patterns where applicable
- All test files are self-contained and can run independently
- Tests are organized by concern (retry, parallel, integration)
