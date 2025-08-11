#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.advanced_classifier import AdvancedJobClassifier

def test_specific_case_fix():
    """Test the specific case that was incorrectly classified as address"""
    
    classifier = AdvancedJobClassifier(use_ai=False)
    print("🎯 Testing Specific Case Fix")
    print("=" * 70)
    
    # Your exact problematic case
    problematic_text = "185 Airport jobs available in Surprise, AZ 85388 on Indeed.com. Apply to Baggage Handler, Cleaner, Customer Service Representative and more!Missing: 2CAZ | Show results with:"
    
    print("BEFORE FIX (this was incorrectly classified as Address)")
    print("AFTER FIX (should now be correctly classified):")
    print()
    print(f"Input text: {problematic_text}")
    print()
    
    # Test address detection
    is_address = classifier.is_address(problematic_text)
    print(f"🔍 Address Detection Result: {is_address}")
    print(f"   Expected: False (not an address)")
    print(f"   Result: {'✅ CORRECT' if not is_address else '❌ STILL WRONG'}")
    print()
    
    # Test full processing
    result = classifier.process_row(problematic_text, "test_row")
    
    print("🎯 Full Classification Results:")
    print(f"   Job Title: {result['extracted_job_title']}")
    print(f"   Category: {result['job_category']}")
    print(f"   General Category: {result['general_category']}")
    print(f"   Confidence: {result['confidence']:.2f}")
    print(f"   Job Details: {result['job_details']}")
    print()
    
    # Expected results
    expected_title = "Airport"
    expected_category = "Aviation Mechanic" 
    expected_general = "general"
    expected_job_details = "Baggage Handler, Cleaner, Customer Service Representative"
    
    print("📋 Expected vs Actual:")
    title_correct = result['extracted_job_title'] == expected_title
    category_correct = result['job_category'] == expected_category
    general_correct = result['general_category'] == expected_general
    details_correct = expected_job_details in result['job_details']
    
    print(f"   Job Title: {expected_title} → {result['extracted_job_title']} {'✅' if title_correct else '❌'}")
    print(f"   Category: {expected_category} → {result['job_category']} {'✅' if category_correct else '❌'}")
    print(f"   General: {expected_general} → {result['general_category']} {'✅' if general_correct else '❌'}")
    print(f"   Job Details: Contains expected details? {'✅' if details_correct else '❌'}")
    print()
    
    # Overall success
    all_correct = (not is_address and title_correct and category_correct and general_correct and details_correct)
    
    if all_correct:
        print("🎉 SUCCESS: The problematic case is now correctly classified!")
        print("✅ No longer incorrectly identified as an address")
        print("✅ Correct job title extraction (Airport)")
        print("✅ Correct category (Aviation Mechanic)")
        print("✅ Correct general category (general)")
        print("✅ Job details properly extracted from Apply To section")
        print()
        print("🎯 The fix works! Job postings with location information")
        print("   are now correctly distinguished from actual addresses.")
    else:
        print("❌ Some issues still remain - see details above")
    
    return all_correct

if __name__ == "__main__":
    success = test_specific_case_fix()
    print("\\n" + "=" * 70)
    if success:
        print("🏆 PROBLEM RESOLVED: Address detection now context-aware!")
    else:
        print("⚠️ Additional work needed")
    exit(0 if success else 1)