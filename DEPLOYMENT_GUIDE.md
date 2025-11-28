# Deployment Guide - Bill Extraction API

## Quick Summary

The solution is **fully implemented** with a FastAPI endpoint for bill extraction. However, due to Windows-specific limitations with OCR libraries, you have **three deployment options**:

## Option 1: Install Tesseract Locally (Recommended for Local Testing)

### Steps:
1. **Download Tesseract Installer**
   - Visit: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest Windows installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)
   - Run installer and add to PATH

2. **Verify Installation**
   ```bash
   tesseract --version
   ```

3. **Update Code (if needed)**
   If tesseract is not in PATH, edit `ocr_engine.py` line 21:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

4. **Test**
   ```bash
   python test_extraction.py
   ```

5. **Run API**
   ```bash
   uvicorn app:app --reload
   ```

---

## Option 2: Deploy on Linux/Docker (Recommended for Production)

### Using Docker:

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

# Install Tesseract
RUN apt-get update && apt-get install -y tesseract-ocr poppler-utils

WORKDIR /app
COPY requirements_docker.txt .
RUN pip install -r requirements_docker.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `requirements_docker.txt`:
```
fastapi==0.104.1
uvicorn==0.24.0
pytesseract==0.3.10
pdf2image==1.16.3
opencv-python-headless==4.8.1.78
numpy==1.24.3
pandas==2.1.3
python-multipart==0.0.6
requests==2.31.0
Pillow==10.1.0
rapidfuzz==3.5.2
```

Build and run:
```bash
docker build -t bill-extraction .
docker run -p 8000:8000 bill-extraction
```

---

## Option 3: Use Cloud OCR API (Azure/Google Cloud Vision)

Replace `ocr_engine.py` to use cloud API instead of local OCR.

### Azure Computer Vision Example:
```python
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.ai.formrecognizer import DocumentAnalysisClient
```

### Google Cloud Vision Example:
```python
from google.cloud import vision
```

**Note**: Requires API keys and will incur costs per document.

---

## Current Project Status

### ✅ Completed
- FastAPI endpoint `/extract-bill-data`
- OCR engine (Tesseract-based)
- Row clustering algorithm
- Field extraction (item name, qty, rate, amount)
- Deduplication logic
- Total reconciliation
- Test scripts
- Full documentation

### ⚠ Manual Setup Required
- Install Tesseract binary (Option 1)
- OR Deploy to Linux/Docker (Option 2)
- OR Setup cloud OCR (Option 3)

---

## Testing Without Tesseract (Demo Mode)

If you want to test the API structure without OCR:

Create `ocr_engine_mock.py`:
```python
def process_document(file_path):
    # Return mock data for testing
    return [(1, [
        {'x1': 0, 'x2': 100, 'y1': 0, 'y2': 20, 'text': 'Consultation', 'conf': 0.9},
        {'x1': 200, 'x2': 250, 'y1': 0, 'y2': 20, 'text': '1000.00', 'conf': 0.9}
    ])]
```

Then update `app.py` import to use mock.

---

## Evaluation & Submission

1. **Deploy** using one of the above options
2. **Test** with all 15 training samples
3. **Verify** accuracy by comparing extracted totals with actual bill totals
4. **Document** approach in README.md
5. **Submit** GitHub repository link with deployment instructions

---

## Time Estimate

- **Option 1** (Local Tesseract): 10 minutes setup
- **Option 2** (Docker): 20 minutes setup
- **Option 3** (Cloud): 30 minutes setup + API key

The **12-hour deadline** is achievable with any of these options. I recommend **Option 2 (Docker)** for submission as it's portable and doesn't require local Tesseract installation on the evaluator's machine.

---

## Next Steps for You

1. Choose deployment option
2. Install dependencies
3. Run tests on training samples
4. Deploy and submit

All code is ready - just needs the OCR runtime environment!
