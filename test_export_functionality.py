#!/usr/bin/env python3

import requests
import pandas as pd
import os
import time
from datetime import datetime

def test_export_functionality():
    """Test the new export functionality with both complete and processed-only downloads"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Export Functionality")
    print("=" * 70)
    
    # Create test data
    test_data = {
        'job_id': ['test001', 'test002', 'test003'],
        'job_posting_text': [
            '76 CHANDLER, AZ AIRCRAFT PARTS jobs from companies (hiring now) with openings.',
            '345 Aircraft Detailing jobs available in Chandler, AZ on Indeed.com. Apply to Aircraft Maintenance Technician, Entry Level Technician, Inspector and more!',
            '116 Aircraft jobs available in Decatur, AL on Indeed.com. Apply to Aerospace Technician, Baggage Handler, General Consideration - Talent Network and more!'
        ]
    }
    
    test_df = pd.DataFrame(test_data)
    test_csv_path = 'test_export_data.csv'
    test_df.to_csv(test_csv_path, index=False)
    
    print(f"Created test CSV: {test_csv_path}")
    print(f"Test data rows: {len(test_df)}")
    
    try:
        # Step 1: Upload CSV
        print("\\n📤 Step 1: Uploading CSV file...")
        with open(test_csv_path, 'rb') as f:
            files = {'file': (test_csv_path, f, 'text/csv')}
            response = requests.post(f"{base_url}/analyze-csv", files=files)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.text}")
            return False
        
        upload_result = response.json()
        if not upload_result.get('success'):
            print(f"❌ Upload failed: {upload_result.get('error')}")
            return False
        
        session_id = upload_result['session_id']
        print(f"✅ Upload successful! Session ID: {session_id}")
        
        # Step 2: Process the data
        print("\\n⚙️ Step 2: Processing data...")
        process_data = {
            'session_id': session_id,
            'text_column': 'job_posting_text',
            'job_id_column': 'job_id',
            'start_row': 1,
            'end_row': 3,
            'is_test': False
        }
        
        response = requests.post(f"{base_url}/process-range", data=process_data)
        
        if response.status_code != 200:
            print(f"❌ Processing failed: {response.text}")
            return False
        
        process_result = response.json()
        if not process_result.get('success'):
            print(f"❌ Processing failed: {process_result.get('error')}")
            return False
        
        print(f"✅ Processing successful! Processed {process_result['summary']['total_processed']} rows")
        print(f"Average Confidence: {process_result['summary']['average_confidence']:.2f}")
        
        # Step 3: Test Complete CSV Export
        print("\\n📥 Step 3: Testing Complete CSV Export...")
        response = requests.get(f"{base_url}/download/{session_id}")
        
        if response.status_code != 200:
            print(f"❌ Complete CSV download failed: {response.text}")
            return False
        
        complete_csv_path = f"complete_export_{session_id}.csv"
        with open(complete_csv_path, 'wb') as f:
            f.write(response.content)
        
        # Analyze complete CSV
        complete_df = pd.read_csv(complete_csv_path)
        print(f"✅ Complete CSV downloaded: {complete_csv_path}")
        print(f"   Rows: {len(complete_df)}")
        print(f"   Columns: {len(complete_df.columns)}")
        print(f"   Column names: {', '.join(complete_df.columns[:5])}{'...' if len(complete_df.columns) > 5 else ''}")
        
        # Step 4: Test Processed-Only Export  
        print("\\n🎯 Step 4: Testing Processed-Only Export...")
        response = requests.get(f"{base_url}/download-processed-only/{session_id}")
        
        if response.status_code != 200:
            print(f"❌ Processed-only download failed: {response.text}")
            return False
        
        processed_csv_path = f"processed_only_{session_id}.csv"
        with open(processed_csv_path, 'wb') as f:
            f.write(response.content)
        
        # Analyze processed-only CSV
        processed_df = pd.read_csv(processed_csv_path)
        print(f"✅ Processed-only CSV downloaded: {processed_csv_path}")
        print(f"   Rows: {len(processed_df)}")
        print(f"   Columns: {len(processed_df.columns)}")
        print(f"   Column names: {', '.join(processed_df.columns)}")
        
        # Step 5: Validate Results
        print("\\n✅ Step 5: Validating Results...")
        
        # Check that complete CSV has both original and processed columns
        original_columns = set(test_df.columns)
        processed_columns = {'extracted_job_title', 'job_category', 'general_category', 'confidence', 'job_details', 'row_id', 'original_content'}
        
        complete_has_original = original_columns.issubset(set(complete_df.columns))
        complete_has_processed = processed_columns.issubset(set(complete_df.columns))
        
        expected_processed_columns = processed_columns.union({'job_id'})
        actual_processed_columns = set(processed_df.columns)
        processed_only_correct = expected_processed_columns == actual_processed_columns
        
        if not processed_only_correct:
            print(f"   Expected: {sorted(expected_processed_columns)}")
            print(f"   Actual: {sorted(actual_processed_columns)}")
            print(f"   Missing: {expected_processed_columns - actual_processed_columns}")
            print(f"   Extra: {actual_processed_columns - expected_processed_columns}")
        
        print(f"Complete CSV has original columns: {'✅' if complete_has_original else '❌'}")
        print(f"Complete CSV has processed columns: {'✅' if complete_has_processed else '❌'}")
        print(f"Processed-only CSV has correct columns: {'✅' if processed_only_correct else '❌'}")
        
        # Display sample results
        print("\\n📊 Sample Results:")
        print("Complete CSV (first 2 rows):")
        print(complete_df[['job_id', 'extracted_job_title', 'job_category', 'general_category']].head(2).to_string(index=False))
        
        print("\\nProcessed-only CSV (first 2 rows):")
        print(processed_df[['job_id', 'extracted_job_title', 'job_category', 'general_category']].head(2).to_string(index=False))
        
        # Cleanup
        for file_path in [test_csv_path, complete_csv_path, processed_csv_path]:
            try:
                os.remove(file_path)
                print(f"🗑️ Cleaned up: {file_path}")
            except:
                pass
        
        success = complete_has_original and complete_has_processed and processed_only_correct
        
        if success:
            print("\\n🎉 Export Functionality Test: PASSED")
            print("✅ Both export options working correctly!")
            print("✅ Complete CSV includes all original + processed columns")
            print("✅ Processed-only CSV contains only processed columns")
        else:
            print("\\n❌ Export Functionality Test: FAILED")
        
        return success
        
    except Exception as e:
        print(f"\\n❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_export_functionality()
    exit(0 if success else 1)