#!/usr/bin/env python3

import re

def debug_address_pattern():
    text = "email: contact info:: 12345 ::"
    print(f"Testing text: '{text}'")
    
    patterns = [
        r'\bemail:\s*[A-Za-z\s]+::\b',  # Email pattern
        r'^\d{5}\s*::\b',  # ZIP code with ::
        r'\b\d{5}\s*::\b'   # ZIP code anywhere with ::
    ]
    
    for i, pattern in enumerate(patterns, 1):
        match = re.search(pattern, text, re.IGNORECASE)
        print(f"Pattern {i}: {pattern}")
        print(f"Match: {match.group(0) if match else 'None'}")
        print()

if __name__ == "__main__":
    debug_address_pattern()