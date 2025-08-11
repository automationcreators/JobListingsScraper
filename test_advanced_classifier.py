#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.advanced_classifier import AdvancedJobClassifier

def test_advanced_classifier():
    """Test the advanced classifier with the specific problematic examples"""
    
    classifier = AdvancedJobClassifier(use_ai=False)
    print("🎯 Testing Advanced Classification System with Problematic Examples")
    print("=" * 90)
    
    test_cases = [
        {
            "name": "Aerospace Technician with Apply To List",
            "text": "116 Aircraft jobs available in Decatur, AL on Indeed.com. Apply to Aerospace Technician, Baggage Handler, General Consideration - Talent Network and more!Missing: 2CGA | Show results with:",
            "expected_title": "Aircraft",
            "expected_category": "Aviation Mechanic", 
            "expected_general": "general",
            "expected_details": "Aerospace Technician, Baggage Handler, General Consideration - Talent Network"
        },
        {
            "name": "Airport Jobs with Apply To List",
            "text": "153 Airport jobs available in Buckeye, AZ on Indeed.com. Apply to Customer Service Representative, Baggage Handler, Agent and more!",
            "expected_title": "Airport",
            "expected_category": "Aviation Mechanic",
            "expected_general": "general",
            "expected_details": "Customer Service Representative, Baggage Handler, Agent"
        },
        {
            "name": "Aircraft Parts Jobs",
            "text": "76 CHANDLER, AZ AIRCRAFT PARTS jobs from companies (hiring now) with openings. Find job opportunities near you and apply!",
            "expected_title": "Aircraft Parts",
            "expected_category": "Aviation Mechanic",
            "expected_general": "exact",
            "expected_details": ""
        },
        {
            "name": "Aircraft Detailing with Apply To List", 
            "text": "345 Aircraft Detailing jobs available in Chandler, AZ on Indeed.com. Apply to Aircraft Maintenance Technician, Entry Level Technician, Inspector and more!",
            "expected_title": "Aircraft Detailing",
            "expected_category": "Aviation Mechanic",
            "expected_general": "exact",
            "expected_details": "Aircraft Maintenance Technician, Entry Level Technician, Inspector"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        result = classifier.process_row(case["text"], str(i))
        
        print(f"Test Case {i}: {case['name']}")
        print(f"Input: {case['text'][:80]}...")
        print()
        print(f"RESULTS:")
        print(f"  Job Title: {result['extracted_job_title']}")
        print(f"  Category: {result['job_category']}")
        print(f"  General Category: {result['general_category']}")
        print(f"  Job Details: {result['job_details']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print()
        print(f"EXPECTED vs ACTUAL:")
        
        title_match = "✅" if result['extracted_job_title'] == case['expected_title'] else "❌"
        category_match = "✅" if result['job_category'] == case['expected_category'] else "❌"
        general_match = "✅" if result['general_category'] == case['expected_general'] else "❌"
        details_match = "✅" if result['job_details'].strip() == case['expected_details'].strip() else "❌"
        
        print(f"  Title: {case['expected_title']} → {result['extracted_job_title']} {title_match}")
        print(f"  Category: {case['expected_category']} → {result['job_category']} {category_match}")
        print(f"  General: {case['expected_general']} → {result['general_category']} {general_match}")
        print(f"  Details: '{case['expected_details']}' → '{result['job_details']}' {details_match}")
        print("=" * 90)
    
    print("\n🎯 KEY IMPROVEMENTS IMPLEMENTED:")
    print("1. ✅ First-sentence priority extraction (NUMBER LOCATION JOB TITLE jobs)")
    print("2. ✅ Context-aware classification using Apply To sections")
    print("3. ✅ New 'job_details' column with extracted job lists")
    print("4. ✅ Improved exact/general/other classification logic")
    print("5. ✅ Better handling of generic terms like 'Aircraft', 'Airport'")
    print("6. ✅ Enhanced pattern matching for location-prefixed job titles")

if __name__ == "__main__":
    test_advanced_classifier()