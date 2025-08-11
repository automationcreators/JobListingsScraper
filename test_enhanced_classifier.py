#!/usr/bin/env python3

import sys
import os
import pandas as pd

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from core.enhanced_classifier import EnhancedJobClassifier
    USE_ENHANCED = True
except ImportError:
    USE_ENHANCED = False
    print("Enhanced classifier not available, using inline version")

# Fallback inline classifier (same as in enhanced_server.py)
class InlineEnhancedClassifier:
    def __init__(self):
        self.job_categories = {
            'Aviation Mechanic': ['aircraft', 'aviation', 'airplane', 'aircraft maintenance', 'a&p mechanic', 'aviation mechanic'],
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
            'Pilot': ['pilot', 'airline pilot', 'commercial pilot'],
            'Carpenter': ['carpenter', 'carpentry'],
            'Fitter': ['fitter', 'pipefitter', 'mechanical fitter']
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

    def extract_job_title(self, text):
        if not text or pd.isna(text):
            return "Unable to extract job title"
            
        import re
        text = str(text).strip().lower()
        
        # Remove noise patterns
        cleaned_text = text
        for pattern in self.noise_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        # Direct job title matching
        job_title_patterns = [
            r'\b(aircraft\s+maintenance\s+technician|aviation\s+mechanic|aircraft\s+mechanic)\b',
            r'\b(hvac\s+technician|heating\s+technician|air\s+conditioning\s+technician)\b',
            r'\b(security\s+guard|security\s+officer)\b',
            r'\b(construction\s+worker|construction\s+laborer)\b',
            r'\b(repair\s+technician|service\s+technician|maintenance\s+technician)\b',
            r'\b(steel\s+worker|welder|welding\s+technician)\b',
            r'\b(pipefitter|plumber|plumbing\s+technician)\b',
            r'\b(electrician|electrical\s+technician)\b',
            r'\b(airline\s+pilot|commercial\s+pilot|pilot)\b',
            r'\b(carpenter|carpentry\s+worker)\b'
        ]
        
        for pattern in job_title_patterns:
            match = re.search(pattern, text)
            if match:
                title = match.group(1)
                return ' '.join(word.capitalize() for word in title.split())
        
        # Fallback pattern matching
        fallback_patterns = [
            r'([a-z\s]*(?:technician|mechanic|specialist|worker|guard|officer|pilot|carpenter|fitter|electrician|plumber))',
            r'(hvac|aircraft|aviation|construction|security|repair|steel|welding)',
        ]
        
        for pattern in fallback_patterns:
            match = re.search(pattern, cleaned_text)
            if match:
                potential_title = match.group(1).strip()
                if self._validate_job_title(potential_title):
                    return ' '.join(word.capitalize() for word in potential_title.split())
        
        return "Unable to extract job title"
    
    def _validate_job_title(self, title):
        if not title or len(title) < 3:
            return False
        
        import re
        title_lower = title.lower()
        
        # Invalid patterns
        invalid_patterns = [
            r'\b(blair|stone|airport|satisfaction|guaranteed|az|dallas)\b',
            r'^\d+$', r'^[A-Z\s]+$'
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, title_lower):
                return False
        
        return True
    
    def classify_job_category(self, job_title, full_text=""):
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
    
    def process_row(self, text, row_id=None, job_id=None):
        job_title = self.extract_job_title(text)
        category = self.classify_job_category(job_title, text)
        confidence = 0.8 if job_title != "Unable to extract job title" and category != 'Other' else 0.3
        
        return {
            'extracted_job_title': job_title,
            'job_category': category,
            'confidence': confidence,
            'original_content': text,
            'row_id': row_id,
            'job_id': job_id
        }

def test_enhanced_classifier():
    """Test the enhanced classifier with problematic cases"""
    
    if USE_ENHANCED:
        classifier = EnhancedJobClassifier(use_ai=False)
        print("🎯 Testing Enhanced Job Classifier")
    else:
        classifier = InlineEnhancedClassifier()
        print("🎯 Testing Inline Enhanced Classifier")
    
    print("=" * 80)
    
    # Load test cases
    df = pd.read_csv('test_problematic_cases.csv')
    
    print(f"Processing {len(df)} test cases...\n")
    
    for idx, row in df.iterrows():
        job_id = row['job_id']
        text = row['job_posting_text']
        
        result = classifier.process_row(text, str(idx), str(job_id))
        
        print(f"Test Case {job_id}:")
        print(f"Input: {text[:60]}...")
        print(f"Extracted Title: {result['extracted_job_title']}")
        print(f"Category: {result['job_category']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print("-" * 40)
    
    print("🔍 Analysis of Problematic Cases:")
    print("1. Aircraft-related jobs should be 'Aviation Mechanic'")
    print("2. Location names like 'Blair Stone' should be filtered out")
    print("3. Marketing terms like 'satisfaction guaranteed' should be ignored")
    print("4. Generic terms like 'Airport' should not be job titles")
    print("5. Specific roles should be properly classified")

if __name__ == "__main__":
    test_enhanced_classifier()