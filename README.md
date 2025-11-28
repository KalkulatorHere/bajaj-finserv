# Bill Extraction API

A FastAPI-based service for extracting line items and totals from bill/invoice documents using OCR.

## 🚀 Quick Start

**See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed setup instructions.**

### Docker Deployment (Recommended)
```bash
docker build -t bill-extraction .
docker run -p 8000:8000 bill-extraction
```

### Local Development
1. Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Install Python dependencies: `pip install -r requirements_docker.txt`
3. Run: `uvicorn app:app --reload`

## Features


- **PDF and Image Support**: Processes both PDF documents and image files
- **OCR-based Extraction**: Uses PaddleOCR for text recognition
- **Heuristic Parsing**: Row clustering and field extraction using position-based heuristics
- **Deduplication**: Removes duplicate entries using fuzzy matching
- **REST API**: FastAPI endpoint for easy integration

## Architecture

The solution uses a **no-training** approach suitable for quick deployment:

1. **OCR Engine** (`ocr_engine.py`): PaddleOCR wrapper for text extraction
2. **Extractor** (`extractor.py`): Row clustering, field identification, and deduplication
3. **API** (`app.py`): FastAPI endpoint serving the extraction pipeline

## Installation

```bash
pip install -r requirements.txt
```

**Note**: On Windows, you may need to install poppler for PDF support:
- Download from: https://github.com/oschwartz10612/poppler-windows/releases
- Add `bin/` folder to PATH

## Usage

### Start the API Server

```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoint

**POST** `/extract-bill-data`

**Request:**
```json
{
  "document": "https://example.com/invoice.pdf"
}
```

**Response:**
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

### Testing

Run the test script against training samples:

```bash
python test_api.py
```

## Design Decisions

### Why OCR + Heuristics?

- **No Training Required**: Can be deployed immediately without model training
- **Fast Inference**: OCR + regex is much faster than LLM-based approaches
- **Deterministic**: Predictable behavior for debugging
- **Good Baseline**: Achieves reasonable accuracy on structured bills

### Limitations

- Assumes tabular layout with consistent column ordering
- May struggle with:
  - Highly unstructured documents
  - Handwritten text
  - Complex multi-column layouts
  - Poor quality scans

### Future Improvements

If more accuracy is needed:
1. Fine-tune Donut model on annotated samples
2. Add layout detection (layoutparser/YOLO)
3. Implement table structure recognition
4. Add validation rules based on domain knowledge

## File Structure

```
.
├── app.py              # FastAPI application
├── ocr_engine.py       # PaddleOCR wrapper
├── extractor.py        # Data extraction logic
├── utils.py            # Helper functions
├── test_api.py         # Test script
├── requirements.txt    # Dependencies
└── TRAINING_SAMPLES/   # Training data
```

## Evaluation Criteria

The solution is evaluated on:
1. **Accuracy**: Line item extraction and total reconciliation
2. **Completeness**: No missing items, no double-counting
3. **Format Compliance**: Output matches required schema

## Author

Created for Bajaj Finserv Datathon
