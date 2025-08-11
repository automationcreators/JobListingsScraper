import re
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
import logging
import json
from datetime import datetime

class EnhancedJobClassifier:
    """
    Enhanced job classification system using AI-first approach with rule-based fallback.
    Focuses on accurate job title extraction and specific category classification.
    """
    
    def __init__(self, use_ai: bool = True):
        self.use_ai = use_ai
        
        # Strict job categories mapping with synonym awareness
        self.job_categories = {
            'HVAC Technician': [
                'hvac technician', 'hvac tech', 'heating technician', 'ventilation technician',
                'air conditioning technician', 'hvac mechanic', 'hvac installer', 'hvac maintenance technician',
                'hvac repair technician', 'hvac service technician', 'hvac'
            ],
            'Security Guard': [
                'security guard', 'security officer', 'safety officer', 'protection officer',
                'security personnel', 'armed guard', 'unarmed guard', 'security'
            ],
            'Registered Nurse': [
                'registered nurse', 'rn', 'staff nurse', 'floor nurse', 'charge nurse',
                'hospital nurse', 'clinical nurse', 'nurse'
            ],
            'Licensed Practical Nurse': [
                'licensed practical nurse', 'lpn', 'lvn', 'licensed vocational nurse',
                'practical nurse'
            ],
            'Veterinary Assistant': [
                'veterinary assistant', 'vet assistant', 'veterinary technician', 'vet tech',
                'animal care assistant', 'veterinary aide', 'veterinary', 'vet'
            ],
            'Dental Assistant': [
                'dental assistant', 'dental hygienist', 'dental aide', 'orthodontic assistant',
                'oral surgery assistant', 'dental'
            ],
            'CDL Driver': [
                'cdl driver', 'truck driver', 'commercial driver', 'delivery driver',
                'transport driver', 'freight driver', 'semi driver', 'cdl'
            ],
            'Speech Pathologist': [
                'speech pathologist', 'speech therapist', 'speech language pathologist',
                'slp', 'speech therapy', 'communication disorders specialist', 'speech pathology'
            ],
            'Aviation Mechanic': [
                'aviation mechanic', 'aircraft mechanic', 'airplane mechanic', 'aircraft technician',
                'aviation technician', 'aircraft maintenance technician', 'a&p mechanic',
                'aircraft maintenance', 'aircraft inspector', 'aerospace', 'aviation', 'aircraft',
                'aircraft maintenance tech', 'aviation maintenance technician'
            ],
            'Plumber': [
                'plumber', 'pipefitter', 'plumbing technician', 'pipe installer',
                'plumbing specialist', 'journeyman plumber', 'plumbing maintenance technician',
                'plumbing repair technician', 'plumbing'
            ],
            'Electrician': [
                'electrician', 'electrical technician', 'electrical installer', 'lineman',
                'journeyman electrician', 'electrical specialist', 'power technician', 
                'electrical maintenance technician', 'electrical repair technician',
                'electronics installation & repair technician', 'electronics installation and repair technician',
                'electronics installation technician', 'electronics repair technician', 'electrical'
            ],
            'Welder': [
                'welder', 'welding technician', 'fabricator', 'welding specialist',
                'structural welder', 'pipe welder', 'arc welder', 'steel worker', 'welding'
            ],
            'Construction Worker': [
                'construction worker', 'construction laborer', 'general laborer',
                'construction helper', 'building worker', 'construction'
            ],
            'Project Manager': [
                'project manager', 'construction project manager', 'site manager',
                'construction manager', 'project coordinator'
            ],
            'Medical Assistant': [
                'medical assistant', 'medical aide', 'healthcare assistant', 'clinical assistant',
                'medical office assistant'
            ],
            'Driver': [
                'driver', 'delivery driver', 'transport driver', 'courier', 'chauffeur'
            ]
        }
        
        # Synonym mapping for maintenance/repair/technician -> mechanic equivalence
        self.synonym_mapping = {
            'maintenance': 'mechanic',
            'repair': 'mechanic', 
            'technician': 'mechanic',
            'tech': 'mechanic',
            'service': 'mechanic'
        }
        
        # Exact match keywords for the original 11 categories
        self.exact_match_keywords = [
            'hvac', 'security', 'nurse', 'veterinary assistant', 'dental assistant',
            'cdl', 'speech pathology', 'aviation mechanic', 'plumber', 'electrician', 'welder'
        ]
        
        # Address detection patterns
        self.address_patterns = [
            r'\b\d+\s+[A-Za-z\s]+(road|rd|street|st|avenue|ave|drive|dr|lane|ln|boulevard|blvd)\b',
            r'\b\d+\s+[A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5}\b',  # City, State ZIP
            r'\b[A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5}\b',  # City, State ZIP without street number
            r'\bemail:\s*[A-Za-z\s]+::\b',  # Email pattern
            r'\b\d{5}\s*::\b',  # ZIP code with ::
        ]
        
        # Common non-job-title patterns to filter out
        self.noise_patterns = [
            r'\b\d+\s*(jobs?|positions?|openings?)\b',  # "25 jobs"
            r'\bavailable\s+in\b',  # "available in"
            r'\bon\s+indeed\.com\b',  # "on indeed.com"
            r'\bapply\s+to\b',  # "apply to"
            r'\band\s+more\b',  # "and more"
            r'\bsatisfaction\s+guaranteed\b',  # company slogans
            r'\b(locations?|cities?|areas?)\b',  # location words
            r'\b(hiring|seeking|looking)\b',  # action words without context
        ]
        
        # Job title validation patterns
        self.valid_job_patterns = [
            r'\b\w+\s+(technician|tech|mechanic|specialist|assistant|aide|manager|coordinator|supervisor|director|analyst|engineer|developer|designer|operator|worker|driver|nurse|therapist|pathologist|electrician|plumber|welder|guard|officer)\b',
            r'\b(registered|licensed|certified|senior|junior|lead|head|chief)\s+\w+\b',
            r'\b\w+\s+(rn|lpn|lvn|cdl|slp|cna|emt|paramedic)\b'
        ]

    def extract_job_title_ai(self, text: str) -> Optional[str]:
        """
        Use AI to extract job title from text.
        This is a placeholder for AI integration - implement with your preferred AI service.
        """
        if not self.use_ai:
            return None
            
        # Placeholder for AI service integration
        # You would implement calls to OpenAI, Anthropic, or local LLM here
        
        # For now, return None to fall back to rule-based extraction
        return None
    
    def is_address(self, text: str) -> bool:
        """Check if text is primarily an address."""
        if not text:
            return False
            
        text = str(text).strip()
        
        # Check for address patterns
        for pattern in self.address_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def extract_job_title_rules(self, text: str) -> str:
        """
        Enhanced rule-based job title extraction with better pattern matching.
        """
        if not text or pd.isna(text):
            return "No text provided"
            
        text = str(text).strip()
        
        # Remove noise patterns first
        cleaned_text = text
        for pattern in self.noise_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        # Split into sentences and analyze each
        sentences = re.split(r'[.!?]', cleaned_text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short fragments
                continue
            
            # Enhanced extraction patterns with specific job title detection
            patterns = [
                # Pattern: Extract full job titles from complex sentences (highest priority)
                # Looks for job titles that appear after periods or at beginning and before dashes/plus signs
                r'(?:^|\.\s+)([A-Za-z\s&]+?(?:maintenance|repair|installation|technician|mechanic|pilot|specialist|manager)\s*(?:technician|mechanic|specialist|manager|pilot)?)\s*[-+]\s*[A-Z]',  # ". Aircraft Maintenance Technician - RSW"
                
                # Pattern: Extract job titles mentioned in the middle of complex job posting text
                r'([A-Z][A-Za-z\s&]*?(?:maintenance|repair|installation)\s+technicians?)\s*[-+]',  # "Aircraft Maintenance Technician - RSW"
                
                # Pattern: Specific complex job titles first 
                r'(\d+)?\s*(aircraft\s+maintenance\s+technicians?|aviation\s+maintenance\s+technicians?)\s+(?:jobs?|positions?|-)',
                r'(\d+)?\s*(electronics\s+installation\s*&?\s*repair\s+technicians?|electronics\s+installation\s+and\s+repair\s+technicians?)\s+(?:jobs?|positions?)',
                r'(\d+)?\s*(airline\s+pilots?|commercial\s+pilots?)\s+(?:jobs?|positions?)',
                r'(\d+)?\s*(hvac\s+technicians?|plumbing\s+technicians?|electrical\s+technicians?)\s+(?:jobs?|positions?)',
                r'(\d+)?\s*(aerospace\s+engineers?)\s+(?:jobs?|positions?)',
                r'(\d+)?\s*(medical\s+assistants?)\s+(?:jobs?|positions?)',
                
                # Pattern: Job titles mentioned in "Apply to X, Y, Z" sections but prioritize the main one
                r'apply\s+to\s+[^,]*?([A-Za-z\s]+?(?:officer|pilot|technician|mechanic))',
                
                # Pattern: Single word job categories (for cases like "Airport jobs", "Driver jobs") - LOWER PRIORITY
                r'(\d+)?\s*(airport|driver|security|construction|hvac|electrical|plumbing|welding|medical|dental|veterinary)\s+(?:jobs?|positions?)',
                # Note: Removed "aircraft" and "aviation" from single-word matches to prioritize full job titles
                
                # Pattern: "X [job title] positions/jobs"  
                r'(\d+)?\s*([A-Za-z\s&]+?(?:technicians?|techs?|mechanics?|specialists?|assistants?|aides?|managers?|coordinators?|supervisors?|directors?|analysts?|engineers?|developers?|designers?|operators?|workers?|drivers?|nurses?|therapists?|pathologists?|electricians?|plumbers?|welders?|guards?|officers?|pilots?))\s+(?:jobs?|positions?|openings?)',
                
                # Pattern: "[job title] needed/wanted/required"
                r'([A-Za-z\s&]+?(?:technician|tech|mechanic|specialist|assistant|aide|manager|coordinator|supervisor|director|analyst|engineer|developer|designer|operator|worker|driver|nurse|therapist|pathologist|electrician|plumber|welder|guard|officer|pilot))\s+(?:needed|wanted|required)',
                
                # Pattern: "Hiring [job title]"
                r'(?:hiring|seeking|looking\s+for)\s+([A-Za-z\s&]+?(?:technician|tech|mechanic|specialist|assistant|aide|manager|coordinator|supervisor|director|analyst|engineer|developer|designer|operator|worker|driver|nurse|therapist|pathologist|electrician|plumber|welder|guard|officer|pilot))',
                
                # Pattern: Professional licenses/certifications
                r'([A-Za-z\s]*(?:registered|licensed|certified)\s+[A-Za-z\s]*(?:nurse|technician|therapist|pathologist|assistant))',
                
                # Pattern: CDL or other specific qualifications
                r'(cdl\s+driver|truck\s+driver|commercial\s+driver)',
                
                # Pattern: Common job titles at start of sentence
                r'^([A-Za-z\s&]+?(?:technician|tech|mechanic|specialist|assistant|aide|manager|coordinator|supervisor|director|analyst|engineer|developer|designer|operator|worker|driver|nurse|therapist|pathologist|electrician|plumber|welder|guard|officer|pilot))'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    # Get the job title group (usually group 2, but handle both cases)
                    title = None
                    if len(match.groups()) >= 2 and match.group(2):
                        title = match.group(2).strip()
                    elif match.group(1):
                        title = match.group(1).strip()
                    
                    if title:
                        cleaned_title = self._clean_job_title(title)
                        if cleaned_title and len(cleaned_title) > 2:
                            # Special handling for complex job titles like "Aircraft Maintenance Technician"
                            if 'maintenance technician' in cleaned_title.lower() or 'repair technician' in cleaned_title.lower():
                                return cleaned_title  # High confidence for these patterns
                            # For single words like "Airport", don't validate as strictly
                            elif len(cleaned_title.split()) == 1 or self._validate_job_title(cleaned_title):
                                return cleaned_title
        
        # Final fallback: Look for any valid job title patterns
        for pattern in self.valid_job_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                title = match.group(0)
                cleaned_title = self._clean_job_title(title)
                if self._validate_job_title(cleaned_title):
                    return cleaned_title
        
        return "Unable to extract job title"

    def _clean_job_title(self, title: str) -> str:
        """Clean and normalize extracted job title."""
        if not title:
            return ""
            
        # Remove common noise words but preserve special characters like &
        noise_words = ['jobs', 'job', 'positions', 'position', 'available', 'needed', 
                      'wanted', 'hiring', 'seeking', 'openings', 'opening', 'apply']
        
        # Split by spaces but preserve & and other important characters
        words = title.strip().split()
        cleaned_words = []
        
        for word in words:
            # Keep special characters and valid words
            if word in ['&', 'and'] or (word.lower() not in noise_words and len(word) > 1):
                cleaned_words.append(word)
        
        result = ' '.join(cleaned_words).strip()
        
        # Capitalize properly but keep & as is
        words = result.split()
        capitalized_words = []
        for word in words:
            if word == '&':
                capitalized_words.append('&')
            else:
                capitalized_words.append(word.capitalize())
        
        return ' '.join(capitalized_words)

    def _validate_job_title(self, title: str) -> bool:
        """Validate if extracted text is likely a real job title."""
        if not title or len(title) < 3:
            return False
            
        title_lower = title.lower()
        
        # Check against known invalid patterns
        invalid_patterns = [
            r'^\d+$',  # Just numbers
            r'^[A-Z\s]+$',  # All caps (likely company/location names)
            r'\b(and|the|of|in|at|to|for|with|by)\b',  # Common connecting words
            r'\b(city|town|county|state|area|location|address)\b',  # Location words
            r'\b(company|corp|inc|llc|ltd)\b',  # Company suffixes
            r'\b(guaranteed|satisfaction|quality|service|best|top)\b'  # Marketing terms
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, title_lower):
                return False
        
        # Must contain at least one valid job-related word
        job_keywords = [
            'technician', 'tech', 'mechanic', 'specialist', 'assistant', 'aide',
            'manager', 'coordinator', 'supervisor', 'director', 'analyst',
            'engineer', 'developer', 'designer', 'operator', 'worker',
            'driver', 'nurse', 'therapist', 'pathologist', 'electrician',
            'plumber', 'welder', 'guard', 'officer', 'clerk', 'representative',
            'pilot'  # Add pilot to valid keywords
        ]
        
        return any(keyword in title_lower for keyword in job_keywords)

    def extract_job_title(self, text: str) -> str:
        """
        Main job title extraction method - tries AI first, falls back to rules.
        """
        # Try AI extraction first
        if self.use_ai:
            ai_result = self.extract_job_title_ai(text)
            if ai_result and ai_result != "Unable to extract job title":
                return ai_result
        
        # Fall back to rule-based extraction
        return self.extract_job_title_rules(text)

    def classify_general_category(self, job_title: str, job_category: str, full_text: str = "") -> str:
        """
        Classify into general categories: 'exact', 'general', or 'other'
        """
        if not job_title or job_title == "Unable to extract job title":
            return 'other'
        
        search_text = (job_title + " " + full_text).lower()
        
        # Check for exact matches with original 11 categories first
        exact_category_matches = {
            'hvac': ['hvac technician', 'hvac', 'hvac mechanic', 'hvac maintenance technician'],
            'security': ['security guard', 'security'],
            'nurse': ['registered nurse', 'licensed practical nurse'],
            'veterinary assistant': ['veterinary assistant'],
            'dental assistant': ['dental assistant'],
            'cdl': ['cdl driver'],  # Only CDL drivers are exact
            'speech pathology': ['speech pathologist'],
            'aviation mechanic': ['aviation mechanic', 'aircraft mechanic', 'aircraft maintenance technician', 'aviation maintenance technician'],
            'plumber': ['plumber', 'plumbing technician', 'plumbing maintenance technician'],
            'electrician': ['electrician', 'electrical technician', 'electronics installation & repair technician', 'electronics installation and repair technician'],
            'welder': ['welder', 'welding technician']
        }
        
        for category, variations in exact_category_matches.items():
            if any(variation in search_text for variation in variations):
                return 'exact'
        
        # Special cases that are "other" (not exact matches)
        other_categories = [
            'airline pilot', 'medical assistant', 'electronics technician', 
            'address', 'project manager'
        ]
        
        if job_category.lower() in [cat.lower() for cat in other_categories]:
            return 'other'
        
        # Driver without CDL is general (check job_category not search_text to avoid "no cdl" issue)
        if job_category == 'Driver':
            return 'general'
        
        # Check if it fits in general categories
        general_indicators = [
            'technician', 'mechanic', 'worker', 'assistant', 'specialist',
            'manager', 'coordinator', 'supervisor', 'operator', 'installer'
        ]
        
        # If it contains general job function words and isn't in other categories
        if any(indicator in search_text for indicator in general_indicators):
            return 'general'
        
        return 'other'
    
    def classify_job_category(self, job_title: str, full_text: str = "") -> str:
        """Enhanced job classification with strict rules and context awareness."""
        if not job_title or job_title == "Unable to extract job title":
            return 'Unable to Classify'
            
        search_text = (job_title + " " + full_text).lower()
        job_title_lower = job_title.lower()
        
        # Strict classification rules based on your requirements
        
        # 1. Aircraft-related jobs -> Aviation Mechanic
        if any(term in job_title_lower for term in ['aircraft', 'aviation', 'aerospace', 'airplane']):
            return 'Aviation Mechanic'
        
        # 2. Airlines/Pilot jobs -> Aviation Mechanic (not Airline Pilot category)
        if any(term in job_title_lower for term in ['airline pilot', 'pilot', 'first officer', 'captain']):
            return 'Aviation Mechanic'
        
        # 3. Electronics installation & repair -> Electrician (exact match requirement)
        if 'electronics' in job_title_lower and ('installation' in job_title_lower or 'repair' in job_title_lower):
            return 'Electrician'
        
        # 4. Any technician/maintenance/repair with specific trades -> exact match
        if 'hvac' in job_title_lower:
            return 'HVAC Technician'
        elif any(term in job_title_lower for term in ['plumbing', 'plumber', 'pipe']):
            return 'Plumber'
        elif any(term in job_title_lower for term in ['electrical', 'electrician']):
            return 'Electrician'
        elif any(term in job_title_lower for term in ['welding', 'welder']):
            return 'Welder'
        
        # 5. Special handling for driver categories
        if 'driver' in search_text:
            if ('cdl' in search_text and 'no cdl' not in search_text) or 'truck driver' in search_text or 'commercial driver' in search_text:
                return 'CDL Driver'
            else:
                return 'Driver'
        
        # 6. Airport jobs -> Aviation Mechanic
        if job_title_lower == 'airport':
            return 'Aviation Mechanic'
        
        # 7. General category matching with strict scoring
        best_match = None
        best_score = 0
        
        for category, keywords in self.job_categories.items():
            # Skip categories we've already handled
            if category in ['CDL Driver', 'Driver']:
                continue
                
            score = 0
            for keyword in keywords:
                if keyword in search_text:
                    # Exact matches get highest priority
                    if keyword == job_title_lower:
                        score += 100
                    else:
                        # Weight longer, more specific keywords higher
                        keyword_specificity = len(keyword.split()) * 2
                        score += keyword_specificity
            
            if score > best_score:
                best_score = score
                best_match = category
        
        return best_match if best_match else 'Other'

    def calculate_confidence(self, text: str, job_title: str, category: str) -> float:
        """Calculate confidence score based on extraction and classification quality."""
        confidence = 0.3  # Base confidence
        
        if not text or not job_title:
            return 0.1
        
        # Higher confidence for validated job titles
        if self._validate_job_title(job_title):
            confidence += 0.3
        
        # Higher confidence if category is specific (not 'Other')
        if category != 'Other' and category != 'Unable to Classify':
            confidence += 0.2
        
        # Higher confidence if job title contains professional terms
        professional_terms = ['technician', 'specialist', 'manager', 'director', 
                             'registered', 'licensed', 'certified']
        if any(term in job_title.lower() for term in professional_terms):
            confidence += 0.1
        
        # Lower confidence if extraction failed
        if job_title == "Unable to extract job title":
            confidence = 0.1
        
        return min(confidence, 1.0)

    def process_row(self, text: str, row_id: Optional[str] = None, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a single row and return enhanced classification results."""
        try:
            if not text or pd.isna(text):
                return self._error_result("Empty or invalid text", text, row_id, job_id)
            
            text = str(text).strip()
            if len(text) < 10:
                return self._error_result("Text too short", text, row_id, job_id)
            
            # Check if text is primarily an address
            if self.is_address(text):
                result = {
                    'extracted_job_title': 'Address',
                    'job_category': 'Address',
                    'general_category': 'other',
                    'confidence': 0.9,
                    'original_content': text,
                    'processing_status': 'success',
                    'extraction_method': 'address_detection'
                }
            else:
                # Extract job title
                job_title = self.extract_job_title(text)
                
                # Classify job category
                category = self.classify_job_category(job_title, text)
                
                # Classify general category
                general_category = self.classify_general_category(job_title, category, text)
                
                # Calculate confidence
                confidence = self.calculate_confidence(text, job_title, category)
                
                result = {
                    'extracted_job_title': job_title,
                    'job_category': category,
                    'general_category': general_category,
                    'confidence': confidence,
                    'original_content': text,
                    'processing_status': 'success',
                    'extraction_method': 'ai' if self.use_ai else 'rules'
                }
            
            # Add identifiers if provided
            if row_id is not None:
                result['row_id'] = row_id
            if job_id is not None:
                result['job_id'] = job_id
                
            return result
            
        except Exception as e:
            logging.error(f"Error processing row: {str(e)}")
            return self._error_result(f"Processing error: {str(e)}", text, row_id, job_id)

    def _error_result(self, error_msg: str, original_text: str = "", 
                     row_id: Optional[str] = None, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Return standardized error result."""
        result = {
            'extracted_job_title': 'Error',
            'job_category': 'Error',
            'general_category': 'other',
            'confidence': 0.0,
            'original_content': original_text,
            'processing_status': 'error',
            'error_message': error_msg,
            'extraction_method': 'error'
        }
        
        if row_id is not None:
            result['row_id'] = row_id
        if job_id is not None:
            result['job_id'] = job_id
            
        return result

    def process_dataframe(self, df: pd.DataFrame, text_column: str, 
                         job_id_column: Optional[str] = None) -> pd.DataFrame:
        """Process entire DataFrame with enhanced tracking."""
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame")
        
        results = []
        
        for idx, row in df.iterrows():
            text = row[text_column]
            row_id = str(idx)  # Use DataFrame index as row ID
            job_id = str(row[job_id_column]) if job_id_column and job_id_column in df.columns else None
            
            result = self.process_row(text, row_id, job_id)
            results.append(result)
        
        # Convert results to DataFrame columns
        results_df = pd.DataFrame(results)
        
        # Add new columns to original DataFrame
        output_columns = ['extracted_job_title', 'job_category', 'general_category', 'confidence', 
                         'original_content', 'row_id']
        if job_id_column:
            output_columns.append('job_id')
            
        for col in output_columns:
            if col in results_df.columns:
                df[col] = results_df[col]
        
        return df

    def get_processing_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate enhanced processing summary."""
        total_rows = len(df)
        
        # Count by category
        category_counts = df['job_category'].value_counts().to_dict()
        
        # Confidence statistics
        avg_confidence = df['confidence'].mean()
        low_confidence_count = len(df[df['confidence'] < 0.5])
        high_confidence_count = len(df[df['confidence'] >= 0.7])
        
        # Error statistics
        error_count = len(df[df['job_category'] == 'Error'])
        unable_to_extract = len(df[df['extracted_job_title'] == 'Unable to extract job title'])
        
        return {
            'total_rows_processed': total_rows,
            'successful_extractions': total_rows - error_count,
            'error_count': error_count,
            'unable_to_extract_count': unable_to_extract,
            'average_confidence': round(avg_confidence, 3),
            'low_confidence_count': low_confidence_count,
            'high_confidence_count': high_confidence_count,
            'category_distribution': category_counts,
            'processing_accuracy': round((total_rows - error_count) / total_rows * 100, 1),
            'extraction_quality': round((total_rows - error_count - unable_to_extract) / total_rows * 100, 1)
        }