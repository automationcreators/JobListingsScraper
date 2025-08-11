#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.enhanced_classifier import EnhancedJobClassifier
import re

def debug_full_extraction():
    text = "59 Aircraft Jobs in Cape Coral Metropolitan Area (1 new). Aircraft Maintenance Technician - RSW + $10,000 Bonus! Aircraft Maintenance Technician - RSW + $10,000 ...Missing:  2CFL | Show results with:"
    
    classifier = EnhancedJobClassifier(use_ai=False)
    
    print(f"Text: {text}")
    print("=" * 80)
    
    # Step through the extraction process
    print("1. Cleaning text from noise patterns...")
    cleaned_text = text
    for pattern in classifier.noise_patterns:
        before = cleaned_text
        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        if before != cleaned_text:
            print(f"   Removed by pattern '{pattern}': '{before}' -> '{cleaned_text}'")
    
    print(f"Cleaned text: {cleaned_text}")
    print()
    
    print("2. Splitting into sentences...")
    sentences = re.split(r'[.!?]', cleaned_text)
    for i, sentence in enumerate(sentences):
        print(f"   Sentence {i}: '{sentence.strip()}'")
    print()
    
    print("3. Processing each sentence...")
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if len(sentence) < 10:
            print(f"   Sentence {i}: Too short, skipping")
            continue
            
        print(f"   Processing sentence {i}: '{sentence}'")
        
        # Test the pattern that should work
        pattern = r'(?:^|\.\s+)([A-Za-z\s&]+?(?:maintenance|repair|installation|technician|mechanic|pilot|specialist|manager)\s*(?:technician|mechanic|specialist|manager|pilot)?)\s*[-+]\s*[A-Z]'
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            print(f"     ✅ Pattern matched: '{title}'")
            
            # Test cleaning
            cleaned_title = classifier._clean_job_title(title)
            print(f"     Cleaned title: '{cleaned_title}'")
            
            # Test validation
            if cleaned_title and len(cleaned_title) > 2:
                if 'maintenance technician' in cleaned_title.lower():
                    print(f"     ✅ Special handling for maintenance technician")
                    return cleaned_title
                elif classifier._validate_job_title(cleaned_title):
                    print(f"     ✅ Validation passed")
                    return cleaned_title
                else:
                    print(f"     ❌ Validation failed")
        else:
            print(f"     ❌ No pattern match")
    
    print("4. Trying full extraction...")
    result = classifier.extract_job_title(text)
    print(f"Final result: '{result}'")

if __name__ == "__main__":
    debug_full_extraction()