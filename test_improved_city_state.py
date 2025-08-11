#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.advanced_classifier import AdvancedJobClassifier

def test_improved_city_state_extraction():
    """Test the improved city and state extraction patterns"""
    
    classifier = AdvancedJobClassifier(use_ai=False)
    print("🧪 Testing Improved City & State Extraction")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "Pattern: NUMBER CITY, STATE AIRCRAFT - Buckeye",
            "text": "47 BUCKEYE, AZ AIRCRAFT MAINTENANCE jobs from companies (hiring now) with openings. Find job opportunities near you and apply!Missing: linked. | Show results with:",
            "expected_city": "Buckeye",
            "expected_state": "AZ",
            "expected_count": "47"
        },
        {
            "name": "Pattern: NUMBER CITY, STATE AIRCRAFT PARTS - Chandler",
            "text": "76 CHANDLER, AZ AIRCRAFT PARTS jobs from companies (hiring now) with openings. Find job opportunities near you and apply!",
            "expected_city": "Chandler", 
            "expected_state": "AZ",
            "expected_count": "76"
        },
        {
            "name": "Pattern: NUMBER CITY, STATE AIRCRAFT - Flagstaff",
            "text": "33 FLAGSTAFF, AZ AIRCRAFT MAINTENANCE jobs from companies (hiring now) with openings. Find job opportunities near you and apply!Missing: linked. | Show results with:",
            "expected_city": "Flagstaff",
            "expected_state": "AZ", 
            "expected_count": "33"
        },
        {
            "name": "Pattern: NUMBER CITY, STATE - Cape Coral",
            "text": "46 CAPE CORAL, FL AIRCRAFT MAINTENANCE jobs from companies (hiring now) with openings. Find job opportunities near you and apply!Missing: linked. | Show results with:",
            "expected_city": "Cape Coral",
            "expected_state": "FL",
            "expected_count": "46"
        },
        {
            "name": "Pattern: services in CITY, STATE - Port St. Lucie",
            "text": "100% satisfaction guaranteed on heating and air conditioning services in Port St. Lucie, FL including AC repair, installation and maintenance.",
            "expected_city": "Port St. Lucie",
            "expected_state": "FL",
            "expected_count": ""  # No job count in this text
        },
        {
            "name": "Existing pattern should still work - Standard format",
            "text": "185 Airport jobs available in Surprise, AZ 85388 on Indeed.com.",
            "expected_city": "Surprise",
            "expected_state": "AZ", 
            "expected_count": "185"
        }
    ]
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {case['name']}")
        print(f"Input: {case['text']}")
        print("-" * 70)
        
        # Extract using new methods
        job_count = classifier.extract_job_count(case['text'])
        city = classifier.extract_city(case['text'])
        state = classifier.extract_state(case['text'])
        
        # Check results
        count_match = job_count == case['expected_count']
        city_match = city == case['expected_city']
        state_match = state == case['expected_state']
        
        print(f"📊 Results:")
        print(f"   Job Count: '{job_count}' (expected: '{case['expected_count']}') {'✅' if count_match else '❌'}")
        print(f"   City:      '{city}' (expected: '{case['expected_city']}') {'✅' if city_match else '❌'}")
        print(f"   State:     '{state}' (expected: '{case['expected_state']}') {'✅' if state_match else '❌'}")
        
        # Test passed/failed
        case_passed = count_match and city_match and state_match
        if case_passed:
            print("✅ CASE PASSED")
        else:
            print("❌ CASE FAILED")
            all_passed = False
        
        print("=" * 70)
    
    return all_passed

def test_individual_patterns():
    """Test specific regex patterns"""
    classifier = AdvancedJobClassifier(use_ai=False)
    
    print(f"\n🔬 TESTING INDIVIDUAL PATTERNS")
    print("=" * 80)
    
    # Test the new number-city-state pattern
    import re
    pattern = r'^\d+\s+([A-Z][A-Za-z\s]{1,25}),\s*([A-Z]{2})\s+'
    test_texts = [
        "47 BUCKEYE, AZ AIRCRAFT MAINTENANCE",
        "76 CHANDLER, AZ AIRCRAFT PARTS", 
        "33 FLAGSTAFF, AZ AIRCRAFT MAINTENANCE",
        "46 CAPE CORAL, FL AIRCRAFT MAINTENANCE"
    ]
    
    print("📊 Number-City-State Pattern Tests:")
    for text in test_texts:
        match = re.match(pattern, text)
        if match:
            city, state = match.groups()
            print(f"  '{text}' → City: '{city}', State: '{state}' ✅")
        else:
            print(f"  '{text}' → No match ❌")
    
    # Test services pattern
    services_pattern = r'\b(?:services?|work|business)\s+in\s+([A-Za-z\s\.]{2,30}),\s*([A-Z]{2})\b'
    services_text = "services in Port St. Lucie, FL including"
    
    print(f"\n🏢 Services Pattern Test:")
    match = re.search(services_pattern, services_text, re.IGNORECASE)
    if match:
        city, state = match.groups()
        print(f"  '{services_text}' → City: '{city}', State: '{state}' ✅")
    else:
        print(f"  '{services_text}' → No match ❌")

if __name__ == "__main__":
    print("🚀 TESTING IMPROVED CITY & STATE EXTRACTION")
    print("=" * 80)
    
    # Test the full integration
    success = test_improved_city_state_extraction()
    
    # Test individual patterns
    test_individual_patterns()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 ALL IMPROVED EXTRACTION TESTS PASSED!")
        print("✅ Number-City-State pattern working (47 BUCKEYE, AZ format)")
        print("✅ Services pattern working (services in Port St. Lucie, FL format)")
        print("✅ Existing patterns still working correctly")
        print("✅ Multi-word cities handled properly (Cape Coral, Port St. Lucie)")
        print("🎯 Ready for production use!")
    else:
        print("❌ Some tests failed - need to review patterns")
    
    exit(0 if success else 1)