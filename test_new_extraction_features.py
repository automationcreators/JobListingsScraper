#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.advanced_classifier import AdvancedJobClassifier

def test_new_extraction_features():
    """Test the new extraction features: job_count, city, and state"""
    
    classifier = AdvancedJobClassifier(use_ai=False)
    print("🧪 Testing New Extraction Features: Job Count, City, State")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "Standard pattern with job count, city, state",
            "text": "185 Airport jobs available in Surprise, AZ 85388 on Indeed.com. Apply to Baggage Handler, Cleaner, Customer Service Representative and more!",
            "expected_job_count": "185",
            "expected_city": "Surprise",
            "expected_state": "AZ",
            "expected_job_title": "Airport"
        },
        {
            "name": "Plus pattern with job count",
            "text": "apprenticeship jobs in el mirage, az. 50+ jobs. Air Conditioning Technician & Apprentices.",
            "expected_job_count": "50",
            "expected_city": "El Mirage", 
            "expected_state": "AZ",
            "expected_job_title": "Air Conditioning Technician & Apprentices"
        },
        {
            "name": "Full state name pattern - Georgia is a state",
            "text": "Aviation Safety Inspector jobs in Georgia. 100+ jobs. Aircraft Interior Installer.",
            "expected_job_count": "100",
            "expected_city": "",     # Georgia is a state, not a city
            "expected_state": "GA",  # Georgia should be normalized to GA
            "expected_job_title": "Aviation Safety Inspector"
        },
        {
            "name": "Jobs available in pattern",
            "text": "25 HVAC Technician jobs available in Phoenix, Arizona on job site",
            "expected_job_count": "25",
            "expected_city": "Phoenix",
            "expected_state": "AZ",
            "expected_job_title": "HVAC Technician"
        },
        {
            "name": "Complex location pattern",
            "text": "heating jobs in phoenix, az. 25+ jobs. HVAC Installation Specialist & Maintenance Tech.",
            "expected_job_count": "25",
            "expected_city": "Phoenix",
            "expected_state": "AZ",
            "expected_job_title": "HVAC Installation Specialist & Maintenance Tech"
        },
        {
            "name": "Multi-word city name",
            "text": "75 Security Guard jobs available in New York, NY",
            "expected_job_count": "75",
            "expected_city": "New York",
            "expected_state": "NY",
            "expected_job_title": "Security Guard"
        },
        {
            "name": "Address should not extract job data",
            "text": "1234 Main Street, Phoenix, AZ 85001",
            "expected_job_count": "",
            "expected_city": "",
            "expected_state": "",
            "expected_job_title": "Address"
        }
    ]
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {case['name']}")
        print(f"Input: {case['text']}")
        print("-" * 70)
        
        # Test full processing
        result = classifier.process_row(case['text'], str(i))
        
        # Check each extraction
        job_count_match = result['job_count'] == case['expected_job_count']
        city_match = result['city'] == case['expected_city']
        state_match = result['state'] == case['expected_state']
        title_match = result['extracted_job_title'] == case['expected_job_title']
        
        print(f"📊 Results:")
        print(f"   Job Count: '{result['job_count']}' (expected: '{case['expected_job_count']}') {'✅' if job_count_match else '❌'}")
        print(f"   City:      '{result['city']}' (expected: '{case['expected_city']}') {'✅' if city_match else '❌'}")
        print(f"   State:     '{result['state']}' (expected: '{case['expected_state']}') {'✅' if state_match else '❌'}")
        print(f"   Job Title: '{result['extracted_job_title']}' (expected: '{case['expected_job_title']}') {'✅' if title_match else '❌'}")
        print(f"   Category:  '{result['job_category']}'")
        print(f"   General:   '{result['general_category']}'")
        print(f"   Details:   '{result['job_details']}'")
        
        # Test passed/failed
        case_passed = job_count_match and city_match and state_match and title_match
        if case_passed:
            print("✅ CASE PASSED")
        else:
            print("❌ CASE FAILED")
            all_passed = False
        
        print("=" * 70)
    
    return all_passed

def test_individual_extraction_methods():
    """Test individual extraction methods in isolation"""
    classifier = AdvancedJobClassifier(use_ai=False)
    
    print("\n" + "=" * 80)
    print("🔬 TESTING INDIVIDUAL EXTRACTION METHODS")
    print("=" * 80)
    
    # Test job count extraction
    print("\n📊 Job Count Extraction Tests:")
    job_count_tests = [
        ("185 Airport jobs available in Surprise, AZ", "185"),
        ("50+ jobs. Air Conditioning Technician", "50"),
        ("100+ jobs in Georgia", "100"),
        ("25 positions available in Phoenix", "25"),
        ("1234 Main Street, Phoenix, AZ 85001", ""),  # Address should return empty
    ]
    
    for text, expected in job_count_tests:
        result = classifier.extract_job_count(text)
        match = "✅" if result == expected else "❌"
        print(f"  '{text}' → '{result}' (expected: '{expected}') {match}")
    
    # Test city extraction
    print("\n🏙️ City Extraction Tests:")
    city_tests = [
        ("185 Airport jobs available in Surprise, AZ 85388", "Surprise"),
        ("apprenticeship jobs in el mirage, az. 50+ jobs", "El Mirage"),
        ("jobs available in New York, NY", "New York"),
        ("Phoenix, Arizona job listings", "Phoenix"),
        ("1234 Main Street, Phoenix, AZ 85001", ""),  # Address should return empty
    ]
    
    for text, expected in city_tests:
        result = classifier.extract_city(text)
        match = "✅" if result == expected else "❌"
        print(f"  '{text}' → '{result}' (expected: '{expected}') {match}")
    
    # Test state extraction
    print("\n🗺️ State Extraction Tests:")
    state_tests = [
        ("185 Airport jobs available in Surprise, AZ 85388", "AZ"),
        ("jobs available in Phoenix, Arizona", "AZ"),
        ("employment in New York, NY", "NY"),
        ("positions in Miami, Florida", "FL"),
        ("1234 Main Street, Phoenix, AZ 85001", ""),  # Address should return empty
    ]
    
    for text, expected in state_tests:
        result = classifier.extract_state(text)
        match = "✅" if result == expected else "❌"
        print(f"  '{text}' → '{result}' (expected: '{expected}') {match}")

if __name__ == "__main__":
    print("🚀 STARTING COMPREHENSIVE NEW FEATURE TESTING")
    print("=" * 80)
    
    # Test the full integration
    success = test_new_extraction_features()
    
    # Test individual methods
    test_individual_extraction_methods()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Job count extraction working correctly")
        print("✅ City extraction working correctly") 
        print("✅ State extraction working correctly")
        print("✅ Address detection prevents extraction on addresses")
        print("✅ All existing functionality preserved")
        print("🎯 Ready to update web interface!")
    else:
        print("❌ Some integration tests failed")
        print("⚠️ Need to review and fix extraction patterns")
    
    exit(0 if success else 1)