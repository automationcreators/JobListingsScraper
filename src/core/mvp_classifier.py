import re
import pandas as pd
from typing import Dict, List, Tuple, Any
import logging

class MVPJobClassifier:
    """
    Simplified MVP job classification system focused on accuracy and simplicity.
    Uses code-first approach with regex patterns and keyword matching.
    """
    
    def __init__(self):
        self.job_categories = {
            'HVAC': ['hvac', 'heating', 'ventilation', 'air conditioning', 'hvac tech', 'hvac technician'],
            'Security': ['security guard', 'security', 'guard', 'safety officer', 'protection officer'],
            'Nurse': ['nurse', 'rn', 'lvn', 'lpn', 'nursing', 'registered nurse'],
            'Veterinary Assistant': ['veterinary assistant', 'vet tech', 'veterinary', 'animal hospital'],
            'Dental Assistant': ['dental assistant', 'dental hygienist', 'dental', 'dentist office'],
            'CDL': ['cdl driver', 'truck driver', 'commercial driver', 'cdl'],
            'Speech Pathology': ['speech pathology', 'speech therapist', 'slp', 'speech therapy'],
            'Aviation Mechanic': ['aviation mechanic', 'aircraft mechanic', 'airplane mechanic'],
            'Plumber': ['plumber', 'plumbing', 'pipefitter'],
            'Electrician': ['electrician', 'electrical', 'lineman', 'electrical technician'],
            'Welder': ['welder', 'welding', 'fabrication', 'fabricator', 'steel worker', 'steel fabrication'],
            'Construction': ['construction', 'construction worker', 'craftsman', 'construction project'],
            'Technician': ['technician', 'tech', 'fitter', 'machine operator', 'sprinkler technician']
        }
        
        self.experience_keywords = {
            'entry_level': ['assistant', 'aide', 'trainee', 'entry', 'junior', 'helper', 
                          'entry level', 'no experience', 'will train', 'apprentice'],
            'advanced': ['specialist', 'senior', 'supervisor', 'manager', 'lead', 
                       'experienced', 'expert', 'professional', 'certified']
        }
        
        self.license_keywords = {
            'required': ['cdl', 'license', 'certification', 'certified', 'rn', 'lvn', 
                        'lpn', 'license required', 'must have license'],
            'not_required': ['no license', 'no experience', 'will train', 'entry level',
                           'no certification needed', 'training provided']
        }
        
        self.function_keywords = {
            'Customer Support': ['customer service', 'support', 'call center', 'help desk',
                               'customer care', 'customer support'],
            'Sales/Marketing': ['sales', 'marketing', 'business development', 'account',
                              'sales rep', 'marketing coordinator'],
            'Receptionist': ['receptionist', 'front desk', 'administrative', 'office',
                           'admin assistant', 'secretary'],
            'Coding': ['developer', 'programmer', 'software', 'coding', 'it', 
                      'software engineer', 'web developer'],
            'Medical Paperwork': ['medical records', 'billing', 'coding', 'clerk', 
                                'data entry', 'medical clerk']
        }

    def extract_job_title(self, text: str) -> str:
        """Extract job title from first sentence using regex patterns"""
        if not text or pd.isna(text):
            return "No text provided"
            
        # Clean and get first sentence
        text = str(text).strip()
        first_sentence = re.split(r'[.!?]', text)[0]
        
        # Enhanced regex patterns for job title extraction
        patterns = [
            # Pattern: "X jobs for [job title]" or "X [job title] jobs"
            r'(\d+)?\s*(?:jobs?\s+(?:for\s+|available\s+for\s+)?)?([A-Za-z\s]+?)\s+(?:jobs?|positions?|openings?)',
            
            # Pattern: "[job title] positions available"
            r'([A-Za-z\s]+?)\s+(?:positions?|jobs?|openings?)\s+(?:available|needed|wanted)',
            
            # Pattern: "Hiring [job title]" or "Seeking [job title]"
            r'(?:hiring|seeking|looking\s+for)\s+([A-Za-z\s]+?)(?:\s+in\s+|\s+for\s+|\s*-|\s*$)',
            
            # Pattern: "[job title] needed/wanted/required"
            r'([A-Za-z\s]+?)\s+(?:needed|wanted|required)(?:\s+in\s+|\s+for\s+|\s*-|\s*$)',
            
            # Pattern: Direct job title at beginning
            r'^([A-Za-z\s]+?)\s+(?:-|in\s+|for\s+|available)',
            
            # Fallback: Extract first 2-4 meaningful words
            r'^([A-Za-z]+(?:\s+[A-Za-z]+){1,3})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, first_sentence, re.IGNORECASE)
            if match:
                # Get the job title group
                title_group = 2 if len(match.groups()) > 1 and match.group(2) else 1
                title = match.group(title_group).strip()
                
                # Clean the extracted title
                title = self._clean_job_title(title)
                if title and len(title) > 2:
                    return title
        
        # Final fallback: return first few meaningful words
        words = first_sentence.split()[:3]
        cleaned_words = [word for word in words if word.isalpha() and len(word) > 1]
        return ' '.join(cleaned_words[:2]) if cleaned_words else "Unable to extract"

    def _clean_job_title(self, title: str) -> str:
        """Clean extracted job title"""
        # Remove common noise words
        noise_words = ['jobs', 'job', 'positions', 'position', 'available', 'needed', 
                      'wanted', 'hiring', 'seeking', 'openings', 'opening']
        
        words = title.split()
        cleaned_words = [word for word in words if word.lower() not in noise_words]
        
        return ' '.join(cleaned_words).strip()

    def classify_job_category(self, job_title: str, full_text: str = "") -> str:
        """Classify job into predefined categories using keyword matching"""
        search_text = (job_title + " " + full_text).lower()
        
        # Track matches and their specificity
        category_scores = {}
        
        for category, keywords in self.job_categories.items():
            score = 0
            for keyword in keywords:
                if keyword in search_text:
                    # More specific keywords get higher scores
                    specificity = len(keyword.split())
                    score += specificity
            
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            # Return category with highest score
            return max(category_scores, key=category_scores.get)
        
        return 'Other'

    def determine_experience_level(self, text: str) -> str:
        """Determine experience level based on keyword matching"""
        if not text or pd.isna(text):
            return 'Not Specified'
            
        text_lower = str(text).lower()
        
        entry_score = sum(2 if keyword in text_lower else 0 
                         for keyword in self.experience_keywords['entry_level'])
        advanced_score = sum(2 if keyword in text_lower else 0 
                           for keyword in self.experience_keywords['advanced'])
        
        if entry_score > advanced_score and entry_score > 0:
            return 'Entry Level'
        elif advanced_score > 0:
            return 'Advanced'
        else:
            return 'Not Specified'

    def check_license_requirement(self, text: str) -> str:
        """Check if license/certification is required"""
        if not text or pd.isna(text):
            return 'Not Specified'
            
        text_lower = str(text).lower()
        
        required_score = sum(2 if keyword in text_lower else 0 
                           for keyword in self.license_keywords['required'])
        not_required_score = sum(2 if keyword in text_lower else 0 
                               for keyword in self.license_keywords['not_required'])
        
        if required_score > not_required_score and required_score > 0:
            return 'Required'
        elif not_required_score > 0:
            return 'Not Required'
        else:
            return 'Not Specified'

    def identify_job_function(self, text: str) -> str:
        """Identify specific job function"""
        if not text or pd.isna(text):
            return 'General'
            
        text_lower = str(text).lower()
        
        function_scores = {}
        for function, keywords in self.function_keywords.items():
            score = sum(1 if keyword in text_lower else 0 for keyword in keywords)
            if score > 0:
                function_scores[function] = score
        
        if function_scores:
            return max(function_scores, key=function_scores.get)
        
        return 'General'

    def calculate_confidence(self, text: str, job_title: str) -> float:
        """Calculate confidence score for extraction accuracy"""
        confidence = 0.3  # Base confidence
        
        if not text or not job_title:
            return 0.1
        
        # Higher confidence if common job keywords found
        text_lower = text.lower()
        job_keywords_found = any(
            keyword in text_lower 
            for keywords in self.job_categories.values() 
            for keyword in keywords
        )
        if job_keywords_found:
            confidence += 0.4
        
        # Higher confidence if job title has professional terms
        professional_terms = ['technician', 'assistant', 'specialist', 'manager', 
                             'director', 'coordinator', 'representative', 'analyst']
        if any(term in job_title.lower() for term in professional_terms):
            confidence += 0.2
        
        # Higher confidence if text structure suggests job posting
        structure_indicators = ['jobs', 'hiring', 'positions', 'experience', 'required']
        structure_score = sum(1 for indicator in structure_indicators if indicator in text_lower)
        confidence += min(structure_score * 0.1, 0.3)
        
        return min(confidence, 1.0)

    def process_row(self, text: str) -> Dict[str, Any]:
        """Process a single row of data and return classification results"""
        try:
            if not text or pd.isna(text):
                return self._error_result("Empty or invalid text")
            
            text = str(text).strip()
            if len(text) < 10:
                return self._error_result("Text too short")
            
            # Extract job title
            job_title = self.extract_job_title(text)
            
            # Perform all classifications
            result = {
                'extracted_job_title': job_title,
                'job_category': self.classify_job_category(job_title, text),
                'experience_level': self.determine_experience_level(text),
                'license_required': self.check_license_requirement(text),
                'job_function': self.identify_job_function(text),
                'confidence': self.calculate_confidence(text, job_title),
                'processing_status': 'success'
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Error processing row: {str(e)}")
            return self._error_result(f"Processing error: {str(e)}")

    def _error_result(self, error_msg: str) -> Dict[str, Any]:
        """Return standardized error result"""
        return {
            'extracted_job_title': 'Error',
            'job_category': 'Error',
            'experience_level': 'Error',
            'license_required': 'Error',
            'job_function': 'Error',
            'confidence': 0.0,
            'processing_status': 'error',
            'error_message': error_msg
        }

    def process_dataframe(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """Process entire DataFrame and add classification columns"""
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame")
        
        # Create new columns
        new_columns = ['extracted_job_title', 'job_category', 'experience_level', 
                      'license_required', 'job_function', 'confidence']
        
        # Process each row
        results = []
        for idx, row in df.iterrows():
            text = row[text_column]
            result = self.process_row(text)
            results.append(result)
        
        # Convert results to DataFrame columns
        results_df = pd.DataFrame(results)
        
        # Add new columns to original DataFrame
        for col in new_columns:
            df[col] = results_df[col]
        
        return df

    def get_processing_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate processing summary statistics"""
        total_rows = len(df)
        
        # Count by category
        category_counts = df['job_category'].value_counts().to_dict()
        
        # Count by experience level
        experience_counts = df['experience_level'].value_counts().to_dict()
        
        # Confidence statistics
        avg_confidence = df['confidence'].mean()
        low_confidence_count = len(df[df['confidence'] < 0.5])
        
        # Error statistics
        error_count = len(df[df['job_category'] == 'Error'])
        
        return {
            'total_rows_processed': total_rows,
            'successful_extractions': total_rows - error_count,
            'error_count': error_count,
            'average_confidence': round(avg_confidence, 3),
            'low_confidence_count': low_confidence_count,
            'category_distribution': category_counts,
            'experience_distribution': experience_counts,
            'processing_accuracy': round((total_rows - error_count) / total_rows * 100, 1)
        }