#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.advanced_classifier import AdvancedJobClassifier

def test_improved_address_detection():
    """Test the improved address detection with job posting context awareness"""
    
    classifier = AdvancedJobClassifier(use_ai=False)
    print("🧪 Testing Improved Address Detection")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "Job posting with location (should NOT be address)",
            "text": "185 Airport jobs available in Surprise, AZ 85388 on Indeed.com. Apply to Baggage Handler, Cleaner, Customer Service Representative and more!Missing: 2CAZ | Show results with:",
            "expected_is_address": False,
            "expected_title": "Airport",
            "expected_category": "Aviation Mechanic"
        },
        {
            "name": "Another job posting with location",
            "text": "50 HVAC Technician jobs available in Phoenix, AZ 85001 on Indeed.com. Apply to Technician, Installer and more!",
            "expected_is_address": False,
            "expected_title": "Hvac Technician",
            "expected_category": "HVAC Technician"
        },
        {
            "name": "Actual street address (should be address)",
            "text": "1234 Main Street, Phoenix, AZ 85001",
            "expected_is_address": True,
            "expected_title": "Address", 
            "expected_category": "Address"
        },
        {
            "name": "Job posting with hiring in location",
            "text": "We are hiring in Dallas, TX 75201. Multiple positions available!",
            "expected_is_address": False,
            "expected_title": "Unable to extract job title",
            "expected_category": "Unable to Classify"
        },
        {
            "name": "Email-style address pattern",
            "text": "email: contact info:: 12345 ::",
            "expected_is_address": True,
            "expected_title": "Address",
            "expected_category": "Address"
        }
    ]
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        print(f"\\nTest Case {i}: {case['name']}")
        print(f"Input: {case['text'][:60]}...")
        
        # Test address detection
        is_address = classifier.is_address(case['text'])
        address_match = "✅" if is_address == case['expected_is_address'] else "❌"
        
        # Test full processing
        result = classifier.process_row(case['text'], str(i))
        
        title_match = "✅" if result['extracted_job_title'] == case['expected_title'] else "❌"
        category_match = "✅" if result['job_category'] == case['expected_category'] else "❌"
        
        print(f"Address Detection: {is_address} (expected: {case['expected_is_address']}) {address_match}")
        print(f"Job Title: {result['extracted_job_title']} (expected: {case['expected_title']}) {title_match}")
        print(f"Category: {result['job_category']} (expected: {case['expected_category']}) {category_match}")
        print(f"Confidence: {result['confidence']:.2f}")
        
        if not (is_address == case['expected_is_address'] and 
                result['extracted_job_title'] == case['expected_title'] and 
                result['job_category'] == case['expected_category']):
            all_passed = False
            print("❌ FAILED")
        else:
            print("✅ PASSED")
        
        print("-" * 60)
    
    print(f"\\n🎯 SUMMARY:")
    if all_passed:
        print("✅ All tests PASSED! Address detection is now context-aware.")
        print("✅ Job postings with locations are correctly identified as job postings")
        print("✅ Actual addresses are still correctly identified as addresses")
    else:
        print("❌ Some tests FAILED - review results above")
    
    return all_passed

if __name__ == "__main__":
    success = test_improved_address_detection()
    exit(0 if success else 1)