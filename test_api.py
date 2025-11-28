"""Test the bill extraction API with training samples."""
import os
import json
import requests
from pathlib import Path


def test_local_api():
    """Test the local API with training samples."""
    api_url = "http://localhost:8000/extract-bill-data"
    
    # Get training samples directory
    base_dir = Path(__file__).parent
    samples_dir = base_dir / "TRAINING_SAMPLES"
    
    if not samples_dir.exists():
        print(f"Training samples directory not found: {samples_dir}")
        return
    
    # Get all PDF files
    pdf_files = sorted(samples_dir.glob("*.pdf"))
    
    print(f"Found {len(pdf_files)} training samples")
    print("=" * 80)
    
    results = []
    
    for pdf_file in pdf_files[:3]:  # Test first 3 files
        print(f"\nTesting: {pdf_file.name}")
        print("-" * 80)
        
        try:
            # Send request
            response = requests.post(
                api_url,
                json={"document": str(pdf_file)},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✓ Success!")
                
                # Display summary
                if data.get('is_success') and 'data' in data:
                    extracted_data = data['data']
                    print(f"  Total items: {extracted_data.get('total_item_count', 0)}")
                    print(f"  Reconciled amount: ₹{extracted_data.get('reconciled_amount', 0):.2f}")
                    print(f"  Pages: {len(extracted_data.get('pagewise_line_items', []))}")
                    
                    # Show first few items
                    for page_data in extracted_data.get('pagewise_line_items', [])[:1]:
                        print(f"\n  Page {page_data.get('page_no')} ({page_data.get('page_type', 'Unknown')}):")
                        for item in page_data.get('bill_items', [])[:5]:
                            print(f"    - {item.get('item_name')[:50]}: ₹{item.get('item_amount'):.2f}")
                        if len(page_data.get('bill_items', [])) > 5:
                            print(f"    ... and {len(page_data.get('bill_items', [])) - 5} more items")
                
                results.append({
                    'file': pdf_file.name,
                    'success': True,
                    'data': data
                })
            else:
                print(f"✗ Failed with status {response.status_code}")
                print(f"  Error: {response.text}")
                results.append({
                    'file': pdf_file.name,
                    'success': False,
                    'error': response.text
                })
        
        except Exception as e:
            print(f"✗ Exception: {e}")
            results.append({
                'file': pdf_file.name,
                'success': False,
                'error': str(e)
            })
    
    # Save results
    output_file = base_dir / "test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 80)
    print(f"Results saved to: {output_file}")
    
    # Summary
    success_count = sum(1 for r in results if r['success'])
    print(f"\nSummary: {success_count}/{len(results)} successful")


if __name__ == "__main__":
    print("Bill Extraction API Test")
    print("Make sure the API is running: uvicorn app:app --reload")
    print()
    
    test_local_api()
