#!/usr/bin/env python3
"""
Simple MVP Job Classification Server - Alternative Launcher
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import io
import os
import re
import json
from datetime import datetime
from typing import Dict, List, Any

# Simple inline classifier (no external imports)
class SimpleJobClassifier:
    def __init__(self):
        self.job_categories = {
            'HVAC': ['hvac', 'heating', 'ventilation', 'air conditioning', 'hvac tech'],
            'Security': ['security guard', 'security', 'guard', 'safety officer'],
            'Nurse': ['nurse', 'rn', 'lvn', 'lpn', 'nursing', 'registered nurse'],
            'Veterinary Assistant': ['veterinary assistant', 'vet tech', 'veterinary'],
            'Dental Assistant': ['dental assistant', 'dental hygienist', 'dental'],
            'CDL': ['cdl driver', 'truck driver', 'commercial driver', 'cdl'],
            'Speech Pathology': ['speech pathology', 'speech therapist', 'slp'],
            'Aviation Mechanic': ['aviation mechanic', 'aircraft mechanic'],
            'Plumber': ['plumber', 'plumbing', 'pipefitter'],
            'Electrician': ['electrician', 'electrical', 'lineman'],
            'Welder': ['welder', 'welding', 'fabrication', 'steel worker'],
            'Construction': ['construction', 'construction worker', 'craftsman'],
            'Technician': ['technician', 'tech', 'fitter', 'machine operator']
        }
        
    def extract_job_title(self, text: str) -> str:
        if not text or pd.isna(text):
            return "No text provided"
            
        text = str(text).strip()
        first_sentence = re.split(r'[.!?]', text)[0]
        
        patterns = [
            r'(\d+)?\s*(?:jobs?\s+(?:for\s+|available\s+for\s+)?)?([A-Za-z\s]+?)\s+(?:jobs?|positions?|openings?)',
            r'([A-Za-z\s]+?)\s+(?:positions?|jobs?|openings?)\s+(?:available|needed|wanted)',
            r'(?:hiring|seeking|looking\s+for)\s+([A-Za-z\s]+?)(?:\s+in\s+|\s+for\s+|\s*-|\s*$)',
            r'^([A-Za-z]+(?:\s+[A-Za-z]+){1,3})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, first_sentence, re.IGNORECASE)
            if match:
                title_group = 2 if len(match.groups()) > 1 and match.group(2) else 1
                title = match.group(title_group).strip()
                
                # Clean title
                noise_words = ['jobs', 'job', 'positions', 'available', 'needed', 'hiring']
                words = [word for word in title.split() if word.lower() not in noise_words]
                cleaned = ' '.join(words).strip()
                
                if cleaned and len(cleaned) > 2:
                    return cleaned
        
        words = first_sentence.split()[:3]
        cleaned_words = [word for word in words if word.isalpha() and len(word) > 1]
        return ' '.join(cleaned_words[:2]) if cleaned_words else "Unable to extract"

    def classify_job_category(self, job_title: str, full_text: str = "") -> str:
        search_text = (job_title + " " + full_text).lower()
        
        category_scores = {}
        for category, keywords in self.job_categories.items():
            score = sum(len(keyword.split()) for keyword in keywords if keyword in search_text)
            if score > 0:
                category_scores[category] = score
        
        return max(category_scores, key=category_scores.get) if category_scores else 'Other'

    def process_row(self, text: str) -> Dict[str, Any]:
        try:
            job_title = self.extract_job_title(text)
            return {
                'extracted_job_title': job_title,
                'job_category': self.classify_job_category(job_title, text),
                'experience_level': 'Not Specified',
                'license_required': 'Not Specified',
                'job_function': 'General',
                'confidence': 0.8,
                'processing_status': 'success'
            }
        except Exception as e:
            return {
                'extracted_job_title': 'Error',
                'job_category': 'Error',
                'experience_level': 'Error',
                'license_required': 'Error', 
                'job_function': 'Error',
                'confidence': 0.0,
                'processing_status': 'error',
                'error_message': str(e)
            }

# Create FastAPI app
app = FastAPI(title="MVP Job Classification System", version="1.0.0")
classifier = SimpleJobClassifier()
processed_data = {}

# HTML template embedded in code
HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>🎯 Job Classification MVP</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #333; margin-bottom: 10px; }
        .section { margin: 30px 0; padding: 20px; border: 2px solid #ddd; border-radius: 8px; }
        .file-upload { text-align: center; padding: 40px; border: 3px dashed #ddd; border-radius: 8px; }
        .btn { padding: 10px 20px; margin: 10px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; }
        .btn-primary { background: #007bff; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn:hover { opacity: 0.8; }
        .results-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .results-table th, .results-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .results-table th { background: #f8f9fa; }
        .hidden { display: none; }
        .alert { padding: 15px; margin: 15px 0; border-radius: 4px; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Job Classification MVP</h1>
            <p>Extract and classify job titles from CSV data</p>
        </div>

        <div class="section">
            <h3>📁 Upload CSV File</h3>
            <div class="file-upload">
                <input type="file" id="csv-file" accept=".csv" onchange="analyzeFile()">
                <p>Select a CSV file containing job posting text</p>
            </div>
            
            <div id="column-selection" class="hidden">
                <h4>Select text column:</h4>
                <select id="text-column">
                    <option value="">Choose a column...</option>
                </select>
            </div>
        </div>

        <div class="section">
            <h3>⚙️ Processing</h3>
            <button onclick="testSample()" class="btn btn-secondary" id="test-btn">🧪 Test Sample</button>
            <button onclick="processAll()" class="btn btn-primary" id="process-btn">🚀 Process All</button>
        </div>

        <div id="results" class="section hidden">
            <h3>📊 Results</h3>
            <div id="alert-container"></div>
            <div id="results-content"></div>
            <button onclick="downloadResults()" class="btn btn-primary hidden" id="download-btn">💾 Download CSV</button>
        </div>
    </div>

    <script>
        let currentSessionId = null;

        function showAlert(message, type) {
            const container = document.getElementById('alert-container');
            container.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
        }

        async function analyzeFile() {
            const fileInput = document.getElementById('csv-file');
            const file = fileInput.files[0];
            if (!file) {
                showAlert('Please select a file first', 'error');
                return;
            }

            showAlert('Uploading and analyzing file...', 'success');
            
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/analyze-csv', { 
                    method: 'POST', 
                    body: formData 
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                
                if (result.success) {
                    currentSessionId = result.session_id;
                    const columnSelect = document.getElementById('text-column');
                    columnSelect.innerHTML = '<option value="">Choose a column...</option>';
                    result.columns.forEach(col => {
                        columnSelect.innerHTML += `<option value="${col}">${col}</option>`;
                    });
                    document.getElementById('column-selection').classList.remove('hidden');
                    showAlert(`✅ File analyzed successfully! ${result.total_rows} rows found`, 'success');
                } else {
                    showAlert(`❌ Error: ${result.error || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showAlert(`❌ Upload failed: ${error.message}`, 'error');
                console.error('Upload error:', error);
            }
        }

        async function testSample() {
            await processData('/test-sample', 10);
        }

        async function processAll() {
            await processData('/process-full', -1);
        }

        async function processData(endpoint, testRows) {
            const textColumn = document.getElementById('text-column').value;
            if (!textColumn) {
                showAlert('❌ Please select a text column first', 'error');
                return;
            }
            if (!currentSessionId) {
                showAlert('❌ Please upload a CSV file first', 'error');
                return;
            }

            const formData = new FormData();
            formData.append('session_id', currentSessionId);
            formData.append('text_column', textColumn);
            if (testRows > 0) formData.append('test_rows', testRows);

            try {
                showAlert('🔄 Processing data...', 'success');
                
                const response = await fetch(endpoint, { 
                    method: 'POST', 
                    body: formData 
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                
                if (result.success) {
                    displayResults(result);
                    document.getElementById('results').classList.remove('hidden');
                    
                    const actionType = endpoint === '/test-sample' ? 'Test' : 'Processing';
                    showAlert(`✅ ${actionType} completed successfully!`, 'success');
                    
                    if (endpoint === '/process-full') {
                        document.getElementById('download-btn').classList.remove('hidden');
                    }
                } else {
                    showAlert(`❌ Processing failed: ${result.error || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showAlert(`❌ Processing failed: ${error.message}`, 'error');
                console.error('Processing error:', error);
            }
        }

        function displayResults(result) {
            const container = document.getElementById('results-content');
            const data = result.test_results || result.sample_results;
            
            if (!data || data.length === 0) {
                container.innerHTML = '<p>No results to display</p>';
                return;
            }

            let html = '<table class="results-table"><thead><tr>';
            html += '<th>Job Title</th><th>Category</th><th>Experience</th><th>License</th><th>Function</th></tr></thead><tbody>';
            
            data.forEach(row => {
                html += '<tr>';
                html += `<td>${row.extracted_job_title || 'N/A'}</td>`;
                html += `<td>${row.job_category || 'N/A'}</td>`;
                html += `<td>${row.experience_level || 'N/A'}</td>`;
                html += `<td>${row.license_required || 'N/A'}</td>`;
                html += `<td>${row.job_function || 'N/A'}</td>`;
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            container.innerHTML = html;

            if (result.summary) {
                const summary = result.summary;
                html += `<p><strong>Summary:</strong> Processed ${summary.total_tested || summary.total_rows_processed} rows, `;
                html += `${summary.successful_extractions} successful extractions</p>`;
                container.innerHTML += html;
            }
        }

        async function downloadResults() {
            if (!currentSessionId) return;
            
            try {
                const response = await fetch(`/download/${currentSessionId}`);
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `classified_jobs_${currentSessionId}.csv`;
                    a.click();
                    URL.revokeObjectURL(url);
                    showAlert('Download started!', 'success');
                }
            } catch (error) {
                showAlert(`Download error: ${error.message}`, 'error');
            }
        }
    </script>
</body>
</html>'''

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTMLResponse(content=HTML_TEMPLATE)

@app.post("/analyze-csv")
async def analyze_csv_file(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Please upload a CSV file")
        
        contents = await file.read()
        # Fix pandas reading issues
        df = pd.read_csv(
            io.StringIO(contents.decode('utf-8')), 
            dtype=str,  # Read everything as strings to avoid type issues
            na_filter=False  # Don't convert to NaN
        )
        
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        columns = list(df.columns)
        
        # Clean sample data for JSON serialization
        sample_data = df.head(3).fillna("").to_dict('records')
        
        # Clean the sample data to ensure JSON serialization
        cleaned_sample = []
        for row in sample_data:
            cleaned_row = {}
            for key, value in row.items():
                # Convert any problematic values to strings
                if pd.isna(value) or value is None:
                    cleaned_row[key] = ""
                elif isinstance(value, (int, float)):
                    if pd.isna(value) or not pd.isfinite(value):
                        cleaned_row[key] = ""
                    else:
                        cleaned_row[key] = str(value)
                else:
                    cleaned_row[key] = str(value)[:100]  # Truncate long strings
            cleaned_sample.append(cleaned_row)
        
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        processed_data[session_id] = {
            'original_df': df,
            'filename': file.filename
        }
        
        return {
            "success": True,
            "columns": columns,
            "sample_data": cleaned_sample,
            "total_rows": len(df),
            "session_id": session_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error analyzing CSV: {str(e)}"
        }

@app.post("/test-sample")
async def test_sample_processing(
    session_id: str = Form(...),
    text_column: str = Form(...),
    test_rows: int = Form(10)
):
    try:
        if session_id not in processed_data:
            raise HTTPException(status_code=400, detail="Session not found")
        
        df = processed_data[session_id]['original_df'].copy()
        if text_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{text_column}' not found")
        
        test_df = df.head(test_rows)
        results = []
        
        for idx, row in test_df.iterrows():
            text = str(row[text_column])
            result = classifier.process_row(text)
            results.append(result)
        
        successful_results = [r for r in results if r['processing_status'] == 'success']
        
        summary = {
            'total_tested': len(results),
            'successful_extractions': len(successful_results)
        }
        
        return {
            "success": True,
            "test_results": results,
            "summary": summary
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error testing sample: {str(e)}"
        }

@app.post("/process-full")
async def process_full_dataset(
    session_id: str = Form(...),
    text_column: str = Form(...)
):
    try:
        if session_id not in processed_data:
            raise HTTPException(status_code=400, detail="Session not found")
        
        df = processed_data[session_id]['original_df'].copy()
        if text_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{text_column}' not found")
        
        # Process each row
        results = []
        for idx, row in df.iterrows():
            text = str(row[text_column])
            result = classifier.process_row(text)
            results.append(result)
        
        # Add results to dataframe
        results_df = pd.DataFrame(results)
        for col in ['extracted_job_title', 'job_category', 'experience_level', 'license_required', 'job_function']:
            df[col] = results_df[col]
        
        processed_data[session_id]['processed_df'] = df
        
        summary = {
            'total_rows_processed': len(df),
            'successful_extractions': len([r for r in results if r['processing_status'] == 'success'])
        }
        
        sample_results = df.head(5)[
            ['extracted_job_title', 'job_category', 'experience_level', 'license_required', 'job_function']
        ].to_dict('records')
        
        return {
            "success": True,
            "summary": summary,
            "sample_results": sample_results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing dataset: {str(e)}"
        }

@app.get("/download/{session_id}")
async def download_results(session_id: str):
    try:
        if session_id not in processed_data or 'processed_df' not in processed_data[session_id]:
            raise HTTPException(status_code=400, detail="No processed data found")
        
        processed_df = processed_data[session_id]['processed_df']
        original_filename = processed_data[session_id]['filename']
        
        base_name = original_filename.replace('.csv', '')
        output_filename = f"{base_name}_classified_{session_id}.csv"
        temp_file_path = f"/tmp/{output_filename}"
        
        processed_df.to_csv(temp_file_path, index=False)
        
        return FileResponse(
            temp_file_path,
            media_type='text/csv',
            filename=output_filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🎯 Starting Simple MVP Job Classification System")
    print("   Access at: http://localhost:8000")
    print("   Press Ctrl+C to stop")
    uvicorn.run(app, host="0.0.0.0", port=8000)