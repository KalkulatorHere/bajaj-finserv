# Tesseract Installation Required

The solution now uses **Tesseract OCR** instead of PaddleOCR for better Windows compatibility.

## Install Tesseract

### Windows
Download and install Tesseract from:
https://github.com/UB-Mannheim/tesseract/wiki

Or use chocolatey:
```bash
choco install tesseract
```

After installation, tesseract should be in your PATH. If not, update `ocr_engine.py` with the path:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Quick Test
```bash
tesseract --version
```

## Alternative: Use PaddleOCR Docker Image

If you prefer PaddleOCR, you can use Docker:
```bash
docker pull paddlepaddle/paddle:latest-gpu-cuda11.2-cudnn8
```

## Current Status

- ✓ FastAPI endpoint implemented
- ✓ OCR engine (Tesseract)
- ✓ Extraction logic (row clustering, field detection)
- ✓ Deduplication
- ⚠ Tesseract binary needs to be installed for testing
