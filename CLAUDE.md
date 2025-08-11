# JobListingsScraper - Advanced Data Processing System

## Project Overview
Comprehensive data processing system with persistent storage, flexible column mapping, batch management, selective reprocessing, and multi-platform export capabilities.

## Project Rules

### Persistent Storage Requirements
- Maintain processing state across sessions with resume capability
- Track all column transformations and rule applications
- Support selective reprocessing of specific rows/columns
- Implement versioning for data and rule changes
- Create audit trails for all modifications

### Data Export & Integration
- Support Google Sheets, Airtable, local files (CSV/Excel/JSON)
- Flexible column mapping for different output formats
- Batch processing with file splitting capabilities
- Real-time sync options for collaborative platforms
- Template-based output formatting

### State Persistence & Recovery
- Save processing checkpoints every 1000 rows
- Track rule application history per column
- Enable selective rollback of specific transformations
- Maintain row-level processing status
- Support pause/resume with exact state restoration

### Selective Reprocessing Framework
- Filter rows by keywords, patterns, or custom criteria
- Apply new rules to specific subsets of data
- Choose between creating new columns or overwriting existing ones
- Batch reprocessing with progress tracking
- Rule conflict detection and resolution

## Technology Stack
- **Backend**: Python with FastAPI for robust processing
- **Frontend**: HTML/CSS/JavaScript with progressive enhancement
- **Database**: SQLite for local projects (PostgreSQL for collaborative later)
- **Processing**: Pandas for data manipulation, BeautifulSoup/Playwright for scraping
- **Background Tasks**: Threading for local processing (Celery/Redis for production)

## Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py

# Run tests
python -m pytest tests/

# Build for production
python build.py
```

## Project Structure
```
JobListingsScraper/
├── src/
│   ├── core/
│   │   ├── processor.py      # Main data processing engine
│   │   ├── state_manager.py  # State persistence and checkpointing
│   │   ├── export_manager.py # Multi-platform export system
│   │   └── rule_engine.py    # Data transformation rules
│   ├── scrapers/
│   │   ├── base.py          # Base scraper interface
│   │   ├── indeed.py        # Indeed job scraper
│   │   └── linkedin.py      # LinkedIn job scraper
│   ├── web/
│   │   ├── app.py           # FastAPI web application
│   │   ├── static/          # CSS, JS, images
│   │   └── templates/       # HTML templates
│   └── utils/
│       ├── database.py      # Database operations
│       └── helpers.py       # Utility functions
├── tests/
├── data/                    # Processing data storage
├── exports/                 # Export outputs
├── checkpoints/            # Processing checkpoints
└── config/                 # Configuration files
```

## Current Development Phase
**Phase 2: Enhanced Job Classification System - COMPLETED**
- [x] AI-enhanced job title extraction with improved accuracy
- [x] Specific category classification (Aviation Mechanic vs generic Technician)
- [x] Advanced noise filtering (removes location names, marketing terms)
- [x] Original content and unique identifier tracking
- [x] Streamlined output format (removed experience/license columns)
- [x] Enhanced web interface with reference tracking
- [x] Comprehensive testing with problematic cases

## Enhanced System Usage Instructions

### Quick Start
```bash
# Install dependencies
pip install pandas fastapi uvicorn jinja2 python-multipart

# Run the enhanced application
python3 enhanced_server.py
```

### Access the Enhanced Application
1. Open browser to http://localhost:8000
2. Upload a CSV file with job posting text
3. Select the text column and optionally a job ID column
4. Test on a sample (10 rows) to verify accuracy
5. Process the full dataset
6. Download enhanced CSV with improved classifications

### Enhanced Classification Categories
**Specific Categories:**
- Aviation Mechanic, HVAC Technician, Security Guard, Construction Worker
- Project Manager, Welder, Plumber, Electrician, CDL Driver
- Registered Nurse, Licensed Practical Nurse, Veterinary Assistant
- Dental Assistant, Speech Pathologist, Technician, Pilot, Carpenter, Fitter

### Enhanced Output Columns
- `extracted_job_title`: Accurately extracted job title (improved algorithm)
- `job_category`: Specific category classification  
- `confidence`: Accuracy confidence score (0.0 to 1.0)
- `original_content`: Full job posting text for reference
- `row_id`: Row number for easy reference and feedback
- `job_id`: Original job ID if available (optional column)

### Key Improvements Over MVP
✅ **Better Job Title Extraction**: Filters out location names ("Blair Stone"), marketing terms ("satisfaction guaranteed")
✅ **Specific Categories**: "Aircraft" → "Aviation Mechanic" instead of generic "Technician"  
✅ **Reference Tracking**: Includes original content and unique identifiers for feedback
✅ **Noise Filtering**: Removes non-job-title text patterns
✅ **Validation Logic**: Ensures extracted titles are actual job roles

### Testing Files
- `enhanced_server.py`: Main enhanced application
- `test_enhanced_classifier.py`: Command-line testing script
- `test_problematic_cases.csv`: Challenging test cases
- `src/core/enhanced_classifier.py`: Core classification engine

### Test Results on Problematic Cases
| Input | Old Result | New Result |
|-------|------------|------------|
| "Aircraft maintenance technician needed..." | "Aircraft" → Technician | "Aircraft Maintenance Technician" → **Aviation Mechanic** |
| "Blair Stone location hiring construction..." | "Blair Stone" → Other | "Construction" → **Construction Worker** |
| "Customer satisfaction guaranteed - HVAC..." | "satisfaction guaranteed" → HVAC | "HVAC Technician" → **HVAC Technician** |
| "Airport security guard jobs..." | "Airport" → Other | "Security Guard" → **Security Guard** |

### Development Commands
```bash
# Test enhanced classifier
python3 test_enhanced_classifier.py

# Run enhanced server  
python3 enhanced_server.py

# Health check
curl http://localhost:8000/health
```