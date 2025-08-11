#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.mvp_classifier import MVPJobClassifier
import pandas as pd

def test_classifier():
    """Test the MVP classifier with sample data"""
    classifier = MVPJobClassifier()
    
    # Test cases from user data
    test_cases = [
        "446 Steel Worker jobs available in San Antonio, TX on Indeed.com. Apply to Pipefitter, Technician, Machine Operator and more!",
        "138 Residential Construction jobs available in San Antonio, TX on Indeed.com. Apply to Craftsman, Construction Project Manager, Plumbing Helper and more!",
        "16 Fitter jobs available in San Antonio, TX on Indeed.com. Apply to Fire Sprinkler Technician, Pipefitter, Remodeler and more!"
    ]
    
    print("🎯 MVP Job Classification Test Results")
    print("=" * 60)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Input: {text[:80]}...")
        print("-" * 40)
        
        result = classifier.process_row(text)
        
        print(f"Job Title: {result['extracted_job_title']}")
        print(f"Category: {result['job_category']}")
        print(f"Experience Level: {result['experience_level']}")
        print(f"License Required: {result['license_required']}")
        print(f"Job Function: {result['job_function']}")
        print(f"Confidence: {result['confidence']:.3f} ({result['confidence']*100:.1f}%)")
        print(f"Status: {result['processing_status']}")
        
        if result['processing_status'] == 'error':
            print(f"Error: {result.get('error_message', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    
    # Test CSV processing
    print("\n📊 Testing CSV Processing...")
    try:
        df = pd.read_csv('sample_test_data.csv')
        processed_df = classifier.process_dataframe(df, 'job_posting_text')
        
        print(f"Processed {len(processed_df)} rows successfully")
        
        # Show results
        print("\nProcessed Results:")
        for _, row in processed_df.iterrows():
            print(f"- {row['extracted_job_title']} → {row['job_category']} (conf: {row['confidence']:.2f})")
        
        # Generate summary
        summary = classifier.get_processing_summary(processed_df)
        print(f"\nProcessing Summary:")
        print(f"- Total rows: {summary['total_rows_processed']}")
        print(f"- Successful: {summary['successful_extractions']}")
        print(f"- Average confidence: {summary['average_confidence']:.3f}")
        print(f"- Accuracy: {summary['processing_accuracy']}%")
        
        # Save processed file
        output_file = 'sample_test_data_processed.csv'
        processed_df.to_csv(output_file, index=False)
        print(f"\n💾 Saved processed results to: {output_file}")
        
    except Exception as e:
        print(f"Error processing CSV: {e}")

if __name__ == "__main__":
    test_classifier()