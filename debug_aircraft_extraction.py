#!/usr/bin/env python3

import re

def debug_aircraft_extraction():
    text = "59 Aircraft Jobs in Cape Coral Metropolitan Area (1 new). Aircraft Maintenance Technician - RSW + $10,000 Bonus! Aircraft Maintenance Technician - RSW + $10,000 ...Missing:  2CFL | Show results with:"
    
    print(f"Text: {text}")
    print("=" * 80)
    
    # Test each pattern individually
    patterns = [
        # Pattern 1: Extract full job titles from complex sentences
        r'(?:^|\.\s+)([A-Za-z\s&]+?(?:maintenance|repair|installation|technician|mechanic|pilot|specialist|manager)\s*(?:technician|mechanic|specialist|manager|pilot)?)\s*[-+]\s*[A-Z]',
        
        # Pattern 2: Extract job titles mentioned in the middle
        r'([A-Z][A-Za-z\s&]*?(?:maintenance|repair|installation)\s+technicians?)\s*[-+]',
        
        # Pattern 3: Specific aircraft maintenance 
        r'(\d+)?\s*(aircraft\s+maintenance\s+technicians?|aviation\s+maintenance\s+technicians?)\s+(?:jobs?|positions?|-)',
    ]
    
    for i, pattern in enumerate(patterns, 1):
        print(f"Testing Pattern {i}: {pattern}")
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            print(f"  ✅ Match found: {match.group(0)}")
            print(f"  Groups: {match.groups()}")
            
            # Get the job title
            title = None
            if len(match.groups()) >= 2 and match.group(2):
                title = match.group(2).strip()
            elif match.group(1):
                title = match.group(1).strip()
            
            print(f"  Extracted title: '{title}'")
        else:
            print(f"  ❌ No match")
        print()
    
    # Test a simpler approach
    print("Testing simpler approach:")
    simple_pattern = r'Aircraft\s+Maintenance\s+Technician'
    match = re.search(simple_pattern, text, re.IGNORECASE)
    if match:
        print(f"  ✅ Simple match found: {match.group(0)}")
    else:
        print(f"  ❌ Simple match failed")

if __name__ == "__main__":
    debug_aircraft_extraction()