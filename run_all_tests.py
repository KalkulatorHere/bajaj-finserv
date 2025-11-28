"""Run tests on all training samples."""
from pathlib import Path
import subprocess
import json
import sys
import codecs

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def run_all_tests():
    """Test extraction on all training samples."""
    samples_dir = Path("TRAINING_SAMPLES/TRAINING_SAMPLES")
    
    if not samples_dir.exists():
        print(f"Error: Training samples directory not found: {samples_dir}")
        return
    
    pdf_files = sorted(samples_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in training samples directory")
        return
    
    print(f"Found {len(pdf_files)} training samples")
    print("=" * 80)
    
    results = []
    successful = 0
    failed = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Testing: {pdf_file.name}")
        print("-" * 80)
        
        try:
            result = subprocess.run(
                ["python", "test_extraction.py", str(pdf_file)],
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                print("[SUCCESS]")
                successful += 1
                
                # Try to read output file
                output_file = pdf_file.parent.parent / f"{pdf_file.stem}_output.json"
                if output_file.exists():
                    with open(output_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'data' in data:
                            total_items = data['data'].get('total_item_count', 0)
                            reconciled_amount = data['data'].get('reconciled_amount', 0)
                            print(f"  Items: {total_items}, Amount: Rs.{reconciled_amount:.2f}")
                
                results.append({
                    'file': pdf_file.name,
                    'status': 'success',
                    'output': result.stdout
                })
            else:
                print(f"[FAILED] (exit code: {result.returncode})")
                print(f"  Error: {result.stderr[:200] if result.stderr else 'No error output'}")
                failed += 1
                results.append({
                    'file': pdf_file.name,
                    'status': 'failed',
                    'error': result.stderr
                })
                
        except subprocess.TimeoutExpired:
            print("[TIMEOUT] (>60s)")
            failed += 1
            results.append({
                'file': pdf_file.name,
                'status': 'timeout'
            })
        except Exception as e:
            print(f"[EXCEPTION] {e}")
            failed += 1
            results.append({
                'file': pdf_file.name,
                'status': 'exception',
                'error': str(e)
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total: {len(pdf_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {successful/len(pdf_files)*100:.1f}%")
    
    # Save results
    results_file = Path("test_results_all.json")
    with open(results_file, 'w') as f:
        json.dump({
            'total': len(pdf_files),
            'successful': successful,
            'failed': failed,
            'results': results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return successful == len(pdf_files)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
