"""FastAPI application for bill extraction."""
import os
import tempfile
from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ocr_engine import OCREngine
from extractor import BillExtractor
from utils import download_file


app = FastAPI(title="Bill Extraction API")

# Initialize components
ocr_engine = OCREngine()
extractor = BillExtractor(y_tolerance=12)


class DocumentRequest(BaseModel):
    """Request model for document extraction."""
    document: str


class TokenUsage(BaseModel):
    """Token usage model (for LLM calls, 0 for OCR-only)."""
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0


class ExtractionResponse(BaseModel):
    """Response model for document extraction."""
    is_success: bool
    token_usage: TokenUsage
    data: Dict


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "running", "service": "Bill Extraction API"}


@app.post("/extract-bill-data")
def extract_bill_data(request: DocumentRequest) -> ExtractionResponse:
    """
    Extract line items and totals from bill document.
    
    Args:
        request: Contains document URL or path
        
    Returns:
        Structured bill data
    """
    temp_file = None
    try:
        # Download or get file
        document_url = request.document
        
        if document_url.startswith('http://') or document_url.startswith('https://'):
            # Download from URL
            temp_file = download_file(document_url)
            file_path = temp_file
        else:
            # Local file path
            file_path = document_url
            if not os.path.exists(file_path):
                raise HTTPException(status_code=400, detail=f"File not found: {file_path}")
        
        # Process document with OCR
        page_tokens = ocr_engine.process_document(file_path)
        
        if not page_tokens:
            raise HTTPException(status_code=500, detail="Failed to extract text from document")
        
        # Extract structured data
        extracted_data = extractor.extract_from_document(page_tokens)
        
        return ExtractionResponse(
            is_success=True,
            token_usage=TokenUsage(),  # No LLM tokens used
            data=extracted_data
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    
    finally:
        # Cleanup temp file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except:
                pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
