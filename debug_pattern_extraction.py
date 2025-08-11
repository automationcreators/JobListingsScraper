#!/usr/bin/env python3

import re

def debug_pattern_extraction():
    test_cases = [
        "76 CHANDLER, AZ AIRCRAFT PARTS jobs from companies (hiring now) with openings",
        "345 Aircraft Detailing jobs available in Chandler, AZ on Indeed.com",
        "116 Aircraft jobs available in Decatur, AL on Indeed.com",
        "153 Airport jobs available in Buckeye, AZ on Indeed.com"
    ]
    
    patterns = [
        # Pattern 1: "76 CHANDLER, AZ AIRCRAFT PARTS jobs" -> "Aircraft Parts" - specific location pattern
        r'^\d+\s+[A-Z\s,]+?,\s*[A-Z]{2}\s+([A-Z][A-Za-z\s&]+?)\s+jobs?',
        
        # Pattern 2: "345 Aircraft Detailing jobs available" -> "Aircraft Detailing" 
        r'^\d+\s+([A-Z][A-Za-z\s&]+?)\s+jobs?\s+available',
        
        # Pattern 3: "116 Aircraft jobs available" -> "Aircraft" 
        r'^\d+\s+([A-Z][A-Za-z\s&]*?)\s+jobs?\s+available',
        
        # Pattern 4: "NUMBER JOB TITLE jobs" (simple case without location)
        r'^\d+\s+([A-Z][A-Za-z\s&]+?)\s+jobs?(?:\s+from|\s*$)',
    ]
    
    for sentence in test_cases:
        print(f"\nTesting: '{sentence}'")
        print("-" * 60)
        
        for i, pattern in enumerate(patterns, 1):
            print(f"Pattern {i}: {pattern}")
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                print(f"  ✅ Match: '{match.group(1)}'")
                break
            else:
                print(f"  ❌ No match")
        
        # Test a simpler approach for complex cases
        print("\nAlternative approach:")
        if "CHANDLER, AZ" in sentence:
            # For "76 CHANDLER, AZ AIRCRAFT PARTS jobs"
            simple_pattern = r'^\d+\s+[A-Z\s,]+?\s+([A-Z\s]+?)\s+jobs'
            match = re.search(simple_pattern, sentence)
            if match:
                print(f"  ✅ Simple match: '{match.group(1).strip()}'")

if __name__ == "__main__":
    debug_pattern_extraction()