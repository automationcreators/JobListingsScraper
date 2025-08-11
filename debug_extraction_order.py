#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.advanced_classifier import AdvancedJobClassifier

def debug_extraction_order():
    """Debug the extraction order and identify why wrong titles are being extracted"""
    
    classifier = AdvancedJobClassifier(use_ai=False)
    
    test_text = "apprenticeship jobs in el mirage, az. 50+ jobs. Air Conditioning Technician & Apprentices."
    
    print("🔍 DEBUGGING EXTRACTION ORDER")
    print("=" * 70)
    print(f"Input: {test_text}")
    print("=" * 70)
    
    # Split into sentences manually to see what we're working with
    sentences = test_text.split('.')
    print(f"Sentences found: {len(sentences)}")
    for i, sentence in enumerate(sentences):
        print(f"  Sentence {i}: '{sentence.strip()}'")
    
    print("\n" + "=" * 70)
    
    # Test first sentence extraction
    first_sentence = sentences[0].strip() if sentences else test_text
    print(f"🎯 Testing first sentence extraction:")
    print(f"First sentence: '{first_sentence}'")
    
    first_result = classifier._extract_from_first_sentence(first_sentence)
    print(f"First sentence result: '{first_result}'")
    
    # Test new structure extraction
    print(f"\n🎯 Testing new structure extraction:")
    new_result = classifier._extract_from_quantity_later_structure(test_text)
    print(f"New structure result: '{new_result}'")
    
    # Test the priority system in the main method
    print(f"\n🎯 Testing main extraction method:")
    main_result = classifier.extract_job_title_rules(test_text)
    print(f"Main method result: '{main_result}'")
    
    print("\n" + "=" * 70)
    print("ANALYSIS:")
    print("The issue might be that the first sentence extraction is succeeding")
    print("when it should fail for this new pattern type.")
    print("We need to adjust the logic to prioritize the new structure")
    print("when the pattern matches the 'general jobs in location. NUMBER+ jobs. Specific Job Title' format.")

if __name__ == "__main__":
    debug_extraction_order()