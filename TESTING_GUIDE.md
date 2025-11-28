# Testing Guide

## Overview
While Docker is not available on the current Windows system, here's how you can test the solution:

## Option 1: Test Locally with Tesseract

### 1. Install Tesseract
Download from: https://github.com/UB-Mannheim/tesseract/wiki

After installation, verify:
```bash
tesseract --version
```

### 2. Install Python Dependencies
```bash
pip install -r requirements_docker.txt
```

### 3. Run Standalone Test
```bash
python test_extraction.py TRAINING_SAMPLES/TRAINING_SAMPLES/train_sample_1.pdf
```

This will:
- Extract text using OCR
- Cluster rows and identify fields
- Output results to `train_sample_1_output.json`
- Display summary in console

### 4. Run All Training Samples
Create a batch test script `run_all_tests.py`:

```python
from pathlib import Path
import subprocess

samples_dir = Path("TRAINING_SAMPLES/TRAINING_SAMPLES")
for pdf in sorted(samples_dir.glob("*.pdf")):
    print(f"\n{'='*80}")
    print(f"Testing: {pdf.name}")
    print('='*80)
    subprocess.run(["python", "test_extraction.py", str(pdf)])
```

Run it:
```bash
python run_all_tests.py
```

### 5. Start API Server
```bash
uvicorn app:app --reload
```

Test with curl:
```bash
curl -X POST http://localhost:8000/extract-bill-data \
  -H "Content-Type: application/json" \
  -d "{\"document\": \"TRAINING_SAMPLES/TRAINING_SAMPLES/train_sample_1.pdf\"}"
```

---

## Option 2: Test with Docker (On Linux/Mac or WSL2)

### 1. Build Docker Image
```bash
docker build -t bill-extraction .
```

### 2. Run Container
```bash
docker run -p 8000:8000 bill-extraction
```

### 3. Test API
```bash
curl -X POST http://localhost:8000/extract-bill-data \
  -H "Content-Type: application/json" \
  -d "{\"document\": \"https://example.com/bill.pdf\"}"
```

---

## Expected Output Format

```json
{
  "is_success": true,
  "token_usage": {
    "total_tokens": 0,
    "input_tokens": 0,
    "output_tokens": 0
  },
  "data": {
    "pagewise_line_items": [
      {
        "page_no": "1",
        "page_type": "Bill Detail",
        "bill_items": [
          {
            "item_name": "Consultation",
            "item_amount": 4000.00,
            "item_rate": 1000.00,
            "item_quantity": 4.00
          }
        ]
      }
    ],
    "total_item_count": 12,
    "reconciled_amount": 16390.00
  }
}
```

---

## Evaluation Criteria

When testing, check:

1. **Completeness**: Are all line items extracted?
2. **Accuracy**: Do amounts match the bill totals?
3. **No Duplicates**: Same item shouldn't appear multiple times
4. **Format Compliance**: Output matches required schema

---

## Tuning Parameters

If extraction accuracy is low, adjust these in `extractor.py`:

### Y-Tolerance (Row Clustering)
```python
# Line 11 in extractor.py
extractor = BillExtractor(y_tolerance=12)  # Increase if rows split incorrectly
```

### Confidence Threshold
```python
# Line 74 in ocr_engine.py
if conf < 0:  # Change to if conf < 30 to filter low-confidence text
```

### Fuzzy Match Threshold
```python
# Line 149 in extractor.py
if name_similarity >= 90  # Lower to 80 for more aggressive deduplication
```

---

## Common Issues

### Issue 1: Missing Items
**Cause**: Y-tolerance too low, rows split incorrectly  
**Fix**: Increase `y_tolerance` to 15-20

### Issue 2: Duplicate Items
**Cause**: Fuzzy matching threshold too high  
**Fix**: Lower `name_similarity` threshold to 85

### Issue 3: Wrong Amounts
**Cause**: Column detection misidentified numbers  
**Fix**: Check if bill has unusual layout, may need manual column mapping

### Issue 4: Tesseract Not Found
**Cause**: Tesseract not in PATH  
**Fix**: Add this to `ocr_engine.py` line 21:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

---

## Next Steps

1. Install Tesseract locally
2. Run tests on all 15 samples
3. Calculate accuracy metrics
4. Tune parameters if needed
5. Document results in README
6. Deploy and submit!

---

## Deployment for Evaluation

For submission, evaluators can use:

### Docker (Recommended)
```bash
git clone https://github.com/KalkulatorHere/bajaj-finserv.git
cd bajaj-finserv
docker build -t bill-extraction .
docker run -p 8000:8000 bill-extraction
```

### Local
```bash
git clone https://github.com/KalkulatorHere/bajaj-finserv.git
cd bajaj-finserv
pip install -r requirements_docker.txt
# Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
uvicorn app:app --reload
```

API will be available at: `http://localhost:8000`
