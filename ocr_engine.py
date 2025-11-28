"""OCR Engine using Tesseract (Pytesseract) - Windows compatible alternative."""
import os
from typing import List, Dict, Tuple
import cv2
import numpy as np
try:
    import pytesseract
    from pytesseract import Output
except ImportError:
    print("Warning: pytesseract not installed. Run: pip install pytesseract")
    pytesseract = None
from pdf2image import convert_from_path
from PIL import Image


class OCREngine:
    """Wrapper around Tesseract OCR for document processing."""
    
    def __init__(self):
        """Initialize Tesseract OCR."""
        # If tesseract is not in PATH, you may need to set it manually:
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def pdf_to_images(self, pdf_path: str, dpi: int = 300) -> List[np.ndarray]:
        """Convert PDF to list of images."""
        try:
            images = convert_from_path(pdf_path, dpi=dpi)
            # Convert PIL images to numpy arrays
            return [np.array(img) for img in images]
        except Exception as e:
            print(f"Error converting PDF: {e}")
            return []
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results."""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        return denoised
    
    def extract_tokens(self, image: np.ndarray) -> List[Dict]:
        """Extract OCR tokens with bounding boxes from image."""
        if pytesseract is None:
            raise ImportError("pytesseract is not installed")
        
        # Preprocess
        processed = self.preprocess_image(image)
        
        # Run OCR with bounding boxes
        data = pytesseract.image_to_data(processed, output_type=Output.DICT)
        
        tokens = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            text = data['text'][i].strip()
            if not text:  # Skip empty text
                continue
            
            conf = float(data['conf'][i])
            if conf < 0:  # Skip low confidence
                continue
            
            x = data['left'][i]
            y = data['top'][i]
            w = data['width'][i]
            h = data['height'][i]
            
            tokens.append({
                'x1': x,
                'x2': x + w,
                'y1': y,
                'y2': y + h,
                'text': text,
                'conf': conf / 100.0,  # Normalize to 0-1
                'box': [[x, y], [x+w, y], [x+w, y+h], [x, y+h]]
            })
        
        return tokens
    
    def process_document(self, file_path: str) -> List[Tuple[int, List[Dict]]]:
        """
        Process a document (PDF or image) and return OCR tokens for each page.
        
        Returns:
            List of (page_number, tokens) tuples
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            images = self.pdf_to_images(file_path)
        else:
            # Single image
            img = cv2.imread(file_path)
            if img is None:
                # Try with PIL
                pil_img = Image.open(file_path)
                img = np.array(pil_img)
            images = [img]
        
        results = []
        for page_num, image in enumerate(images, start=1):
            tokens = self.extract_tokens(image)
            results.append((page_num, tokens))
        
        return results
