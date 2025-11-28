"""Quick test of the extraction pipeline on a local file."""
import sys
import os
from pathlib import Path
from ocr_engine import OCREngine
from extractor import BillExtractor
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def test_single_file(file_path: str):
    """Test extraction on a single file."""
    print(f"Testing: {file_path}")
    print("=" * 80)
    
    # Initialize
    ocr_engine = OCREngine()
    extractor = BillExtractor(y_tolerance=12)
    
    try:
        # Process document
        print("Running OCR...")
        page_tokens = ocr_engine.process_document(file_path)
        
        print(f"Extracted {len(page_tokens)} pages")
        
        # Extract data
        print("Extracting structured data...")
        data = extractor.extract_from_document(page_tokens)
        
        # Display results
        print("\nResults:")
        print("-" * 80)
        print(f"Total items: {data['total_item_count']}")
        print(f"Reconciled amount: Rs.{data['reconciled_amount']:.2f}")
        print(f"Pages: {len(data['pagewise_line_items'])}")
        
        print("\nPage-wise breakdown:")
        for page_data in data['pagewise_line_items']:
            print(f"\n  Page {page_data['page_no']} ({page_data.get('page_type', 'Unknown')}):")
            print(f"  Items: {len(page_data['bill_items'])}")
            
            for i, item in enumerate(page_data['bill_items'][:10], 1):
                print(f"    {i}. {item['item_name'][:60]}")
                print(f"       Qty: {item['item_quantity']}, Rate: Rs.{item['item_rate']:.2f}, Amount: Rs.{item['item_amount']:.2f}")
            
            if len(page_data['bill_items']) > 10:
                print(f"    ... and {len(page_data['bill_items']) - 10} more items")
        
        # Save output
        output_file = Path(file_path).parent / f"{Path(file_path).stem}_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'is_success': True,
                'token_usage': {'total_tokens': 0, 'input_tokens': 0, 'output_tokens': 0},
                'data': data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n[SUCCESS] Output saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Use first training sample by default
        samples_dir = Path(__file__).parent / "TRAINING_SAMPLES"
        pdf_files = sorted(samples_dir.glob("*.pdf"))
        if pdf_files:
            file_path = str(pdf_files[0])
        else:
            print("No PDF files found in TRAINING_SAMPLES")
            sys.exit(1)
    
    success = test_single_file(file_path)
    sys.exit(0 if success else 1)
