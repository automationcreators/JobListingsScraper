#!/usr/bin/env python3

import re

def debug_extraction():
    test_cases = [
        "153 Airport jobs available in Buckeye, AZ on Indeed.com. Apply to Customer Service Representative",
        "40 Airline Pilot jobs available in Buckeye, AZ on Indeed.com. Apply to Customer Service"
    ]
    
    patterns = [
        # Pattern: Specific complex job titles first (highest priority)
        r'(\d+)?\s*(electronics\s+installation\s*&?\s*repair\s+technicians?|electronics\s+installation\s+and\s+repair\s+technicians?)\s+(?:jobs?|positions?)',
        r'(\d+)?\s*(airline\s+pilots?|commercial\s+pilots?)\s+(?:jobs?|positions?)',
        r'(\d+)?\s*(aircraft\s+maintenance\s+technicians?|aviation\s+mechanics?)\s+(?:jobs?|positions?)',
        r'(\d+)?\s*(aerospace\s+engineers?)\s+(?:jobs?|positions?)',
        r'(\d+)?\s*(medical\s+assistants?)\s+(?:jobs?|positions?)',
        
        # Pattern: Single word job categories (for cases like "Airport jobs", "Driver jobs")
        r'(\d+)?\s*(airport|aviation|aircraft|airline\s+pilot|driver|security|construction|hvac|electrical|plumbing|welding|medical|dental|veterinary)\s+(?:jobs?|positions?)',
        
        # Pattern: "X [job title] positions/jobs"  
        r'(\d+)?\s*([A-Za-z\s&]+?(?:technicians?|techs?|mechanics?|specialists?|assistants?|aides?|managers?|coordinators?|supervisors?|directors?|analysts?|engineers?|developers?|designers?|operators?|workers?|drivers?|nurses?|therapists?|pathologists?|electricians?|plumbers?|welders?|guards?|officers?|pilots?))\s+(?:jobs?|positions?|openings?)',
    ]
    
    for text in test_cases:
        print(f"\nTesting: {text}")
        print("-" * 50)
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                print(f"Pattern {i+1} matched:")
                print(f"  Full match: {match.group(0)}")
                for j, group in enumerate(match.groups()):
                    if group:
                        print(f"  Group {j+1}: {group}")
                break
        else:
            print("No patterns matched")

if __name__ == "__main__":
    debug_extraction()