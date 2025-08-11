#!/usr/bin/env python3
"""
MVP Job Classification System - Main Runner
Run this to start the web interface for CSV job classification
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add src directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Import the FastAPI app
from web.mvp_app import app

def main():
    """Main entry point for the MVP application"""
    print("🎯 Starting MVP Job Classification System")
    print("=" * 50)
    print("📊 Features:")
    print("  • CSV file upload and processing")
    print("  • Job title extraction from text")  
    print("  • Classification into 13 predefined categories")
    print("  • Experience level detection")
    print("  • License requirement analysis")
    print("  • Job function identification")
    print("  • Confidence scoring")
    print("  • Sample testing capability")
    print("  • Processed CSV download")
    print()
    print("🚀 Starting web server...")
    print("   Access the application at: http://localhost:8000")
    print("   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Run the FastAPI server
        uvicorn.run(
            "web.mvp_app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down MVP Job Classification System")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("Please ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()