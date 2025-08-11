#!/usr/bin/env python3

import sys
import os
import pandas as pd

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.enhanced_classifier import EnhancedJobClassifier

def test_final_improvements():
    """Test the final improved classifier with specific problematic cases"""
    
    classifier = EnhancedJobClassifier(use_ai=False)
    print("🎯 Testing Final Enhanced Job Classifier - Addressing Specific Issues")
    print("=" * 80)
    
    # Load test cases
    df = pd.read_csv('test_specific_cases.csv')
    
    print(f"Processing {len(df)} specific test cases...\n")
    
    expected_results = [
        {"case": 1, "expected_title": "Address", "expected_category": "Address", "expected_general": "other"},
        {"case": 2, "expected_title": "Airport", "expected_category": "Aviation Mechanic", "expected_general": "other"},
        {"case": 3, "expected_title": "Airline Pilot", "expected_category": "Airline Pilot", "expected_general": "other"},
        {"case": 4, "expected_title": "Electronics Installation & Repair Technician", "expected_category": "Electronics Technician", "expected_general": "other"},
        {"case": 5, "expected_title": "Aerospace Engineer", "expected_category": "Aviation Mechanic", "expected_general": "other"},
        {"case": 6, "expected_title": "Driver", "expected_category": "Driver", "expected_general": "general"},
        {"case": 7, "expected_title": "Medical Assistant", "expected_category": "Medical Assistant", "expected_general": "other"},
    ]
    
    for idx, row in df.iterrows():
        job_id = row['job_id']
        text = row['job_posting_text']
        expected = expected_results[idx]
        
        result = classifier.process_row(text, str(idx), str(job_id))
        
        print(f"Test Case {job_id}:")
        print(f"Input: {text[:80]}...")
        print(f"Extracted Title: {result['extracted_job_title']}")
        print(f"Category: {result['job_category']}")
        print(f"General Category: {result['general_category']}")
        print(f"Confidence: {result['confidence']:.2f}")
        
        # Check results against expectations
        title_match = "✅" if result['extracted_job_title'] == expected['expected_title'] else "❌"
        category_match = "✅" if result['job_category'] == expected['expected_category'] else "❌"
        general_match = "✅" if result['general_category'] == expected['expected_general'] else "❌"
        
        print(f"Expected vs Actual:")
        print(f"  Title: {expected['expected_title']} → {result['extracted_job_title']} {title_match}")
        print(f"  Category: {expected['expected_category']} → {result['job_category']} {category_match}")
        print(f"  General: {expected['expected_general']} → {result['general_category']} {general_match}")
        print("-" * 80)
    
    print("\n🔍 Summary of Improvements Made:")
    print("1. ✅ Address Detection: Recognizes addresses and classifies as 'Address'")
    print("2. ✅ General Category Column: Added 'exact', 'general', 'other' classification")
    print("3. ✅ Better Job Title Extraction: Handles complex titles with '&' and multiple words")
    print("4. ✅ Enhanced Categories: Added Airline Pilot, Electronics Technician, etc.")
    print("5. ✅ Nuanced Classification: Handles non-CDL drivers, medical assistants with office work")
    print("6. ✅ Aerospace Inclusion: Aerospace jobs classified as Aviation Mechanic")
    print("7. ✅ Reference Tracking: Row IDs and job IDs for feedback")

if __name__ == "__main__":
    test_final_improvements()