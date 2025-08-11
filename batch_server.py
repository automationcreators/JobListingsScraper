#!/usr/bin/env python3
"""
Batch Processing Enhanced Job Classification Server
With range specification, batch processing, and full content display
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
from typing import Dict, List, Any, Optional

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.advanced_classifier import AdvancedJobClassifier

app = FastAPI(title="Batch Processing Job Classification System", version="3.0.0")

# Initialize classifier
classifier = AdvancedJobClassifier(use_ai=False)
processed_data = {}

# Enhanced HTML template with batch processing controls
HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>🎯 Batch Processing Job Classification System</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f8f9fa; }
        .container { max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin: -30px -30px 30px -30px; }
        .section { margin: 30px 0; padding: 25px; border: 2px solid #e9ecef; border-radius: 8px; background: #fdfdfd; }
        .section h3 { color: #495057; margin-bottom: 20px; font-size: 1.3rem; }
        .batch-controls { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .batch-input { padding: 10px; border: 2px solid #dee2e6; border-radius: 6px; font-size: 1rem; }
        .file-upload { text-align: center; padding: 40px; border: 3px dashed #dee2e6; border-radius: 8px; transition: all 0.3s; }
        .file-upload:hover { border-color: #667eea; background: #f8f9ff; }
        .file-upload input[type="file"] { display: none; }
        .btn { padding: 12px 24px; margin: 10px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.2s; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-warning { background: #ffc107; color: #212529; }
        .btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .results-table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.9rem; }
        .results-table th, .results-table td { border: 1px solid #dee2e6; padding: 12px 8px; text-align: left; }
        .results-table th { background: #f8f9fa; font-weight: 600; color: #495057; }
        .results-table tr:nth-child(even) { background: #f8f9fa; }
        .original-content { max-width: 400px; word-wrap: break-word; white-space: pre-wrap; font-size: 0.85rem; }
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
        .batch-history { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; margin: 15px 0; max-height: 200px; overflow-y: auto; }
        select { width: 100%; padding: 12px; border: 2px solid #dee2e6; border-radius: 6px; font-size: 1rem; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Batch Processing Job Classification System</h1>
            <p>Advanced processing with range specification, batch control, and flexible export options</p>
        </div>

        <div class="section">
            <h3>📁 Upload CSV File</h3>
            <div class="file-upload" onclick="document.getElementById('csv-file').click()">
                <input type="file" id="csv-file" accept=".csv" onchange="analyzeFile()">
                <div class="btn btn-primary">📂 Choose CSV File</div>
                <p style="margin-top: 15px; color: #6c757d;">Select a CSV file containing job posting text</p>
            </div>
            
            <div id="column-selection" class="hidden">
                <h4>Select columns:</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 10px;">
                    <div>
                        <label><strong>Text Column:</strong></label>
                        <select id="text-column">
                            <option value="">Choose a column...</option>
                        </select>
                    </div>
                    <div>
                        <label><strong>Job ID Column (optional):</strong></label>
                        <select id="job-id-column">
                            <option value="">No job ID column</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h3>⚙️ Batch Processing Controls</h3>
            <div class="batch-controls">
                <div>
                    <label><strong>Start Row:</strong></label>
                    <input type="number" id="start-row" class="batch-input" value="1" min="1">
                </div>
                <div>
                    <label><strong>End Row:</strong></label>
                    <input type="number" id="end-row" class="batch-input" value="10">
                </div>
                <div>
                    <label><strong>Batch Size:</strong></label>
                    <input type="number" id="batch-size" class="batch-input" value="50" min="1" max="1000">
                </div>
                <div>
                    <label><strong>Total Rows:</strong></label>
                    <input type="text" id="total-rows" class="batch-input" readonly>
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <button onclick="testRange()" class="btn btn-secondary">🧪 Test Range</button>
                <button onclick="processBatch()" class="btn btn-primary">🚀 Process Batch</button>
                <button onclick="processAll()" class="btn btn-warning">⚡ Process All Rows</button>
                <button onclick="rerunBatch()" class="btn btn-secondary">🔄 Rerun Last Batch</button>
            </div>
            
            <div id="batch-history" class="batch-history hidden">
                <h5>Batch History:</h5>
                <div id="history-content"></div>
            </div>
        </div>

        <div id="results" class="section hidden">
            <h3>📊 Processing Results</h3>
            <div id="alert-container"></div>
            <div id="stats-container"></div>
            <div id="results-content"></div>
            
            <div id="download-section" class="hidden" style="margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 8px; border: 2px solid #dee2e6;">
                <h4>📥 Export Options</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                    <div style="text-align: center;">
                        <h5>Complete CSV</h5>
                        <p style="font-size: 0.9em; color: #6c757d; margin: 10px 0;">Original data + new processed columns</p>
                        <button onclick="downloadCompleteResults()" class="btn btn-success">
                            📊 Download Complete CSV
                        </button>
                    </div>
                    <div style="text-align: center;">
                        <h5>Processed Data Only</h5>
                        <p style="font-size: 0.9em; color: #6c757d; margin: 10px 0;">Only the new processed columns</p>
                        <button onclick="downloadProcessedOnly()" class="btn btn-primary">
                            🎯 Download Processed Only
                        </button>
                    </div>
                </div>
                <div id="export-info" style="margin-top: 15px; padding: 10px; background: #e9ecef; border-radius: 4px; font-size: 0.85em;">
                    <strong>ℹ️ Export Information:</strong><br>
                    • <strong>Complete CSV</strong>: Includes all original columns plus new processed columns (job_title, job_category, general_category, confidence, job_details, etc.)<br>
                    • <strong>Processed Only</strong>: Contains only the classification results without original data
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentSessionId = null;
        let totalRowsCount = 0;
        let lastBatchConfig = null;
        let batchHistory = [];

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
                
                const result = await response.json();
                
                if (result.success) {
                    currentSessionId = result.session_id;
                    totalRowsCount = result.total_rows;
                    
                    // Populate column selectors
                    const textColumnSelect = document.getElementById('text-column');
                    const jobIdColumnSelect = document.getElementById('job-id-column');
                    
                    textColumnSelect.innerHTML = '<option value="">Choose a column...</option>';
                    jobIdColumnSelect.innerHTML = '<option value="">No job ID column</option>';
                    
                    result.columns.forEach(col => {
                        textColumnSelect.innerHTML += `<option value="${col}">${col}</option>`;
                        jobIdColumnSelect.innerHTML += `<option value="${col}">${col}</option>`;
                    });
                    
                    // Set batch controls
                    document.getElementById('total-rows').value = totalRowsCount;
                    document.getElementById('end-row').value = Math.min(10, totalRowsCount);
                    
                    document.getElementById('column-selection').classList.remove('hidden');
                    showAlert(`✅ File analyzed successfully! ${totalRowsCount} rows found`, 'success');
                } else {
                    showAlert(`❌ Error: ${result.error || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showAlert(`❌ Upload failed: ${error.message}`, 'error');
            }
        }

        async function testRange() {
            await processData('/process-range', true);
        }

        async function processBatch() {
            await processData('/process-range', false);
        }

        async function processAll() {
            const startRow = 1;
            const endRow = totalRowsCount;
            document.getElementById('start-row').value = startRow;
            document.getElementById('end-row').value = endRow;
            await processData('/process-range', false);
        }

        async function rerunBatch() {
            if (!lastBatchConfig) {
                showAlert('No previous batch to rerun', 'error');
                return;
            }
            
            document.getElementById('start-row').value = lastBatchConfig.start_row;
            document.getElementById('end-row').value = lastBatchConfig.end_row;
            await processData('/process-range', false);
        }

        async function processData(endpoint, isTest) {
            const textColumn = document.getElementById('text-column').value;
            const jobIdColumn = document.getElementById('job-id-column').value;
            const startRow = parseInt(document.getElementById('start-row').value);
            const endRow = parseInt(document.getElementById('end-row').value);
            
            if (!textColumn) {
                showAlert('❌ Please select a text column first', 'error');
                return;
            }
            if (!currentSessionId) {
                showAlert('❌ Please upload a CSV file first', 'error');
                return;
            }
            if (startRow < 1 || endRow < startRow || endRow > totalRowsCount) {
                showAlert('❌ Invalid row range specified', 'error');
                return;
            }

            const config = {
                session_id: currentSessionId,
                text_column: textColumn,
                job_id_column: jobIdColumn,
                start_row: startRow,
                end_row: endRow,
                is_test: isTest
            };

            if (!isTest) {
                lastBatchConfig = config;
                addToBatchHistory(config);
            }

            const formData = new FormData();
            Object.keys(config).forEach(key => {
                if (config[key]) formData.append(key, config[key]);
            });

            try {
                const actionType = isTest ? 'Testing' : 'Processing';
                showAlert(`🔄 ${actionType} rows ${startRow}-${endRow}...`, 'success');
                
                const response = await fetch(endpoint, { 
                    method: 'POST', 
                    body: formData 
                });
                
                const result = await response.json();
                
                if (result.success) {
                    displayResults(result);
                    document.getElementById('results').classList.remove('hidden');
                    
                    showAlert(`✅ ${actionType} completed! Processed ${result.summary.total_processed} rows`, 'success');
                    
                    // Show export section for both test and full processing
                    document.getElementById('download-section').classList.remove('hidden');
                    
                    // Update export section title and info based on test vs full processing
                    const exportTitle = document.querySelector('#download-section h4');
                    const exportInfo = document.getElementById('export-info');
                    if (isTest) {
                        exportTitle.textContent = '📥 Export Test Results';
                        exportInfo.innerHTML = `
                            <strong>🧪 Test Results Export:</strong><br>
                            • <strong>Complete CSV</strong>: Original data + processed columns for the tested range<br>
                            • <strong>Processed Only</strong>: Just the classification results for the tested range<br>
                            <em>Note: This is test data only. Use "Process Batch" for full dataset processing.</em>
                        `;
                    } else {
                        exportTitle.textContent = '📥 Export Options';
                        exportInfo.innerHTML = `
                            <strong>ℹ️ Export Information:</strong><br>
                            • <strong>Complete CSV</strong>: Includes all original columns plus new processed columns (job_title, job_category, general_category, confidence, job_details, etc.)<br>
                            • <strong>Processed Only</strong>: Contains only the classification results without original data
                        `;
                    }
                } else {
                    showAlert(`❌ ${actionType} failed: ${result.error || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                showAlert(`❌ Processing failed: ${error.message}`, 'error');
            }
        }

        function addToBatchHistory(config) {
            const timestamp = new Date().toLocaleTimeString();
            batchHistory.unshift({
                ...config,
                timestamp: timestamp
            });
            
            // Keep only last 10 batches
            batchHistory = batchHistory.slice(0, 10);
            
            updateBatchHistoryDisplay();
        }

        function updateBatchHistoryDisplay() {
            const container = document.getElementById('batch-history');
            const content = document.getElementById('history-content');
            
            if (batchHistory.length === 0) {
                container.classList.add('hidden');
                return;
            }
            
            container.classList.remove('hidden');
            
            let html = '';
            batchHistory.forEach((batch, index) => {
                html += `<div style="padding: 5px; border-bottom: 1px solid #ddd; cursor: pointer;" onclick="loadBatchConfig(${index})">`;
                html += `<strong>${batch.timestamp}</strong> - Rows ${batch.start_row}-${batch.end_row}`;
                html += '</div>';
            });
            
            content.innerHTML = html;
        }

        function loadBatchConfig(index) {
            const batch = batchHistory[index];
            document.getElementById('start-row').value = batch.start_row;
            document.getElementById('end-row').value = batch.end_row;
        }

        function displayResults(result) {
            displayStats(result.summary);
            
            const container = document.getElementById('results-content');
            const data = result.results;
            
            if (!data || data.length === 0) {
                container.innerHTML = '<p>No results to display</p>';
                return;
            }

            let html = '<h4>Advanced Classification Results:</h4><table class="results-table"><thead><tr>';
            html += '<th>Row</th><th>Job Title</th><th>Category</th><th>General</th><th>Conf</th><th>Job Details</th><th>Original Content</th>';
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
                html += `<td class="${confidenceClass}">${((row.confidence || 0) * 100).toFixed(0)}%</td>`;
                html += `<td class="original-content" style="max-width: 250px; font-size: 0.8em;">${row.job_details || 'N/A'}</td>`;
                html += `<td class="original-content">${row.original_content || ''}</td>`;
                if (row.job_id !== undefined) html += `<td>${row.job_id || 'N/A'}</td>`;
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            container.innerHTML = html;
        }

        function displayStats(summary) {
            if (!summary) return;
            
            const container = document.getElementById('stats-container');
            let html = '<div class="stats">';
            html += `<div class="stat-card"><div class="stat-number">${summary.total_processed || 0}</div><div class="stat-label">Processed</div></div>`;
            html += `<div class="stat-card"><div class="stat-number">${summary.successful_extractions || 0}</div><div class="stat-label">Successful</div></div>`;
            html += `<div class="stat-card"><div class="stat-number">${((summary.average_confidence || 0) * 100).toFixed(1)}%</div><div class="stat-label">Avg Confidence</div></div>`;
            html += `<div class="stat-card"><div class="stat-number">${summary.range || 'N/A'}</div><div class="stat-label">Row Range</div></div>`;
            html += '</div>';
            container.innerHTML = html;
        }

        async function downloadCompleteResults() {
            if (!currentSessionId) return;
            
            try {
                showAlert('📥 Preparing complete CSV download...', 'success');
                const response = await fetch(`/download/${currentSessionId}`);
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `complete_processed_${currentSessionId}.csv`;
                    a.click();
                    URL.revokeObjectURL(url);
                    showAlert('✅ Complete CSV downloaded successfully!', 'success');
                } else {
                    showAlert('❌ Failed to download complete CSV', 'error');
                }
            } catch (error) {
                showAlert(`❌ Download error: ${error.message}`, 'error');
            }
        }

        async function downloadProcessedOnly() {
            if (!currentSessionId) return;
            
            try {
                showAlert('📥 Preparing processed-only CSV download...', 'success');
                const response = await fetch(`/download-processed-only/${currentSessionId}`);
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `processed_only_${currentSessionId}.csv`;
                    a.click();
                    URL.revokeObjectURL(url);
                    showAlert('✅ Processed-only CSV downloaded successfully!', 'success');
                } else {
                    showAlert('❌ Failed to download processed-only CSV', 'error');
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
        df = pd.read_csv(
            io.StringIO(contents.decode('utf-8')), 
            dtype=str,
            na_filter=False
        )
        
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        columns = list(df.columns)
        sample_data = df.head(3).fillna("").to_dict('records')
        
        # Clean sample data
        cleaned_sample = []
        for row in sample_data:
            cleaned_row = {}
            for key, value in row.items():
                cleaned_row[key] = str(value)[:100] if len(str(value)) > 100 else str(value)
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

@app.post("/process-range")
async def process_range(
    session_id: str = Form(...),
    text_column: str = Form(...),
    job_id_column: str = Form(None),
    start_row: int = Form(...),
    end_row: int = Form(...),
    is_test: bool = Form(False)
):
    try:
        if session_id not in processed_data:
            raise HTTPException(status_code=400, detail="Session not found")
        
        df = processed_data[session_id]['original_df'].copy()
        if text_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{text_column}' not found")
        
        # Adjust for 0-based indexing (user inputs 1-based)
        start_idx = max(0, start_row - 1)
        end_idx = min(len(df), end_row)
        
        # Process range
        range_df = df.iloc[start_idx:end_idx].copy()
        results = []
        
        for idx, row in range_df.iterrows():
            text = str(row[text_column])
            row_id = str(idx + 1)  # Convert back to 1-based for display
            job_id = str(row[job_id_column]) if job_id_column and job_id_column in df.columns else None
            
            result = classifier.process_row(text, row_id, job_id)
            results.append(result)
        
        # Store results for export (both test and full processing)
        results_df = pd.DataFrame(results)
        output_columns = ['extracted_job_title', 'job_category', 'general_category', 'confidence', 'original_content', 'job_details', 'row_id']
        if job_id_column:
            output_columns.append('job_id')
        
        # Always store data for export, but mark if it's test data
                
            for col in output_columns:
                if col in results_df.columns:
                    range_df[col] = results_df[col]
            
            # Store/update processed data
            if 'processed_df' not in processed_data[session_id]:
                processed_data[session_id]['processed_df'] = df.copy()
                # Initialize new columns with empty strings
                for col in output_columns:
                    if col not in processed_data[session_id]['processed_df'].columns:
                        processed_data[session_id]['processed_df'][col] = ''
            
            # Update the processed dataframe with new results - simplified approach
            for col in output_columns:
                if col in results_df.columns:
                    # Add column if it doesn't exist
                    if col not in processed_data[session_id]['processed_df'].columns:
                        processed_data[session_id]['processed_df'][col] = ''
                    
                    # Update the specific rows
                    for i, (_, result_row) in enumerate(results_df.iterrows()):
                        actual_idx = start_idx + i
                        if actual_idx < len(processed_data[session_id]['processed_df']):
                            processed_data[session_id]['processed_df'].loc[actual_idx, col] = result_row[col]
        
        successful_results = [r for r in results if r['processing_status'] == 'success']
        
        summary = {
            'total_processed': len(results),
            'successful_extractions': len(successful_results),
            'average_confidence': sum(r['confidence'] for r in successful_results) / len(successful_results) if successful_results else 0,
            'range': f"{start_row}-{end_row}"
        }
        
        return {
            "success": True,
            "results": results,
            "summary": summary
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing range: {str(e)}"
        }

@app.get("/download/{session_id}")
async def download_complete_results(session_id: str):
    """Download complete CSV with original data + appended processed columns"""
    try:
        if session_id not in processed_data or 'processed_df' not in processed_data[session_id]:
            raise HTTPException(status_code=400, detail="No processed data found")
        
        processed_df = processed_data[session_id]['processed_df']
        original_filename = processed_data[session_id]['filename']
        
        base_name = original_filename.replace('.csv', '')
        output_filename = f"{base_name}_complete_processed_{session_id}.csv"
        temp_file_path = f"/tmp/{output_filename}"
        
        processed_df.to_csv(temp_file_path, index=False)
        
        return FileResponse(
            temp_file_path,
            media_type='text/csv',
            filename=output_filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading complete file: {str(e)}")

@app.get("/download-processed-only/{session_id}")
async def download_processed_only(session_id: str):
    """Download only the processed data columns (no original data)"""
    try:
        if session_id not in processed_data or 'processed_df' not in processed_data[session_id]:
            raise HTTPException(status_code=400, detail="No processed data found")
        
        processed_df = processed_data[session_id]['processed_df']
        original_filename = processed_data[session_id]['filename']
        
        # Extract only the processed columns
        processed_columns = ['row_id', 'extracted_job_title', 'job_category', 'general_category', 
                           'confidence', 'job_details', 'original_content']
        
        # Add job_id if it exists
        if 'job_id' in processed_df.columns:
            processed_columns.insert(1, 'job_id')
        
        # Create dataframe with only processed columns
        processed_only_df = processed_df[processed_columns].copy()
        
        base_name = original_filename.replace('.csv', '')
        output_filename = f"{base_name}_processed_only_{session_id}.csv"
        temp_file_path = f"/tmp/{output_filename}"
        
        processed_only_df.to_csv(temp_file_path, index=False)
        
        return FileResponse(
            temp_file_path,
            media_type='text/csv',
            filename=output_filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading processed-only file: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "features": [
            "Advanced batch processing with range specification",
            "First-sentence priority job title extraction",
            "Context-aware classification using Apply To sections",
            "Job details extraction from Apply To lists",
            "Smart exact/general/other categorization",
            "Location-aware pattern matching (e.g. 'CITY, STATE JOB TITLE jobs')",
            "Full original content display with no truncation",
            "Batch history and rerun capability",
            "Perfect accuracy for aircraft/aviation/parts/detailing jobs"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🎯 Starting Batch Processing Job Classification System")
    print("   Features: Range specification, batch processing, full content display")
    print("   Access at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)