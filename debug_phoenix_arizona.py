#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.advanced_classifier import AdvancedJobClassifier
import re

def debug_phoenix_arizona():
    """Debug why Phoenix, Arizona pattern isn't working"""
    
    classifier = AdvancedJobClassifier(use_ai=False)
    text = "25 HVAC Technician jobs available in Phoenix, Arizona on job site"
    
    print("🔍 DEBUGGING PHOENIX, ARIZONA EXTRACTION")
    print("=" * 60)
    print(f"Input: {text}")
    print()
    
    # Test the patterns manually
    patterns = [
        r'jobs?\s+(?:available\s+)?in\s+([A-Za-z\s]{2,30}),\s*([A-Za-z\s]{2,20})',  # Pattern 1
        r'^\d+\s+[A-Za-z\s,]+?,\s*([A-Za-z\s]{2,30}),\s*([A-Za-z\s]{2,20})',    # Pattern 2
        r'\b([A-Za-z\s]{2,30}),\s*([A-Za-z\s]{2,20})\b'                          # Pattern 3
    ]
    
    for i, pattern in enumerate(patterns, 1):
        print(f"Pattern {i}: {pattern}")
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            for match in matches:
                city, state = match
                print(f"  Found: city='{city}', state='{state}'")
                print(f"  State valid: {classifier._is_valid_state(state)}")
                print(f"  State normalized: {classifier._normalize_state(state)}")
        else:
            print("  No matches")
        print()
    
    # Test the actual methods
    print("🧪 ACTUAL METHOD RESULTS:")
    city = classifier.extract_city(text)
    state = classifier.extract_state(text)
    print(f"City: '{city}'")
    print(f"State: '{state}'")
    
    # Check if "Arizona on job site" is causing issues
    print(f"\n🔍 CHECKING 'ARIZONA ON JOB SITE':")
    test_state = "Arizona on job site"
    print(f"'{test_state}' is valid state: {classifier._is_valid_state(test_state)}")
    print(f"'Arizona' is valid state: {classifier._is_valid_state('Arizona')}")

if __name__ == "__main__":
    debug_phoenix_arizona()