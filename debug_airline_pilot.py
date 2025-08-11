#!/usr/bin/env python3

import re

def debug_airline_pilot():
    text = "40 Airline Pilot jobs available in Buckeye, AZ on Indeed.com. Apply to Customer Service Representative, Customer Service Rep and more!"
    
    # Pattern that should match
    pattern = r'(\d+)?\s*(airline\s+pilots?|commercial\s+pilots?)\s+(?:jobs?|positions?)'
    
    print(f"Text: {text}")
    print(f"Pattern: {pattern}")
    
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        print(f"Match found: {match.group(0)}")
        print(f"Groups: {match.groups()}")
        
        # Test the cleaning function
        title = match.group(2) if len(match.groups()) >= 2 and match.group(2) else match.group(1)
        print(f"Raw title: {title}")
        
        # Clean title
        noise_words = ['jobs', 'job', 'positions', 'position', 'available', 'needed', 'wanted', 'hiring']
        words = [word for word in title.strip().split() if word.lower() not in noise_words and len(word) > 1]
        cleaned = ' '.join(words).strip()
        print(f"Cleaned title: {cleaned}")
        
        # Validate
        job_keywords = ['pilot', 'technician', 'mechanic', 'specialist', 'assistant', 'manager']
        valid = any(keyword in cleaned.lower() for keyword in job_keywords)
        print(f"Valid: {valid}")
    else:
        print("No match found")

if __name__ == "__main__":
    debug_airline_pilot()