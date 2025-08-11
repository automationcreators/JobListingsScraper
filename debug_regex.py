#!/usr/bin/env python3

import re

def test_regex_patterns():
    """Test different regex patterns for job title extraction"""
    
    test_sentences = [
        "Air Conditioning Technician & Apprentices",
        "Air Conditioning Technician & Apprentices.",
        "HVAC Installation Specialist & Maintenance Tech",
        "Aviation Safety Inspector",
        "Aircraft Interior Installer ABC Company"
    ]
    
    patterns = [
        r'^([A-Z][A-Za-z\s&]+?)(?:\s*$|\s*\.)',  # Simple: until end or period
        r'^([A-Z][A-Za-z\s&]+?(?:\s*&\s*[A-Za-z\s]+)?)(?:\s*$|\s*\.)',  # Include & phrases
        r'^([A-Z][A-Za-z\s&]+)',  # Everything starting with capital
        r'^(.+?)(?:\s*$|\s*\.)',  # Everything until end or period
        r'^([^\.]+)',  # Everything until period
    ]
    
    print("🔍 TESTING REGEX PATTERNS")
    print("=" * 70)
    
    for i, pattern in enumerate(patterns, 1):
        print(f"\nPattern {i}: {pattern}")
        print("-" * 50)
        
        for sentence in test_sentences:
            match = re.match(pattern, sentence)
            result = match.group(1).strip() if match else "No match"
            print(f"  '{sentence}' → '{result}'")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATION: Use pattern that captures complete job titles with &")

if __name__ == "__main__":
    test_regex_patterns()