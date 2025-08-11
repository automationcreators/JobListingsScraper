#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import re

def debug_alternative_pattern():
    """Debug why the alternative pattern isn't working correctly"""
    
    text = "Aviation Safety Inspector jobs in Georgia. 100+ jobs. Aircraft Interior Installer."
    
    print("🔍 DEBUGGING ALTERNATIVE PATTERN")
    print("=" * 70)
    print(f"Input: {text}")
    
    # Split by periods to get sentences
    sentences = text.split('.')
    print(f"\nSentences found: {len(sentences)}")
    for i, sentence in enumerate(sentences):
        print(f"  Sentence {i}: '{sentence.strip()}'")
    
    if len(sentences) >= 3:
        first_sentence = sentences[0].strip()
        second_sentence = sentences[1].strip()
        third_sentence = sentences[2].strip()
        
        print(f"\nFirst sentence: '{first_sentence}'")
        print(f"Second sentence: '{second_sentence}'")
        print(f"Third sentence: '{third_sentence}'")
        
        # Test patterns
        first_pattern = r'^[A-Za-z\s]+\s+jobs?\s+in\s+[A-Za-z\s,]+'
        second_pattern = r'^\d+\+?\s+jobs?'
        third_pattern = r'^([^\.]+)'
        alt_first_pattern = r'^([A-Z][A-Za-z\s&]+?)\s+jobs?\s+in\s+[A-Za-z\s,]+'
        
        print(f"\n🧪 Testing Patterns:")
        
        # Test main pattern conditions
        first_match = re.match(first_pattern, first_sentence, re.IGNORECASE)
        second_match = re.match(second_pattern, second_sentence, re.IGNORECASE)
        print(f"First pattern (general jobs): {bool(first_match)} - '{first_match.group(0) if first_match else 'No match'}'")
        print(f"Second pattern (number jobs): {bool(second_match)} - '{second_match.group(0) if second_match else 'No match'}'")
        
        # Test alternative pattern conditions
        alt_first_match = re.match(alt_first_pattern, first_sentence, re.IGNORECASE)
        print(f"Alt first pattern (specific job): {bool(alt_first_match)} - '{alt_first_match.group(1) if alt_first_match else 'No match'}'")
        
        print(f"\n🎯 Logic Decision:")
        main_pattern_match = (first_match and second_match and len(third_sentence) > 0)
        alt_pattern_match = (len(sentences) >= 2 and alt_first_match and second_match)
        
        print(f"Main pattern qualifies: {main_pattern_match}")
        print(f"Alt pattern qualifies: {alt_pattern_match}")
        
        if main_pattern_match:
            third_match = re.match(third_pattern, third_sentence)
            title_from_third = third_match.group(1).strip() if third_match else "No match"
            print(f"Title from third sentence: '{title_from_third}'")
        
        if alt_pattern_match:
            title_from_first = alt_first_match.group(1).strip()
            print(f"Title from first sentence: '{title_from_first}'")
        
        print(f"\n❗ ISSUE: Both patterns match, but main pattern runs first and extracts from third sentence")
        print(f"💡 SOLUTION: Need to prioritize alternative pattern or modify conditions")

if __name__ == "__main__":
    debug_alternative_pattern()