"""Extract structured data from OCR tokens."""
import re
from typing import List, Dict, Optional, Tuple
from rapidfuzz import fuzz
from utils import normalize_text, extract_number, clean_item_name


class BillExtractor:
    """Extract bill items and totals from OCR tokens."""
    
    def __init__(self, y_tolerance: float = 12):
        """
        Initialize extractor.
        
        Args:
            y_tolerance: Vertical tolerance for row clustering (pixels)
        """
        self.y_tolerance = y_tolerance
    
    def cluster_rows(self, tokens: List[Dict]) -> List[List[Dict]]:
        """Cluster tokens into rows based on Y-coordinate."""
        if not tokens:
            return []
        
        # Sort by Y coordinate
        sorted_tokens = sorted(tokens, key=lambda t: t['y1'])
        
        rows = []
        current_row = []
        current_y = None
        
        for token in sorted_tokens:
            cy = (token['y1'] + token['y2']) / 2
            
            if current_y is None or abs(cy - current_y) <= self.y_tolerance:
                current_row.append(token)
                current_y = cy if current_y is None else (current_y + cy) / 2
            else:
                if current_row:
                    rows.append(current_row)
                current_row = [token]
                current_y = cy
        
        if current_row:
            rows.append(current_row)
        
        return rows
    
    def classify_page_type(self, tokens: List[Dict]) -> str:
        """Classify page type based on content."""
        text = ' '.join([t['text'].lower() for t in tokens])
        
        if any(keyword in text for keyword in ['pharmacy', 'medicine', 'tablet', 'capsule']):
            return 'Pharmacy'
        elif any(keyword in text for keyword in ['total', 'net amt', 'net amount', 'grand total']):
            return 'Final Bill'
        else:
            return 'Bill Detail'
    
    def extract_row_data(self, row: List[Dict]) -> Optional[Dict]:
        """Extract item data from a row of tokens."""
        if not row:
            return None
        
        # Sort tokens by X coordinate
        sorted_row = sorted(row, key=lambda t: t['x1'])
        
        # Extract text
        row_text = ' '.join([t['text'] for t in sorted_row])
        
        # Skip header rows and total rows
        lower_text = row_text.lower()
        skip_keywords = [
            'item', 'description', 'particular', 'qty', 'quantity', 'rate', 'amount',
            'total', 'subtotal', 'sub-total', 'net amount', 'grand total',
            'page', 'sl no', 's.no', 'sr no', 'date', 'bill no', 'invoice'
        ]
        
        if any(keyword in lower_text for keyword in skip_keywords):
            # Check if it's actually a data row with numbers
            if not re.search(r'\d{2,}', row_text):
                return None
        
        # Try to identify columns
        # Typical pattern: Item Name | Qty | Rate | Amount
        # Amount is usually the rightmost number
        # Rate is usually second from right
        # Qty is usually third from right or a small number
        
        numbers = []
        item_name_tokens = []
        
        for i, token in enumerate(sorted_row):
            text = token['text']
            # Try to extract number
            num = extract_number(text)
            if num is not None:
                numbers.append({
                    'value': num,
                    'position': i,
                    'x': token['x1'],
                    'text': text
                })
            else:
                # Likely part of item name
                item_name_tokens.append(text)
        
        # Need at least amount
        if not numbers:
            return None
        
        # Sort numbers by X position (right to left)
        numbers_sorted = sorted(numbers, key=lambda n: n['x'], reverse=True)
        
        # Extract amount (rightmost number)
        amount = numbers_sorted[0]['value']
        
        # Extract rate and quantity
        rate = None
        quantity = None
        
        if len(numbers_sorted) >= 2:
            rate = numbers_sorted[1]['value']
        
        if len(numbers_sorted) >= 3:
            quantity = numbers_sorted[2]['value']
        elif len(numbers_sorted) == 2:
            # Try to determine if second number is rate or quantity
            # Quantity is usually smaller and often an integer
            second_num = numbers_sorted[1]['value']
            if second_num <= 100 and second_num == int(second_num):
                quantity = second_num
                rate = amount / quantity if quantity > 0 else amount
            else:
                rate = second_num
                quantity = amount / rate if rate > 0 else 1.0
        else:
            # Only amount available
            rate = amount
            quantity = 1.0
        
        # Build item name from remaining tokens
        item_name = ' '.join(item_name_tokens).strip()
        if not item_name:
            # Try to get from left side of row
            left_tokens = [t['text'] for t in sorted_row[:max(1, len(sorted_row) - len(numbers))]]
            item_name = ' '.join(left_tokens).strip()
        
        item_name = clean_item_name(item_name)
        
        # Skip if item name is too short or empty
        if len(item_name) < 2:
            return None
        
        return {
            'item_name': item_name,
            'item_amount': round(amount, 2),
            'item_rate': round(rate, 2) if rate else round(amount, 2),
            'item_quantity': round(quantity, 2) if quantity else 1.0
        }
    
    def deduplicate_items(self, items: List[Dict]) -> List[Dict]:
        """Remove duplicate items based on fuzzy matching."""
        if not items:
            return []
        
        unique_items = []
        seen_signatures = []
        
        for item in items:
            # Create signature
            name_norm = normalize_text(item['item_name'])
            amount = item['item_amount']
            
            # Check against existing items
            is_duplicate = False
            for i, sig in enumerate(seen_signatures):
                sig_name, sig_amount = sig
                # Fuzzy match on name
                name_similarity = fuzz.token_set_ratio(name_norm, sig_name)
                amount_diff = abs(amount - sig_amount)
                
                if name_similarity >= 90 and amount_diff <= max(1.0, 0.01 * amount):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_items.append(item)
                seen_signatures.append((name_norm, amount))
        
        return unique_items
    
    def extract_totals(self, tokens: List[Dict]) -> Dict[str, Optional[float]]:
        """Extract total amounts from tokens."""
        rows = self.cluster_rows(tokens)
        
        totals = {
            'sub_total': None,
            'net_amount': None,
            'grand_total': None
        }
        
        for row in rows:
            sorted_row = sorted(row, key=lambda t: t['x1'])
            row_text = ' '.join([t['text'] for t in sorted_row]).lower()
            
            # Look for total keywords
            if any(kw in row_text for kw in ['net amount', 'net amt', 'total amount']):
                # Extract rightmost number
                numbers = [extract_number(t['text']) for t in sorted_row]
                numbers = [n for n in numbers if n is not None]
                if numbers:
                    totals['net_amount'] = numbers[-1]
            
            elif any(kw in row_text for kw in ['subtotal', 'sub total', 'sub-total']):
                numbers = [extract_number(t['text']) for t in sorted_row]
                numbers = [n for n in numbers if n is not None]
                if numbers:
                    totals['sub_total'] = numbers[-1]
            
            elif 'grand total' in row_text:
                numbers = [extract_number(t['text']) for t in sorted_row]
                numbers = [n for n in numbers if n is not None]
                if numbers:
                    totals['grand_total'] = numbers[-1]
        
        return totals
    
    def extract_page_items(self, page_num: int, tokens: List[Dict]) -> Dict:
        """Extract all items from a single page."""
        # Cluster tokens into rows
        rows = self.cluster_rows(tokens)
        
        # Classify page type
        page_type = self.classify_page_type(tokens)
        
        # Extract items from each row
        items = []
        for row in rows:
            item = self.extract_row_data(row)
            if item:
                items.append(item)
        
        # Deduplicate items
        items = self.deduplicate_items(items)
        
        return {
            'page_no': str(page_num),
            'page_type': page_type,
            'bill_items': items
        }
    
    def extract_from_document(self, page_tokens: List[Tuple[int, List[Dict]]]) -> Dict:
        """
        Extract structured data from entire document.
        
        Args:
            page_tokens: List of (page_num, tokens) tuples
            
        Returns:
            Structured data matching required format
        """
        pagewise_line_items = []
        all_items = []
        
        for page_num, tokens in page_tokens:
            page_data = self.extract_page_items(page_num, tokens)
            pagewise_line_items.append(page_data)
            all_items.extend(page_data['bill_items'])
        
        # Deduplicate across all pages
        all_items = self.deduplicate_items(all_items)
        
        # Calculate reconciled amount
        reconciled_amount = sum(item['item_amount'] for item in all_items)
        
        return {
            'pagewise_line_items': pagewise_line_items,
            'total_item_count': len(all_items),
            'reconciled_amount': round(reconciled_amount, 2)
        }
