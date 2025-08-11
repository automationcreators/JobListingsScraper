from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import pandas as pd
import io
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.mvp_classifier import MVPJobClassifier

app = FastAPI(title="MVP Job Classification System", version="1.0.0")

# Mount static files and templates
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

# Create static directory if it doesn't exist
os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Initialize classifier
classifier = MVPJobClassifier()

# Global variable to store processed data for download
processed_data = {}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Main page with CSV upload interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze-csv")
async def analyze_csv_file(file: UploadFile = File(...)):
    """Analyze uploaded CSV file and return column information and sample data"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Please upload a CSV file")
        
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        # Get column information
        columns = list(df.columns)
        
        # Get sample data (first 3 rows)
        sample_data = df.head(3).to_dict('records')
        
        # Store the original data for processing
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        processed_data[session_id] = {
            'original_df': df,
            'filename': file.filename
        }
        
        return {
            "success": True,
            "columns": columns,
            "sample_data": sample_data,
            "total_rows": len(df),
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing CSV: {str(e)}")

@app.post("/test-sample")
async def test_sample_processing(
    session_id: str = Form(...),
    text_column: str = Form(...),
    test_rows: int = Form(10)
):
    """Test classification on a sample of rows"""
    try:
        if session_id not in processed_data:
            raise HTTPException(status_code=400, detail="Session not found. Please upload file again.")
        
        df = processed_data[session_id]['original_df'].copy()
        
        if text_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{text_column}' not found")
        
        # Process only the first test_rows
        test_df = df.head(test_rows)
        
        # Process each row
        results = []
        for idx, row in test_df.iterrows():
            text = str(row[text_column])
            result = classifier.process_row(text)
            result['original_text'] = text[:100] + "..." if len(text) > 100 else text
            result['row_index'] = idx
            results.append(result)
        
        # Generate summary
        successful_results = [r for r in results if r['processing_status'] == 'success']
        avg_confidence = sum(r['confidence'] for r in successful_results) / len(successful_results) if successful_results else 0
        
        summary = {
            'total_tested': len(results),
            'successful_extractions': len(successful_results),
            'average_confidence': round(avg_confidence, 3),
            'low_confidence_count': len([r for r in results if r['confidence'] < 0.5])
        }
        
        return {
            "success": True,
            "test_results": results,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing sample: {str(e)}")

@app.post("/process-full")
async def process_full_dataset(
    session_id: str = Form(...),
    text_column: str = Form(...),
    include_confidence: bool = Form(False)
):
    """Process the complete dataset"""
    try:
        if session_id not in processed_data:
            raise HTTPException(status_code=400, detail="Session not found. Please upload file again.")
        
        df = processed_data[session_id]['original_df'].copy()
        
        if text_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{text_column}' not found")
        
        # Process the entire dataset
        processed_df = classifier.process_dataframe(df, text_column)
        
        # Remove confidence column if not requested
        if not include_confidence:
            processed_df = processed_df.drop('confidence', axis=1)
        
        # Generate processing summary
        summary = classifier.get_processing_summary(processed_df)
        
        # Store processed data for download
        processed_data[session_id]['processed_df'] = processed_df
        processed_data[session_id]['summary'] = summary
        
        # Get sample of results for preview
        sample_results = processed_df.head(5)[
            ['extracted_job_title', 'job_category', 'experience_level', 'license_required', 'job_function']
        ].to_dict('records')
        
        return {
            "success": True,
            "summary": summary,
            "sample_results": sample_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing dataset: {str(e)}")

@app.get("/download/{session_id}")
async def download_results(session_id: str):
    """Download processed CSV file"""
    try:
        if session_id not in processed_data or 'processed_df' not in processed_data[session_id]:
            raise HTTPException(status_code=400, detail="No processed data found for this session")
        
        processed_df = processed_data[session_id]['processed_df']
        original_filename = processed_data[session_id]['filename']
        
        # Create filename for processed data
        base_name = original_filename.replace('.csv', '')
        output_filename = f"{base_name}_classified_{session_id}.csv"
        
        # Save to temporary file
        temp_file_path = f"/tmp/{output_filename}"
        processed_df.to_csv(temp_file_path, index=False)
        
        return FileResponse(
            temp_file_path,
            media_type='text/csv',
            filename=output_filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

@app.get("/processing-report/{session_id}")
async def get_processing_report(session_id: str):
    """Get detailed processing report"""
    try:
        if session_id not in processed_data or 'summary' not in processed_data[session_id]:
            raise HTTPException(status_code=400, detail="No processing summary found for this session")
        
        summary = processed_data[session_id]['summary']
        
        return {
            "success": True,
            "report": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "classifier_ready": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)