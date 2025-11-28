# Quick Tesseract Installation for Windows

## Issue
Tests are failing with:
```
TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```

## Solution

### Option 1: Download Installer (5 minutes)

1. **Download Tesseract**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download: `tesseract-ocr-w64-setup-5.3.3.20231005.exe` (or latest version)

2. **Install**
   - Run the installer
   - **IMPORTANT**: During installation, check "Add to PATH"
   - Or manually add `C:\Program Files\Tesseract-OCR` to your PATH

3. **Verify**
   ```powershell
   tesseract --version
   ```

4. **Run Tests**
   ```powershell
   python test_extraction.py "TRAINING_SAMPLES\TRAINING_SAMPLES\train_sample_1.pdf"
   ```

### Option 2: Use Chocolatey (2 minutes)

If you have Chocolatey installed:
```powershell
choco install tesseract -y
```

Then verify and test as above.

### Option 3: Manual Path Configuration

If Tesseract is installed but not in PATH:

1. Find tesseract.exe location (usually `C:\Program Files\Tesseract-OCR\tesseract.exe`)

2. Edit `ocr_engine.py` and add this line after the imports (around line 20):
   ```python
   # Set Tesseract path manually
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

3. Run tests

---

## Already Fixed

✅ Unicode encoding errors (Rs. symbols, checkmarks)  
✅ UTF-8 output support  
✅ Windows console compatibility  

## What's Next

Once Tesseract is installed, you can:

1. **Test single file**:
   ```powershell
   python test_extraction.py "TRAINING_SAMPLES\TRAINING_SAMPLES\train_sample_1.pdf"
   ```

2. **Test all 15 samples**:
   ```powershell
   python run_all_tests.py
   ```

3. **Start API server**:
   ```powershell
   uvicorn app:app --reload
   ```

---

## Alternative: Use Docker (No Tesseract Install Needed!)

If you have Docker:
```powershell
docker build -t bill-extraction .
docker run -p 8000:8000 bill-extraction
```

This includes Tesseract pre-installed!
