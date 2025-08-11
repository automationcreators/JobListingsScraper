#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.advanced_classifier import AdvancedJobClassifier

def test_new_job_structure():
    """Test the new job posting structure patterns"""
    
    classifier = AdvancedJobClassifier(use_ai=False)
    print("🧪 Testing New Job Structure Patterns")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "New structure - Air Conditioning Technician",
            "text": "apprenticeship jobs in el mirage, az. 50+ jobs. Air Conditioning Technician & Apprentices.",
            "expected_title": "Air Conditioning Technician & Apprentices",
            "expected_category": "HVAC Technician",
            "expected_general": "exact"
        },
        {
            "name": "Alternative structure - Aviation Safety Inspector",
            "text": "Aviation Safety Inspector jobs in Georgia. 100+ jobs. Aircraft Interior Installer.",
            "expected_title": "Aviation Safety Inspector", 
            "expected_category": "Aviation Mechanic",
            "expected_general": "exact"
        },
        {
            "name": "Standard structure - Should still work",
            "text": "185 Airport jobs available in Surprise, AZ 85388 on Indeed.com. Apply to Baggage Handler, Cleaner, Customer Service Representative and more!",
            "expected_title": "Airport",
            "expected_category": "Aviation Mechanic", 
            "expected_general": "general"
        },
        {
            "name": "Complex HVAC structure",
            "text": "heating jobs in phoenix, az. 25+ jobs. HVAC Installation Specialist & Maintenance Tech.",
            "expected_title": "HVAC Installation Specialist & Maintenance Tech",
            "expected_category": "HVAC Technician",
            "expected_general": "exact"
        }
    ]
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {case['name']}")
        print(f"Input: {case['text']}")
        print("-" * 60)
        
        # Test full processing
        result = classifier.process_row(case['text'], str(i))
        
        # Check each result
        title_match = result['extracted_job_title'] == case['expected_title']
        category_match = result['job_category'] == case['expected_category']
        general_match = result['general_category'] == case['expected_general']
        
        print(f"📋 Results:")
        print(f"   Job Title: {result['extracted_job_title']}")
        print(f"   Expected:  {case['expected_title']} {'✅' if title_match else '❌'}")
        print()
        print(f"   Category: {result['job_category']}")
        print(f"   Expected: {case['expected_category']} {'✅' if category_match else '❌'}")
        print()
        print(f"   General: {result['general_category']}")
        print(f"   Expected: {case['expected_general']} {'✅' if general_match else '❌'}")
        print()
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Job Details: {result['job_details']}")
        
        # Test passed/failed
        case_passed = title_match and category_match and general_match
        if case_passed:
            print("✅ CASE PASSED")
        else:
            print("❌ CASE FAILED")
            all_passed = False
        
        print("=" * 60)
    
    print(f"\n🎯 OVERALL RESULTS:")
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ New job structure patterns are working correctly")
        print("✅ Air Conditioning Technician properly classified as HVAC Technician (exact)")
        print("✅ Aviation Safety Inspector properly classified as Aviation Mechanic (exact)")
        print("✅ Existing patterns still work correctly")
        print("✅ Job titles with '&' are preserved properly")
    else:
        print("❌ Some tests failed - check results above")
        print("⚠️  New patterns may need additional refinement")
    
    return all_passed

def test_extraction_methods():
    """Test the specific extraction methods"""
    classifier = AdvancedJobClassifier(use_ai=False)
    
    print("\n" + "=" * 70)
    print("🔬 DETAILED EXTRACTION METHOD TESTING")
    print("=" * 70)
    
    # Test the new quantity-later structure method directly
    test_text = "apprenticeship jobs in el mirage, az. 50+ jobs. Air Conditioning Technician & Apprentices."
    
    print("Testing _extract_from_quantity_later_structure method:")
    print(f"Input: {test_text}")
    
    result = classifier._extract_from_quantity_later_structure(test_text)
    print(f"Result: {result}")
    print(f"Expected: Air Conditioning Technician & Apprentices")
    print(f"Match: {'✅' if result == 'Air Conditioning Technician & Apprentices' else '❌'}")
    
    # Test the alternative pattern
    alt_text = "Aviation Safety Inspector jobs in Georgia. 100+ jobs. Aircraft Interior Installer."
    print(f"\nTesting alternative pattern:")
    print(f"Input: {alt_text}")
    
    alt_result = classifier._extract_from_quantity_later_structure(alt_text) 
    print(f"Result: {alt_result}")
    print(f"Expected: Aviation Safety Inspector")
    print(f"Match: {'✅' if alt_result == 'Aviation Safety Inspector' else '❌'}")

if __name__ == "__main__":
    success = test_new_job_structure()
    test_extraction_methods()
    
    print("\n" + "=" * 70)
    if success:
        print("🏆 NEW JOB STRUCTURE IMPLEMENTATION SUCCESSFUL!")
        print("🎯 Ready for user testing with improved patterns")
    else:
        print("⚠️ Implementation needs refinement")
    
    exit(0 if success else 1)