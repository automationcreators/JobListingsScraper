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
from utils.storage import storage
from utils.template_manager import template_manager, JobClassificationTemplate

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Batch Processing Job Classification System", version="3.0.0")

# Initialize classifier
classifier = AdvancedJobClassifier(use_ai=False)
processed_data = {}

# Performance mode: reduce storage operations during processing for speed
PERFORMANCE_MODE = True  # Set to False for maximum data safety, True for speed

# Load existing sessions on startup
try:
    existing_sessions = storage.list_sessions()
    print(f"🔄 Found {len(existing_sessions)} existing sessions in storage")
    for session_id, info in existing_sessions.items():
        print(f"   - {session_id}: {info['filename']} (saved: {info['saved_at']})")
except Exception as e:
    print(f"⚠️ Warning: Could not load existing sessions: {e}")

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
        
        /* Enhanced Refinement Interface Styles */
        .classification-refinement-panel { margin: 30px 0; }
        .filter-controls { background: #f8f9fa; border: 2px solid #e9ecef; border-radius: 8px; padding: 20px; margin: 20px 0; }
        .filter-row { display: grid; grid-template-columns: 1fr 1fr 2fr auto auto; gap: 15px; align-items: center; margin-top: 15px; }
        .filter-control { padding: 8px 12px; border: 1px solid #dee2e6; border-radius: 4px; font-size: 0.9rem; }
        .results-table-container { max-height: 600px; overflow-y: auto; border: 1px solid #dee2e6; border-radius: 6px; }
        .sortable-results-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
        .sortable-results-table th { background: #667eea; color: white; padding: 12px 8px; cursor: pointer; position: sticky; top: 0; z-index: 10; }
        .sortable-results-table th:hover { background: #5a67d8; }
        .sortable-results-table td { padding: 8px; border-bottom: 1px solid #e9ecef; }
        .sortable-results-table tr:hover { background: #f8f9ff; }
        .sortable-results-table tr.selected { background: #e3f2fd; }
        .row-checkbox { margin-right: 8px; }
        .confidence-indicator { padding: 2px 6px; border-radius: 3px; color: white; font-size: 0.75em; font-weight: bold; }
        .confidence-high { background: #28a745; }
        .confidence-medium { background: #ffc107; color: #212529; }
        .confidence-low { background: #dc3545; }
        .confidence-failed { background: #6c757d; }
        .original-text-preview { max-width: 200px; font-size: 0.8em; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .filtered-count { font-size: 0.9em; color: #6c757d; font-weight: 500; }
        .bulk-actions { background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 6px; padding: 15px; margin: 10px 0; }
        .bulk-actions.hidden { display: none; }
        .action-btn { padding: 8px 16px; margin: 0 5px; border: none; border-radius: 4px; cursor: pointer; font-size: 0.8rem; }
        .action-btn.primary { background: #667eea; color: white; }
        .action-btn.success { background: #28a745; color: white; }
        .action-btn.warning { background: #ffc107; color: #212529; }
        .action-btn.danger { background: #dc3545; color: white; }
        
        /* Progress Tracking Styles */
        .batch-progress-container { margin: 20px 0; }
        .progress-bar-container { background: #e9ecef; border-radius: 10px; height: 20px; margin: 10px 0; overflow: hidden; }
        .progress-bar { height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); transition: width 0.3s ease; border-radius: 10px; }
        .progress-bar.success { background: linear-gradient(90deg, #28a745 0%, #20c997 100%); }
        .progress-bar.error { background: linear-gradient(90deg, #dc3545 0%, #e74c3c 100%); }
        .progress-text { font-size: 0.85em; color: #6c757d; margin-top: 5px; text-align: center; }
        .batch-progress-text { font-size: 0.9rem; color: #495057; margin: 5px 0; font-weight: 500; }
        .progress-status { display: flex; align-items: center; gap: 10px; margin: 10px 0; }
        .status-indicator { font-size: 1.2rem; }
        .status-indicator.success { color: #28a745; }
        .status-indicator.error { color: #dc3545; }
        .status-indicator.processing { color: #667eea; animation: pulse 1.5s infinite; }
        .status-indicator.cancelled { color: #6c757d; }
        
        /* Batch History Enhanced Styles */
        .batch-item { padding: 12px; margin: 8px 0; border: 1px solid #dee2e6; border-radius: 6px; background: #fff; cursor: pointer; transition: all 0.2s ease; border-left: 4px solid #6c757d; }
        .batch-item:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .batch-completed { border-left-color: #28a745 !important; }
        .batch-error { border-left-color: #dc3545 !important; }
        .batch-processing { border-left-color: #667eea !important; }
        .batch-cancelled { border-left-color: #6c757d !important; }
        .batch-header { display: flex; align-items: center; gap: 8px; font-weight: 500; margin-bottom: 5px; }
        .batch-status-icon { font-size: 1.1em; min-width: 20px; text-align: center; }
        .processing-spinner { animation: pulse 1.5s ease-in-out infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .batch-info { flex: 1; }
        .batch-meta { font-size: 0.8rem; color: #6c757d; }
        .batch-actions { display: flex; gap: 5px; }
        
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
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
        let currentBatchId = null;
        let progressInterval = null;

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

            let batchId = null;
            if (!isTest) {
                lastBatchConfig = config;
                batchId = addToBatchHistory(config);
                currentBatchId = batchId;
            }

            const formData = new FormData();
            Object.keys(config).forEach(key => {
                if (config[key]) formData.append(key, config[key]);
            });

            try {
                const actionType = isTest ? 'Testing' : 'Processing';
                showAlert(`🔄 ${actionType} rows ${startRow}-${endRow}...`, 'success');
                
                // Start progress tracking for non-test batches
                if (!isTest && batchId) {
                    startProgressTracking(batchId, startRow, endRow);
                }
                
                const response = await fetch(endpoint, { 
                    method: 'POST', 
                    body: formData 
                });
                
                const result = await response.json();
                
                // Stop progress tracking
                if (!isTest && batchId) {
                    stopProgressTracking();
                }
                
                if (result.success) {
                    // Complete batch tracking
                    if (!isTest && batchId) {
                        completeBatch(batchId, true);
                    }
                    
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
                    if (!isTest && batchId) {
                        completeBatch(batchId, false);
                    }
                    showAlert(`❌ ${actionType} failed: ${result.error || 'Unknown error'}`, 'error');
                }
            } catch (error) {
                if (!isTest && batchId) {
                    completeBatch(batchId, false);
                    stopProgressTracking();
                }
                showAlert(`❌ Processing failed: ${error.message}`, 'error');
            }
        }

        function addToBatchHistory(config) {
            const timestamp = new Date().toLocaleTimeString();
            const batchId = `batch_${Date.now()}`;
            batchHistory.unshift({
                ...config,
                timestamp: timestamp,
                batchId: batchId,
                status: 'processing',
                progress: 0,
                totalRows: config.end_row - config.start_row + 1
            });
            
            // Keep only last 10 batches
            batchHistory = batchHistory.slice(0, 10);
            
            updateBatchHistoryDisplay();
            return batchId;
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
                const statusIcon = getStatusIcon(batch.status);
                const progressPercent = batch.progress || 0;
                
                html += `<div class="batch-item batch-${batch.status}" onclick="loadBatchConfig(${index})">`;
                html += `  <div class="batch-header">`;
                html += `    <span class="batch-status-icon">${statusIcon}</span>`;
                html += `    <strong>${batch.timestamp}</strong> - Rows ${batch.start_row}-${batch.end_row}`;
                html += `  </div>`;
                
                // Add progress bar for processing status
                if (batch.status === 'processing') {
                    html += `  <div class="progress-bar-container">`;
                    html += `    <div class="progress-bar" style="width: ${progressPercent}%"></div>`;
                    html += `  </div>`;
                    html += `  <div class="progress-text">${Math.round(progressPercent)}% complete</div>`;
                }
                
                html += '</div>';
            });
            
            content.innerHTML = html;
        }
        
        function getStatusIcon(status) {
            switch(status) {
                case 'completed': return '✅';
                case 'error': return '❌';
                case 'cancelled': return '❌';
                case 'processing': return '<span class="processing-spinner">⚡</span>';
                default: return '⏳';
            }
        }
        
        function updateBatchProgress(batchId, progress, status = 'processing') {
            const batch = batchHistory.find(b => b.batchId === batchId);
            if (batch) {
                batch.progress = progress;
                batch.status = status;
                updateBatchHistoryDisplay();
            }
        }
        
        function completeBatch(batchId, success = true) {
            const batch = batchHistory.find(b => b.batchId === batchId);
            if (batch) {
                batch.progress = 100;
                batch.status = success ? 'completed' : 'error';
                updateBatchHistoryDisplay();
            }
        }
        
        function startProgressTracking(batchId, startRow, endRow) {
            currentBatchId = batchId;
            const totalRows = endRow - startRow + 1;
            let currentProgress = 0;
            
            // Simulate progress tracking (since we don't have real-time feedback from server)
            progressInterval = setInterval(() => {
                currentProgress += 5; // Increment progress
                if (currentProgress >= 95) {
                    currentProgress = 95; // Cap at 95% until actual completion
                }
                updateBatchProgress(batchId, currentProgress);
            }, 200); // Update every 200ms
        }
        
        function stopProgressTracking() {
            if (progressInterval) {
                clearInterval(progressInterval);
                progressInterval = null;
            }
            currentBatchId = null;
        }

        function loadBatchConfig(index) {
            const batch = batchHistory[index];
            document.getElementById('start-row').value = batch.start_row;
            document.getElementById('end-row').value = batch.end_row;
        }

        // Global variables for enhanced interface
        let globalResultsData = [];
        let filteredData = [];
        let selectedRows = new Set();
        let sortColumn = '';
        let sortDirection = 'asc';

        function displayResults(result) {
            displayStats(result.summary);
            
            globalResultsData = result.results || [];
            filteredData = [...globalResultsData];
            selectedRows.clear();
            
            const container = document.getElementById('results-content');
            
            if (!globalResultsData || globalResultsData.length === 0) {
                container.innerHTML = '<p>No results to display</p>';
                return;
            }

            // Build enhanced interface
            let html = `
                <div class="classification-refinement-panel">
                    <h4>🔍 Interactive Classification Results</h4>
                    
                    <!-- Filter Controls -->
                    <div class="filter-controls">
                        <h5>Filter & Search Results</h5>
                        <div class="filter-row">
                            <select id="confidence-filter" class="filter-control" onchange="applyFilters()">
                                <option value="all">All Confidence Levels</option>
                                <option value="high">High (&gt;70%)</option>
                                <option value="medium">Medium (40-70%)</option>
                                <option value="low">Low (&lt;40%)</option>
                                <option value="failed">Failed Extractions</option>
                            </select>
                            
                            <select id="category-filter" class="filter-control" onchange="applyFilters()">
                                <option value="all">All Categories</option>
                                <option value="Unable to Classify">Unable to Classify</option>
                                <option value="Aviation Mechanic">Aviation Mechanic</option>
                                <option value="HVAC Technician">HVAC Technician</option>
                                <option value="Security Guard">Security Guard</option>
                                <option value="Address">Address</option>
                            </select>
                            
                            <input type="text" id="keyword-search" class="filter-control" placeholder="Search original text..." onkeyup="applyFilters()">
                            
                            <button onclick="applyFilters()" class="action-btn primary">Apply Filters</button>
                            <span id="filtered-count" class="filtered-count">0 rows shown</span>
                        </div>
                    </div>

                    <!-- Bulk Actions (hidden by default) -->
                    <div id="bulk-actions" class="bulk-actions hidden">
                        <strong>Selected <span id="selection-count">0</span> rows:</strong>
                        <button onclick="markAsCorrect()" class="action-btn success">✅ Mark as Correct</button>
                        <button onclick="exportSelected()" class="action-btn primary">📤 Export Selected</button>
                        <button onclick="createRuleFromSelected()" class="action-btn warning">🔧 Create Rule</button>
                        <button onclick="clearSelection()" class="action-btn">Clear Selection</button>
                    </div>
                    
                    <!-- Enhanced Results Table -->
                    <div class="results-table-container">
                        <table class="sortable-results-table">
                            <thead>
                                <tr>
                                    <th><input type="checkbox" id="select-all" onchange="toggleSelectAll()"></th>
                                    <th onclick="sortBy('confidence')">Confidence ↕️</th>
                                    <th onclick="sortBy('category')">Category ↕️</th>
                                    <th onclick="sortBy('job_title')">Job Title ↕️</th>
                                    <th onclick="sortBy('job_count')">Count ↕️</th>
                                    <th onclick="sortBy('city')">City ↕️</th>
                                    <th onclick="sortBy('state')">State ↕️</th>
                                    <th>Original Text</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="results-tbody">
                                <!-- Filtered results populated here -->
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
            
            container.innerHTML = html;
            populateResultsTable();
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

        // Enhanced interface functions
        function populateResultsTable() {
            const tbody = document.getElementById('results-tbody');
            if (!tbody) return;
            
            let html = '';
            filteredData.forEach((row, index) => {
                const isSelected = selectedRows.has(row.row_id || index);
                const confidence = (row.confidence || 0) * 100;
                const confidenceClass = confidence > 70 ? 'confidence-high' : 
                                       confidence > 40 ? 'confidence-medium' : 
                                       confidence > 0 ? 'confidence-low' : 'confidence-failed';
                
                html += `
                    <tr class="${isSelected ? 'selected' : ''}" data-row-id="${row.row_id || index}">
                        <td><input type="checkbox" class="row-checkbox" ${isSelected ? 'checked' : ''} onchange="toggleRowSelection('${row.row_id || index}')"></td>
                        <td><span class="confidence-indicator ${confidenceClass}">${confidence.toFixed(0)}%</span></td>
                        <td>${row.job_category || 'N/A'}</td>
                        <td><strong>${row.extracted_job_title || 'N/A'}</strong></td>
                        <td style="text-align: center;">${row.job_count || '-'}</td>
                        <td>${row.city || '-'}</td>
                        <td><strong>${row.state || '-'}</strong></td>
                        <td class="original-text-preview" title="${(row.original_content || '').replace(/"/g, '&quot;')}">${(row.original_content || '').substring(0, 100)}${(row.original_content || '').length > 100 ? '...' : ''}</td>
                        <td>
                            <button onclick="editRow('${row.row_id || index}')" class="action-btn primary" style="font-size: 0.7rem; padding: 4px 8px;">✏️ Edit</button>
                        </td>
                    </tr>
                `;
            });
            
            tbody.innerHTML = html;
            updateFilteredCount();
        }

        function applyFilters() {
            const confidenceFilter = document.getElementById('confidence-filter').value;
            const categoryFilter = document.getElementById('category-filter').value;
            const keywordSearch = document.getElementById('keyword-search').value.toLowerCase();
            
            filteredData = globalResultsData.filter(row => {
                // Confidence filter
                const confidence = (row.confidence || 0) * 100;
                if (confidenceFilter === 'high' && confidence <= 70) return false;
                if (confidenceFilter === 'medium' && (confidence <= 40 || confidence > 70)) return false;
                if (confidenceFilter === 'low' && (confidence <= 0 || confidence > 40)) return false;
                if (confidenceFilter === 'failed' && confidence > 0) return false;
                
                // Category filter
                if (categoryFilter !== 'all' && (row.job_category || '') !== categoryFilter) return false;
                
                // Keyword search
                if (keywordSearch && !(row.original_content || '').toLowerCase().includes(keywordSearch)) return false;
                
                return true;
            });
            
            populateResultsTable();
        }

        function sortBy(column) {
            if (sortColumn === column) {
                sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = column;
                sortDirection = 'asc';
            }
            
            filteredData.sort((a, b) => {
                let aVal, bVal;
                
                switch(column) {
                    case 'confidence':
                        aVal = a.confidence || 0;
                        bVal = b.confidence || 0;
                        break;
                    case 'category':
                        aVal = a.job_category || '';
                        bVal = b.job_category || '';
                        break;
                    case 'job_title':
                        aVal = a.extracted_job_title || '';
                        bVal = b.extracted_job_title || '';
                        break;
                    case 'job_count':
                        aVal = parseInt(a.job_count) || 0;
                        bVal = parseInt(b.job_count) || 0;
                        break;
                    case 'city':
                        aVal = a.city || '';
                        bVal = b.city || '';
                        break;
                    case 'state':
                        aVal = a.state || '';
                        bVal = b.state || '';
                        break;
                    default:
                        return 0;
                }
                
                if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
                if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
                return 0;
            });
            
            populateResultsTable();
        }

        function toggleSelectAll() {
            const selectAll = document.getElementById('select-all');
            const checkboxes = document.querySelectorAll('.row-checkbox');
            
            selectedRows.clear();
            
            if (selectAll.checked) {
                filteredData.forEach((row, index) => {
                    selectedRows.add(row.row_id || index);
                });
                checkboxes.forEach(cb => cb.checked = true);
            } else {
                checkboxes.forEach(cb => cb.checked = false);
            }
            
            updateSelectionUI();
        }

        function toggleRowSelection(rowId) {
            if (selectedRows.has(rowId)) {
                selectedRows.delete(rowId);
            } else {
                selectedRows.add(rowId);
            }
            
            updateSelectionUI();
        }

        function updateSelectionUI() {
            const bulkActions = document.getElementById('bulk-actions');
            const selectionCount = document.getElementById('selection-count');
            const selectAll = document.getElementById('select-all');
            
            if (selectedRows.size > 0) {
                bulkActions.classList.remove('hidden');
                selectionCount.textContent = selectedRows.size;
            } else {
                bulkActions.classList.add('hidden');
            }
            
            // Update select-all checkbox state
            const totalVisible = filteredData.length;
            if (selectedRows.size === totalVisible && totalVisible > 0) {
                selectAll.checked = true;
                selectAll.indeterminate = false;
            } else if (selectedRows.size > 0) {
                selectAll.checked = false;
                selectAll.indeterminate = true;
            } else {
                selectAll.checked = false;
                selectAll.indeterminate = false;
            }
            
            // Update row highlighting
            document.querySelectorAll('tbody tr').forEach(row => {
                const rowId = row.dataset.rowId;
                if (selectedRows.has(rowId)) {
                    row.classList.add('selected');
                } else {
                    row.classList.remove('selected');
                }
            });
        }

        function updateFilteredCount() {
            const filteredCountElement = document.getElementById('filtered-count');
            if (filteredCountElement) {
                filteredCountElement.textContent = `${filteredData.length} of ${globalResultsData.length} rows shown`;
            }
        }

        function clearSelection() {
            selectedRows.clear();
            document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = false);
            document.getElementById('select-all').checked = false;
            updateSelectionUI();
        }

        // Placeholder functions for future implementation
        function markAsCorrect() {
            alert(`Marking ${selectedRows.size} rows as correct - Feature coming soon!`);
        }

        function exportSelected() {
            alert(`Exporting ${selectedRows.size} selected rows - Feature coming soon!`);
        }

        function createRuleFromSelected() {
            alert(`Creating rule from ${selectedRows.size} selected rows - Feature coming soon!`);
        }

        function editRow(rowId) {
            alert(`Editing row ${rowId} - Feature coming soon!`);
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
            'filename': file.filename,
            'original_columns': list(df.columns)  # Store original column list
        }
        
        # Save session to persistent storage (only in safety mode for initial upload)
        if not PERFORMANCE_MODE:
            storage.save_session(session_id, processed_data[session_id])
        
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
        
        # Dynamically determine all available columns from the results
        available_columns = list(results_df.columns)
        
        # Define the standard expected columns in preferred order
        preferred_order = ['row_id', 'job_id', 'extracted_job_title', 'job_category', 'general_category', 
                          'confidence', 'job_count', 'city', 'state', 'job_details', 'original_content', 
                          'processing_status', 'extraction_method']
        
        # Build output_columns list: preferred order first, then any additional columns
        output_columns = []
        for col in preferred_order:
            if col in available_columns:
                output_columns.append(col)
        
        # Add any additional columns not in preferred order
        for col in available_columns:
            if col not in output_columns:
                output_columns.append(col)
        
        # Remove job_id if not provided
        if not job_id_column:
            output_columns = [col for col in output_columns if col != 'job_id']
        
        # Always store data for export, but mark if it's test data
        # Store/update processed data
        if 'processed_df' not in processed_data[session_id]:
            processed_data[session_id]['processed_df'] = df.copy()
            # Store reference to original columns for export differentiation
            processed_data[session_id]['original_df'] = df.copy()
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
            
            # Save to persistent storage based on performance mode
            rows_processed = end_idx - start_idx
            total_rows = len(processed_data[session_id]['original_df'])
            is_completion = end_row >= total_rows
            
            if PERFORMANCE_MODE:
                # Performance mode: only save at completion or large batches
                if is_completion or rows_processed >= 1000:
                    try:
                        storage.save_session(session_id, processed_data[session_id])
                        logging.info(f"Saved session {session_id} ({'completion' if is_completion else 'checkpoint'})")
                    except Exception as e:
                        logging.warning(f"Storage save failed (non-critical): {e}")
            else:
                # Safety mode: save after every batch
                try:
                    storage.save_session(session_id, processed_data[session_id])
                except Exception as e:
                    logging.warning(f"Storage save failed (non-critical): {e}")
        
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
        # Try memory first, then load from storage if needed
        if session_id not in processed_data:
            session_data = storage.load_session(session_id)
            if session_data:
                processed_data[session_id] = session_data
        
        if session_id not in processed_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        if 'processed_df' not in processed_data[session_id]:
            raise HTTPException(status_code=400, detail="No processed data found. Please process some data first using 'Process Batch' or 'Process All Rows'.")
        
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
        # Try memory first, then load from storage if needed
        if session_id not in processed_data:
            session_data = storage.load_session(session_id)
            if session_data:
                processed_data[session_id] = session_data
        
        if session_id not in processed_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        if 'processed_df' not in processed_data[session_id]:
            raise HTTPException(status_code=400, detail="No processed data found. Please process some data first using 'Process Batch' or 'Process All Rows'.")
        
        processed_df = processed_data[session_id]['processed_df']
        original_filename = processed_data[session_id]['filename']
        
        # Dynamically extract all processed columns (non-original data columns)
        all_columns = list(processed_df.columns)
        original_columns = list(processed_data[session_id]['original_df'].columns) if 'original_df' in processed_data[session_id] else []
        
        # Processed columns are those not in original data
        processed_columns = [col for col in all_columns if col not in original_columns]
        
        # Ensure we have the key columns in preferred order
        preferred_processed_order = ['row_id', 'job_id', 'extracted_job_title', 'job_category', 'general_category', 
                                   'confidence', 'job_count', 'city', 'state', 'job_details', 'original_content']
        
        # Reorder processed columns: preferred first, then any extras
        ordered_processed_columns = []
        for col in preferred_processed_order:
            if col in processed_columns:
                ordered_processed_columns.append(col)
        
        # Add any additional processed columns
        for col in processed_columns:
            if col not in ordered_processed_columns:
                ordered_processed_columns.append(col)
        
        processed_columns = ordered_processed_columns
        
        # Filter to only columns that exist in the dataframe
        existing_processed_columns = [col for col in processed_columns if col in processed_df.columns]
        
        if not existing_processed_columns:
            raise HTTPException(status_code=400, detail="No processed columns found in dataset")
        
        # Create dataframe with only processed columns
        processed_only_df = processed_df[existing_processed_columns].copy()
        
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
            "Perfect accuracy for aircraft/aviation/parts/detailing jobs",
            "Dynamic column export with job_count, city, state extraction"
        ]
    }

@app.get("/sessions")
async def list_sessions():
    """List all sessions (in-memory + persistent) with their data status"""
    all_sessions = []
    
    # Add in-memory sessions
    for session_id, data in processed_data.items():
        session_info = {
            'session_id': session_id,
            'filename': data.get('filename', 'unknown'),
            'has_original': 'original_df' in data,
            'has_processed': 'processed_df' in data,
            'original_rows': len(data['original_df']) if 'original_df' in data else 0,
            'processed_columns': list(data['processed_df'].columns) if 'processed_df' in data else [],
            'storage_type': 'memory',
            'saved_at': 'current_session'
        }
        all_sessions.append(session_info)
    
    # Add persistent sessions that aren't in memory
    try:
        persistent_sessions = storage.list_sessions()
        for session_id, info in persistent_sessions.items():
            if session_id not in processed_data:
                session_info = {
                    'session_id': session_id,
                    'filename': info.get('filename', 'unknown'),
                    'has_original': info.get('has_original', False),
                    'has_processed': info.get('has_processed', False),
                    'original_rows': 'unknown',
                    'processed_columns': 'unknown',
                    'storage_type': 'disk',
                    'saved_at': info.get('saved_at', 'unknown')
                }
                all_sessions.append(session_info)
    except Exception as e:
        logging.error(f"Error loading persistent sessions: {e}")
    
    return {'sessions': all_sessions}

@app.get("/session/{session_id}/columns")
async def get_session_columns(session_id: str):
    """Get detailed column information for a session"""
    if session_id not in processed_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    data = processed_data[session_id]
    original_columns = list(data['original_df'].columns) if 'original_df' in data else []
    processed_columns = list(data['processed_df'].columns) if 'processed_df' in data else []
    
    # Identify which columns are processed vs original
    new_columns = [col for col in processed_columns if col not in original_columns]
    
    return {
        'session_id': session_id,
        'filename': data.get('filename', 'unknown'),
        'original_columns': original_columns,
        'processed_columns': processed_columns,
        'new_columns': new_columns,
        'total_rows': len(data['processed_df']) if 'processed_df' in data else 0
    }

# Template Management Endpoints

@app.get("/templates")
async def list_templates():
    """List all available processing templates"""
    templates = template_manager.list_templates()
    return {'templates': templates}

@app.post("/templates/save")
async def save_template(
    name: str = Form(...),
    description: str = Form(""),
    template_type: str = Form("job_classification")
):
    """Save current job classification setup as a template"""
    try:
        if template_type == "job_classification":
            config = JobClassificationTemplate.create_from_classifier(classifier)
            success = template_manager.save_template(name, config, description)
            
            if success:
                return {
                    'success': True,
                    'message': f'Template "{name}" saved successfully',
                    'template_name': name
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to save template")
        else:
            raise HTTPException(status_code=400, detail="Unsupported template type")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving template: {str(e)}")

@app.get("/templates/{template_name}")
async def get_template(template_name: str):
    """Get details of a specific template"""
    template = template_manager.load_template(template_name)
    if template:
        return template
    else:
        raise HTTPException(status_code=404, detail="Template not found")

@app.delete("/templates/{template_name}")
async def delete_template(template_name: str):
    """Delete a template"""
    success = template_manager.delete_template(template_name)
    if success:
        return {'success': True, 'message': f'Template "{template_name}" deleted'}
    else:
        raise HTTPException(status_code=404, detail="Template not found")

@app.post("/templates/{template_name}/apply")
async def apply_template(template_name: str, session_id: str = Form(...)):
    """Apply a template to a session (future functionality)"""
    template = template_manager.load_template(template_name)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # For now, just return the template info
    # In the future, this would configure the classifier for the session
    return {
        'message': f'Template "{template_name}" ready to apply',
        'template': template['config'],
        'session_id': session_id
    }

if __name__ == "__main__":
    import uvicorn
    print("🎯 Starting Batch Processing Job Classification System")
    print("   Features: Range specification, batch processing, full content display")
    print("   Templates: Save and reuse processing configurations")
    print("   Access at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)