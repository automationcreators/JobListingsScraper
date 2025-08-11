#!/usr/bin/env python3
"""
Enhanced MVP Job Classification Server
Uses AI-enhanced extraction with improved accuracy and reference tracking
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import io
import os
import re
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from core.enhanced_classifier import EnhancedJobClassifier
    USE_ENHANCED = True
except ImportError:
    # Fallback to inline simple classifier if import fails
    USE_ENHANCED = False

# Inline enhanced classifier (simplified version)
class InlineEnhancedClassifier:
    def __init__(self):
        self.job_categories = {
            'Aviation Mechanic': ['aircraft', 'aviation', 'airplane', 'aircraft maintenance', 'a&p mechanic'],
            'HVAC Technician': ['hvac', 'heating', 'ventilation', 'air conditioning'],
            'Security Guard': ['security guard', 'security officer', 'security'],
            'Construction Worker': ['construction', 'construction worker', 'laborer'],
            'Technician': ['technician', 'tech', 'repair technician', 'service technician'],
            'Welder': ['welder', 'welding', 'fabrication', 'steel worker'],
            'Plumber': ['plumber', 'plumbing', 'pipefitter'],
            'Electrician': ['electrician', 'electrical'],
            'Driver': ['driver', 'cdl', 'truck driver'],
            'Nurse': ['nurse', 'rn', 'lpn', 'lvn'],
            'Project Manager': ['project manager', 'construction manager'],
        }
        
        self.noise_patterns = [
            r'\b\d+\s*(jobs?|positions?|openings?)\b',
            r'\bavailable\s+in\b',
            r'\bon\s+indeed\.com\b',
            r'\bapply\s+to\b',
            r'\band\s+more\b',
            r'\bsatisfaction\s+guaranteed\b',
            r'\b(hiring|seeking|looking)\b'
        ]

    def extract_job_title(self, text: str) -> str:
        if not text or pd.isna(text):
            return "Unable to extract job title"
            
        text = str(text).strip()
        
        # Remove noise patterns
        cleaned_text = text
        for pattern in self.noise_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        # Enhanced patterns for job title extraction
        patterns = [
            r'([A-Za-z\s]+?(?:technician|mechanic|specialist|assistant|manager|coordinator|worker|driver|nurse|electrician|plumber|welder|guard|officer))\s+(?:jobs?|positions?)',
            r'([A-Za-z\s]+?(?:technician|mechanic|specialist|assistant|manager|coordinator|worker|driver|nurse|electrician|plumber|welder|guard|officer))\s+(?:needed|wanted)',
            r'(?:hiring|seeking)\s+([A-Za-z\s]+?(?:technician|mechanic|specialist|assistant|manager|coordinator|worker|driver|nurse|electrician|plumber|welder|guard|officer))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                cleaned_title = self._clean_job_title(title)
                if self._validate_job_title(cleaned_title):
                    return cleaned_title
        
        # Fallback: look for known job categories in text
        text_lower = text.lower()
        for category, keywords in self.job_categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return keyword.title()
        
        return "Unable to extract job title"

    def _clean_job_title(self, title: str) -> str:
        if not title:
            return ""
        
        noise_words = ['jobs', 'job', 'positions', 'position', 'available', 'needed', 'wanted', 'hiring']
        words = [word for word in title.strip().split() if word.lower() not in noise_words and len(word) > 1]
        result = ' '.join(words).strip()
        return ' '.join(word.capitalize() for word in result.split())

    def _validate_job_title(self, title: str) -> bool:
        if not title or len(title) < 3:
            return False
        
        title_lower = title.lower()
        
        # Invalid patterns
        invalid_patterns = [
            r'^\d+$', r'^[A-Z\s]+$', r'\b(and|the|of|in|at|to|for|with|by)\b',
            r'\b(city|town|county|state|area|location)\b', r'\b(company|corp|inc|llc)\b',
            r'\b(guaranteed|satisfaction|quality|service|stone)\b'
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, title_lower):
                return False
        
        # Must contain job-related words
        job_keywords = [
            'technician', 'tech', 'mechanic', 'specialist', 'assistant', 'manager',
            'coordinator', 'supervisor', 'worker', 'driver', 'nurse', 'electrician',
            'plumber', 'welder', 'guard', 'officer'
        ]
        
        return any(keyword in title_lower for keyword in job_keywords)

    def classify_job_category(self, job_title: str, full_text: str = "") -> str:
        if not job_title or job_title == "Unable to extract job title":
            return 'Unable to Classify'
            
        search_text = (job_title + " " + full_text).lower()
        
        best_match = None
        best_score = 0
        
        for category, keywords in self.job_categories.items():
            score = sum(len(keyword.split()) * 2 for keyword in keywords if keyword in search_text)
            if score > best_score:
                best_score = score
                best_match = category
        
        return best_match if best_match else 'Other'

    def process_row(self, text: str, row_id: str = None, job_id: str = None) -> Dict[str, Any]:
        try:
            if not text or pd.isna(text):
                return self._error_result("Empty or invalid text", text, row_id, job_id)
            
            text = str(text).strip()
            if len(text) < 10:
                return self._error_result("Text too short", text, row_id, job_id)
            
            job_title = self.extract_job_title(text)
            category = self.classify_job_category(job_title, text)
            
            # Simple confidence calculation
            confidence = 0.8 if job_title != "Unable to extract job title" and category != 'Other' else 0.3
            
            result = {
                'extracted_job_title': job_title,
                'job_category': category,
                'confidence': confidence,
                'original_content': text,
                'processing_status': 'success'
            }
            
            if row_id is not None:
                result['row_id'] = row_id
            if job_id is not None:
                result['job_id'] = job_id
                
            return result
            
        except Exception as e:
            return self._error_result(f"Processing error: {str(e)}", text, row_id, job_id)

    def _error_result(self, error_msg: str, original_text: str = "", row_id: str = None, job_id: str = None):
        result = {
            'extracted_job_title': 'Error',
            'job_category': 'Error',
            'confidence': 0.0,
            'original_content': original_text,
            'processing_status': 'error',
            'error_message': error_msg
        }
        if row_id is not None:
            result['row_id'] = row_id
        if job_id is not None:
            result['job_id'] = job_id
        return result

# Create FastAPI app
app = FastAPI(title="Enhanced Job Classification System", version="2.0.0")

# Initialize classifier
if USE_ENHANCED:
    classifier = EnhancedJobClassifier(use_ai=False)  # Set to True when AI is configured
else:
    classifier = InlineEnhancedClassifier()

processed_data = {}

# Enhanced HTML template
HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>🎯 Enhanced Job Classification System</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f8f9fa; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin: -30px -30px 30px -30px; }
        .header h1 { margin: 0 0 10px 0; font-size: 2.2rem; }
        .section { margin: 30px 0; padding: 25px; border: 2px solid #e9ecef; border-radius: 8px; background: #fdfdfd; }
        .section h3 { color: #495057; margin-bottom: 20px; font-size: 1.3rem; }
        .file-upload { text-align: center; padding: 40px; border: 3px dashed #dee2e6; border-radius: 8px; transition: all 0.3s; }
        .file-upload:hover { border-color: #667eea; background: #f8f9ff; }
        .file-upload input[type="file"] { display: none; }
        .btn { padding: 12px 24px; margin: 10px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.2s; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .results-table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.9rem; }
        .results-table th, .results-table td { border: 1px solid #dee2e6; padding: 12px 8px; text-align: left; }
        .results-table th { background: #f8f9fa; font-weight: 600; color: #495057; }
        .results-table tr:nth-child(even) { background: #f8f9fa; }
        .original-content { max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .confidence-high { color: #28a745; font-weight: bold; }
        .confidence-medium { color: #ffc107; font-weight: bold; }
        .confidence-low { color: #dc3545; font-weight: bold; }
        .hidden { display: none; }
        .alert { padding: 15px; margin: 15px 0; border-radius: 6px; font-weight: 500; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-card { background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; border: 1px solid #dee2e6; }
        .stat-number { font-size: 1.5rem; font-weight: bold; color: #667eea; }
        .stat-label { color: #6c757d; font-size: 0.9rem; margin-top: 5px; }
        select { width: 100%; padding: 12px; border: 2px solid #dee2e6; border-radius: 6px; font-size: 1rem; }
        .improvement-notice { background: #e3f2fd; border: 1px solid #bbdefb; padding: 15px; border-radius: 6px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Enhanced Job Classification System</h1>
            <p>AI-powered job title extraction with improved accuracy and reference tracking</p>
        </div>

        <div class="section">
            <h3>📁 Upload CSV File</h3>
            <div class="improvement-notice">
                <strong>✨ New Features:</strong> Better job title extraction, specific categories (e.g., Aviation Mechanic), original content tracking, and unique identifiers for feedback.
            </div>
            <div class="file-upload" onclick="document.getElementById('csv-file').click()">
                <input type="file" id="csv-file" accept=".csv" onchange="analyzeFile()">
                <div class="btn btn-primary">📂 Choose CSV File</div>
                <p style="margin-top: 15px; color: #6c757d;">Select a CSV file containing job posting text</p>
            </div>
            
            <div id="column-selection" class="hidden">
                <h4>Select the column containing job posting text:</h4>
                <select id="text-column">
                    <option value="">Choose a column...</option>
                </select>
                <div style="margin-top: 10px;">
                    <label><strong>Job ID Column (optional):</strong></label>
                    <select id="job-id-column">
                        <option value="">No job ID column</option>
                    </select>
                </div>
            </div>
        </div>

        <div class="section">
            <h3>⚙️ Processing Options</h3>
            <button onclick="testSample()" class="btn btn-secondary" id="test-btn">🧪 Test Sample (10 rows)</button>
            <button onclick="processAll()" class="btn btn-primary" id="process-btn">🚀 Process All Rows</button>
        </div>

        <div id="results" class="section hidden">
            <h3>📊 Enhanced Results</h3>
            <div id="alert-container"></div>
            <div id="stats-container"></div>
            <div id="results-content"></div>
            <button onclick="downloadResults()" class="btn btn-success hidden" id="download-btn">💾 Download Enhanced CSV</button>
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

            showAlert('📤 Uploading and analyzing file...', 'success');
            
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
                    
                    // Populate column selectors
                    const textColumnSelect = document.getElementById('text-column');
                    const jobIdColumnSelect = document.getElementById('job-id-column');
                    
                    textColumnSelect.innerHTML = '<option value="">Choose a column...</option>';
                    jobIdColumnSelect.innerHTML = '<option value="">No job ID column</option>';
                    
                    result.columns.forEach(col => {
                        textColumnSelect.innerHTML += `<option value="${col}">${col}</option>`;
                        jobIdColumnSelect.innerHTML += `<option value="${col}">${col}</option>`;
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
            const jobIdColumn = document.getElementById('job-id-column').value;
            
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
            if (jobIdColumn) formData.append('job_id_column', jobIdColumn);
            if (testRows > 0) formData.append('test_rows', testRows);

            try {
                showAlert('🔄 Processing data with enhanced extraction...', 'success');
                
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
                    
                    const actionType = endpoint === '/test-sample' ? 'Sample test' : 'Full processing';
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
            displayStats(result.summary);
            
            const container = document.getElementById('results-content');
            const data = result.test_results || result.sample_results;
            
            if (!data || data.length === 0) {
                container.innerHTML = '<p>No results to display</p>';
                return;
            }

            let html = '<h4>Enhanced Classification Results:</h4><table class="results-table"><thead><tr>';
            html += '<th>Row ID</th><th>Job Title</th><th>Category</th><th>General</th><th>Confidence</th><th>Original Content</th>';
            if (data[0].job_id !== undefined) html += '<th>Job ID</th>';
            html += '</tr></thead><tbody>';
            
            data.forEach((row, index) => {
                const confidenceClass = row.confidence > 0.7 ? 'confidence-high' : 
                                      row.confidence > 0.4 ? 'confidence-medium' : 'confidence-low';
                
                html += '<tr>';
                html += `<td>${row.row_id || index}</td>`;
                html += `<td><strong>${row.extracted_job_title || 'N/A'}</strong></td>`;
                html += `<td>${row.job_category || 'N/A'}</td>`;
                html += `<td><span style="background: ${row.general_category === 'exact' ? '#28a745' : row.general_category === 'general' ? '#ffc107' : '#6c757d'}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">${row.general_category || 'other'}</span></td>`;
                html += `<td class="${confidenceClass}">${((row.confidence || 0) * 100).toFixed(1)}%</td>`;
                html += `<td class="original-content" title="${row.original_content || ''}">${(row.original_content || '').substring(0, 80)}${(row.original_content || '').length > 80 ? '...' : ''}</td>`;
                if (row.job_id !== undefined) html += `<td>${row.job_id || 'N/A'}</td>`;
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            container.innerHTML = html;
        }

        function displayStats(summary) {
            if (!summary) return;
            
            const container = document.getElementById('stats-container');
            html = '<div class="stats">';
            html += `<div class="stat-card"><div class="stat-number">${summary.total_tested || summary.total_rows_processed || 0}</div><div class="stat-label">Total Processed</div></div>`;
            html += `<div class="stat-card"><div class="stat-number">${summary.successful_extractions || 0}</div><div class="stat-label">Successful</div></div>`;
            html += `<div class="stat-card"><div class="stat-number">${((summary.average_confidence || 0) * 100).toFixed(1)}%</div><div class="stat-label">Avg Confidence</div></div>`;
            html += `<div class="stat-card"><div class="stat-number">${summary.unable_to_extract_count || 0}</div><div class="stat-label">Unable to Extract</div></div>`;
            html += '</div>';
            container.innerHTML = html;
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
                    a.download = `enhanced_job_classification_${currentSessionId}.csv`;
                    a.click();
                    URL.revokeObjectURL(url);
                    showAlert('✅ Enhanced CSV downloaded successfully!', 'success');
                }
            } catch (error) {
                showAlert(`❌ Download error: ${error.message}`, 'error');
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
        # Read CSV with improved handling
        df = pd.read_csv(
            io.StringIO(contents.decode('utf-8')), 
            dtype=str,
            na_filter=False
        )
        
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        columns = list(df.columns)
        
        # Clean sample data for JSON serialization
        sample_data = df.head(3).fillna("").to_dict('records')
        cleaned_sample = []
        
        for row in sample_data:
            cleaned_row = {}
            for key, value in row.items():
                if pd.isna(value) or value is None:
                    cleaned_row[key] = ""
                else:
                    cleaned_row[key] = str(value)[:100]
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
    job_id_column: str = Form(None),
    test_rows: int = Form(10)
):
    try:
        if session_id not in processed_data:
            raise HTTPException(status_code=400, detail="Session not found")
        
        df = processed_data[session_id]['original_df'].copy()
        if text_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{text_column}' not found")
        
        # Process sample rows
        test_df = df.head(test_rows)
        results = []
        
        for idx, row in test_df.iterrows():
            text = str(row[text_column])
            row_id = str(idx)
            job_id = str(row[job_id_column]) if job_id_column and job_id_column in df.columns else None
            
            result = classifier.process_row(text, row_id, job_id)
            results.append(result)
        
        successful_results = [r for r in results if r['processing_status'] == 'success']
        unable_to_extract = len([r for r in results if r['extracted_job_title'] == 'Unable to extract job title'])
        
        summary = {
            'total_tested': len(results),
            'successful_extractions': len(successful_results),
            'unable_to_extract_count': unable_to_extract,
            'average_confidence': sum(r['confidence'] for r in successful_results) / len(successful_results) if successful_results else 0
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
    text_column: str = Form(...),
    job_id_column: str = Form(None)
):
    try:
        if session_id not in processed_data:
            raise HTTPException(status_code=400, detail="Session not found")
        
        df = processed_data[session_id]['original_df'].copy()
        if text_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{text_column}' not found")
        
        # Process all rows
        results = []
        for idx, row in df.iterrows():
            text = str(row[text_column])
            row_id = str(idx)
            job_id = str(row[job_id_column]) if job_id_column and job_id_column in df.columns else None
            
            result = classifier.process_row(text, row_id, job_id)
            results.append(result)
        
        # Add results to dataframe
        results_df = pd.DataFrame(results)
        
        # Add new columns to original DataFrame
        output_columns = ['extracted_job_title', 'job_category', 'general_category', 'confidence', 'original_content', 'row_id']
        if job_id_column:
            output_columns.append('job_id')
            
        for col in output_columns:
            if col in results_df.columns:
                df[col] = results_df[col]
        
        processed_data[session_id]['processed_df'] = df
        
        # Generate enhanced summary
        successful_results = [r for r in results if r['processing_status'] == 'success']
        unable_to_extract = len([r for r in results if r['extracted_job_title'] == 'Unable to extract job title'])
        
        summary = {
            'total_rows_processed': len(df),
            'successful_extractions': len(successful_results),
            'unable_to_extract_count': unable_to_extract,
            'average_confidence': sum(r['confidence'] for r in successful_results) / len(successful_results) if successful_results else 0,
            'processing_accuracy': round(len(successful_results) / len(results) * 100, 1) if results else 0
        }
        
        sample_results = results[:5]  # Show first 5 results
        
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
        output_filename = f"{base_name}_enhanced_classification_{session_id}.csv"
        temp_file_path = f"/tmp/{output_filename}"
        
        processed_df.to_csv(temp_file_path, index=False)
        
        return FileResponse(
            temp_file_path,
            media_type='text/csv',
            filename=output_filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "classifier_type": "enhanced" if USE_ENHANCED else "inline",
        "features": [
            "Enhanced job title extraction",
            "Specific category classification", 
            "Original content tracking",
            "Unique identifier support",
            "Improved accuracy"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🎯 Starting Enhanced Job Classification System")
    print("   Features: Better extraction, specific categories, reference tracking")
    print("   Access at: http://localhost:8000")
    print("   Press Ctrl+C to stop")
    uvicorn.run(app, host="0.0.0.0", port=8000)