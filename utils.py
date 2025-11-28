"""Utility functions for bill extraction."""
import re
import os
import tempfile
import requests
from urllib.parse import urlparse
from typing import Optional


def download_file(url: str) -> str:
    """Download file from URL to temp location."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    # Determine file extension from URL or Content-Type
    parsed = urlparse(url)
    ext = os.path.splitext(parsed.path)[1]
    if not ext:
        content_type = response.headers.get('Content-Type', '')
        if 'pdf' in content_type:
            ext = '.pdf'
        elif 'image' in content_type:
            ext = '.png'
        else:
            ext = '.pdf'  # default
    
    # Create temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    temp_file.write(response.content)
    temp_file.close()
    
    return temp_file.name


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_number(text: str) -> Optional[float]:
    """Extract number from text string."""
    # Remove common currency symbols and commas
    text = text.replace('₹', '').replace('Rs', '').replace(',', '').strip()
    
    # Try to find a number
    match = re.search(r'(\d+(?:\.\d{1,2})?)', text)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def is_likely_amount(text: str) -> bool:
    """Check if text looks like a monetary amount."""
    # Check if it's a number with up to 2 decimal places
    pattern = r'^\s*₹?\s*\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?\s*$'
    return bool(re.match(pattern, text.replace(' ', '')))


def clean_item_name(text: str) -> str:
    """Clean item name text."""
    # Remove leading/trailing whitespace
    text = text.strip()
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text
