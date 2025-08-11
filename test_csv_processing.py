#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from core.enhanced_classifier import EnhancedJobClassifier

def test_csv_processing():
    """Test the enhanced classifier with the improved test CSV file"""
    
    classifier = EnhancedJobClassifier(use_ai=False)
    
    # Read the test CSV
    df = pd.read_csv('test_improved_cases.csv')
    
    print("🎯 Testing Enhanced Classifier with CSV Data")
    print("=" * 80)
    print(f"Loaded {len(df)} rows from test_improved_cases.csv")
    print()
    
    # Process the dataframe
    results_df = classifier.process_dataframe(df, 'job_posting_text', 'job_id')
    
    print("📊 PROCESSING RESULTS:")
    print("=" * 80)
    
    for idx, row in results_df.iterrows():
        print(f"Row {idx + 1} (Job ID: {row['job_id']}):")
        print(f"  Original: {row['job_posting_text'][:80]}...")
        print(f"  Job Title: {row['extracted_job_title']}")
        print(f"  Category: {row['job_category']}")
        print(f"  General Category: {row['general_category']}")
        print(f"  Confidence: {row['confidence']:.2f}")
        print("-" * 60)
    
    # Generate summary
    summary = classifier.get_processing_summary(results_df)
    
    print("\n📈 PROCESSING SUMMARY:")
    print("=" * 80)
    for key, value in summary.items():
        if key == 'category_distribution':
            print(f"Category Distribution:")
            for category, count in value.items():
                print(f"  {category}: {count}")
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    # Save results
    output_file = 'test_results_final.csv'
    results_df.to_csv(output_file, index=False)
    print(f"\n💾 Results saved to: {output_file}")
    
    return results_df, summary

if __name__ == "__main__":
    test_csv_processing()