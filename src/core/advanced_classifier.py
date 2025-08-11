import re
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
import logging
import json
from datetime import datetime

class AdvancedJobClassifier:
    """
    Advanced job classification system with first-sentence priority, context awareness,
    and detailed job list extraction from Apply to sections.
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
                'aircraft maintenance tech', 'aviation maintenance technician', 'aircraft parts',
                'aircraft detailing', 'aircraft cleaner', 'aerospace technician'
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
            ]
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

    def extract_job_title_rules(self, text: str) -> str:
        """
        Enhanced rule-based job title extraction with first-sentence priority and context awareness.
        """
        if not text or pd.isna(text):
            return "No text provided"
            
        text = str(text).strip()
        
        # Split into sentences for analysis
        sentences = text.split('.')
        first_sentence = sentences[0].strip() if sentences else text
        
        # PRIORITY 1: Check for new structure with job quantity later and specific job title FIRST
        # This pattern: "general jobs in location. NUMBER+ jobs. Specific Job Title."
        later_job_title = self._extract_from_quantity_later_structure(text)
        if later_job_title and later_job_title != "Unable to extract job title":
            return later_job_title
        
        # PRIORITY 2: Extract from first sentence - typically "NUMBER JOB TITLE jobs"
        first_sentence_title = self._extract_from_first_sentence(first_sentence)
        if first_sentence_title and first_sentence_title != "Unable to extract job title":
            return first_sentence_title
        
        # PRIORITY 3: Check if this is a "Apply to..." format where we should ignore the list
        apply_to_section = self._extract_apply_to_section(text)
        if apply_to_section and len(apply_to_section) >= 2:  # Has job list
            # If there's a job list, use the first sentence job title or fallback to generic
            if first_sentence_title and first_sentence_title != "Unable to extract job title":
                return first_sentence_title
            else:
                # Extract generic job category from first sentence
                generic_title = self._extract_generic_from_first_sentence(first_sentence)
                if generic_title:
                    return generic_title
        
        # PRIORITY 3: Standard extraction for other formats
        return self._extract_standard_patterns(text)
    
    def _extract_from_first_sentence(self, sentence: str) -> str:
        """Extract job title from first sentence with priority patterns."""
        if not sentence:
            return "Unable to extract job title"
        
        sentence = sentence.strip()
        
        # Enhanced patterns for different job posting structures
        patterns = [
            # PRIORITY 1: Number-starting patterns (existing)
            # "76 CHANDLER, AZ AIRCRAFT PARTS jobs" -> "Aircraft Parts" - specific location pattern
            r'^\d+\s+[A-Z\s,]+?,\s*[A-Z]{2}\s+([A-Z][A-Za-z\s&]+?)\s+jobs?',
            
            # "345 Aircraft Detailing jobs available" -> "Aircraft Detailing" 
            r'^\d+\s+([A-Z][A-Za-z\s&]+?)\s+jobs?\s+available',
            
            # "116 Aircraft jobs available" -> "Aircraft" 
            r'^\d+\s+([A-Z][A-Za-z\s&]*?)\s+jobs?\s+available',
            
            # "NUMBER JOB TITLE jobs" (simple case without location)
            r'^\d+\s+([A-Z][A-Za-z\s&]+?)\s+jobs?(?:\s+from|\s*$)',
            
            # PRIORITY 2: Non-number starting patterns with job titles first
            # "Aviation Safety Inspector jobs in Georgia" -> "Aviation Safety Inspector"
            r'^([A-Z][A-Za-z\s&]+?)\s+jobs?\s+in\s+[A-Za-z\s,]+',
            
            # "Air Conditioning Technician jobs in location" -> "Air Conditioning Technician"  
            r'^([A-Z][A-Za-z\s&]+?)\s+jobs?\s+in\s+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                cleaned_title = self._clean_job_title(title)
                if cleaned_title and len(cleaned_title.split()) >= 1:  # Allow single words from first sentence
                    return cleaned_title
        
        return "Unable to extract job title"
    
    def _extract_from_quantity_later_structure(self, text: str) -> str:
        """Extract job title from structure where quantity appears later: 'job type jobs in location. ##+ jobs. Specific Job Title.'"""
        if not text:
            return "Unable to extract job title"
        
        # Look for pattern: "general jobs in location. NUMBER+ jobs. Specific Job Title."
        # Example: "apprenticeship jobs in el mirage, az. 50+ jobs. Air Conditioning Technician & Apprentices."
        
        # Split by periods to get sentences
        sentences = text.split('.')
        if len(sentences) < 3:
            return "Unable to extract job title"
        
        first_sentence = sentences[0].strip()
        second_sentence = sentences[1].strip()
        third_sentence = sentences[2].strip()
        
        # Check if this matches the pattern
        # First sentence: "general jobs in location"
        # Second sentence: "NUMBER+ jobs"  
        # Third sentence: "Specific Job Title"
        
        # First pattern should match GENERIC job types, not specific job titles
        first_pattern = r'^(?:apprenticeship|training|general|entry.level|part.time|full.time|temporary|contract|internship|student|graduate|junior|senior|experienced|new|open|available|heating|cooling|plumbing|electrical|construction|maintenance|repair|installation)\s+jobs?\s+in\s+[A-Za-z\s,]+'
        second_pattern = r'^\d+\+?\s+jobs?'
        third_pattern = r'^([^\.]+)'  # Everything until period or end of string
        
        if (re.match(first_pattern, first_sentence, re.IGNORECASE) and 
            re.match(second_pattern, second_sentence, re.IGNORECASE) and
            len(third_sentence) > 0):
            
            # Extract job title from third sentence
            match = re.match(third_pattern, third_sentence)
            if match:
                title = match.group(1).strip()
                cleaned_title = self._clean_job_title(title)
                if cleaned_title and len(cleaned_title) > 2:
                    return cleaned_title
        
        # Alternative pattern: "Specific Job Title jobs in location. NUMBER+ jobs. [Other info]"
        # Example: "Aviation Safety Inspector jobs in Georgia. 100+ jobs. Aircraft Interior Installer."
        # For this pattern, we want the job title from the FIRST sentence, not the third
        alt_first_pattern = r'^([A-Z][A-Za-z\s&]+?)\s+jobs?\s+in\s+[A-Za-z\s,]+'
        
        if (len(sentences) >= 2 and 
            re.match(alt_first_pattern, first_sentence, re.IGNORECASE) and 
            re.match(second_pattern, second_sentence, re.IGNORECASE)):
            match = re.match(alt_first_pattern, first_sentence, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                cleaned_title = self._clean_job_title(title)
                if cleaned_title and len(cleaned_title) > 2:
                    return cleaned_title
        
        return "Unable to extract job title"
    
    def _extract_generic_from_first_sentence(self, sentence: str) -> str:
        """Extract generic job category when specific title not found."""
        if not sentence:
            return "Unable to extract job title"
            
        # Look for broad categories in first sentence
        generic_patterns = [
            r'aircraft|aviation|aerospace',
            r'medical|healthcare', 
            r'construction|building',
            r'electrical|electronics',
            r'hvac|heating|ventilation',
            r'plumbing|pipe',
            r'security|safety',
            r'driver|transport|delivery'
        ]
        
        for pattern in generic_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    return match.group(0).capitalize()
        
        return "Unable to extract job title"
    
    def _extract_apply_to_section(self, text: str) -> list:
        """Extract job titles from 'Apply to...' sections."""
        # Pattern: "Apply to Job1, Job2, Job3 and more!"
        apply_pattern = r'apply\s+to\s+([^!.]+?)(?:\s+and\s+more)?[!.]'
        match = re.search(apply_pattern, text, re.IGNORECASE)
        
        if match:
            jobs_text = match.group(1)
            # Split by commas and clean
            job_list = []
            for job in jobs_text.split(','):
                job = job.strip()
                if job and len(job) > 2 and not re.match(r'^\d+$', job):  # Skip numbers
                    job_list.append(job)
            return job_list
        
        return []
    
    def _extract_standard_patterns(self, text: str) -> str:
        """Standard extraction patterns for other text formats."""
        # Standard extraction patterns
        patterns = [
            # Pattern: Extract full job titles from complex sentences
            r'(?:^|\.s+)([A-Za-z\s&]+?(?:maintenance|repair|installation|technician|mechanic|pilot|specialist|manager)\s*(?:technician|mechanic|specialist|manager|pilot)?)\s*[-+]\s*[A-Z]',
            
            # Pattern: Extract job titles mentioned in the middle
            r'([A-Z][A-Za-z\s&]*?(?:maintenance|repair|installation)\s+technicians?)\s*[-+]',
            
            # Pattern: Professional job titles
            r'(\d+)?\s*([A-Za-z\s&]+?(?:technicians?|mechanics?|specialists?|assistants?|managers?|coordinators?|supervisors?|directors?|analysts?|engineers?|developers?|designers?|operators?|workers?|drivers?|nurses?|therapists?|pathologists?|electricians?|plumbers?|welders?|guards?|officers?|pilots?))\s+(?:jobs?|positions?|openings?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Get the job title group
                title = None
                if len(match.groups()) >= 2 and match.group(2):
                    title = match.group(2).strip()
                elif match.group(1):
                    title = match.group(1).strip()
                
                if title:
                    cleaned_title = self._clean_job_title(title)
                    if cleaned_title and len(cleaned_title) > 2:
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
        
        # Capitalize properly but keep & as is and preserve HVAC
        words = result.split()
        capitalized_words = []
        for word in words:
            if word == '&':
                capitalized_words.append('&')
            elif word.lower() == 'hvac':
                capitalized_words.append('HVAC')
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
        
        # Must contain at least one valid job-related word OR be from first sentence
        job_keywords = [
            'technician', 'tech', 'mechanic', 'specialist', 'assistant', 'aide',
            'manager', 'coordinator', 'supervisor', 'director', 'analyst',
            'engineer', 'developer', 'designer', 'operator', 'worker',
            'driver', 'nurse', 'therapist', 'pathologist', 'electrician',
            'plumber', 'welder', 'guard', 'officer', 'clerk', 'representative',
            'pilot', 'parts', 'detailing', 'cleaner'  # Add more aviation-related keywords
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

    def extract_job_title_ai(self, text: str) -> Optional[str]:
        """
        Use AI to extract job title from text.
        This is a placeholder for AI integration - implement with your preferred AI service.
        """
        if not self.use_ai:
            return None
            
        # Placeholder for AI service integration
        return None

    def classify_job_category(self, job_title: str, full_text: str = "") -> str:
        """Enhanced job classification with strict rules and context awareness."""
        if not job_title or job_title == "Unable to extract job title":
            return 'Unable to Classify'
            
        search_text = (job_title + " " + full_text).lower()
        job_title_lower = job_title.lower()
        
        # Strict classification rules based on requirements
        
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
        if 'hvac' in job_title_lower or 'air conditioning' in job_title_lower:
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

    def classify_general_category(self, job_title: str, job_category: str, full_text: str = "", job_details: list = []) -> str:
        """
        Classify into general categories: 'exact', 'general', or 'other' using context from job details
        """
        if not job_title or job_title == "Unable to extract job title":
            return 'other'
        
        search_text = (job_title + " " + full_text).lower()
        
        # Use job details list to help determine classification
        context_keywords = []
        if job_details:
            context_text = " ".join(job_details).lower()
            context_keywords.extend(['technician', 'mechanic', 'specialist', 'assistant', 'maintenance', 'repair'])
            
        # Check for exact matches with original 11 categories first
        exact_category_matches = {
            'hvac': ['hvac technician', 'hvac', 'hvac mechanic', 'hvac maintenance technician', 'air conditioning technician'],
            'security': ['security guard', 'security'],
            'nurse': ['registered nurse', 'licensed practical nurse'],
            'veterinary assistant': ['veterinary assistant'],
            'dental assistant': ['dental assistant'],
            'cdl': ['cdl driver'],  # Only CDL drivers are exact
            'speech pathology': ['speech pathologist'],
            'aviation mechanic': ['aviation mechanic', 'aircraft mechanic', 'aircraft maintenance technician', 'aviation maintenance technician', 'aircraft parts', 'aircraft detailing', 'aviation safety inspector'],
            'plumber': ['plumber', 'plumbing technician', 'plumbing maintenance technician'],
            'electrician': ['electrician', 'electrical technician', 'electronics installation & repair technician', 'electronics installation and repair technician'],
            'welder': ['welder', 'welding technician']
        }
        
        for category, variations in exact_category_matches.items():
            if any(variation in search_text for variation in variations):
                return 'exact'
        
        # Special handling for generic terms like "Aircraft", "Airport"
        generic_terms = ['aircraft', 'airport', 'aviation', 'aerospace']
        if job_title.lower().strip() in generic_terms:
            return 'general'
        
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
                             'registered', 'licensed', 'certified', 'parts', 'detailing']
        if any(term in job_title.lower() for term in professional_terms):
            confidence += 0.1
        
        # Lower confidence if extraction failed
        if job_title == "Unable to extract job title":
            confidence = 0.1
        
        return min(confidence, 1.0)

    def is_address(self, text: str) -> bool:
        """Check if text is primarily an address, considering job posting context."""
        if not text:
            return False
            
        text = str(text).strip()
        
        # Job posting context indicators - if these are present, it's NOT just an address
        job_posting_indicators = [
            r'\bjobs?\s+available\s+in\b',  # "jobs available in"
            r'\bjobs?\s+in\b',  # "jobs in"
            r'\bpositions?\s+available\s+in\b',  # "positions available in"
            r'\bpositions?\s+in\b',  # "positions in"
            r'\bhiring\s+in\b',  # "hiring in"
            r'\bopportunities\s+in\b',  # "opportunities in"
            r'\bapply\s+to\b',  # Contains "apply to"
            r'\bon\s+indeed\.com\b',  # On job sites
            r'\bmissing:\s*\d+[A-Z]+\b',  # Missing location codes
            r'\bshow\s+results\s+with\b'  # Show results with
        ]
        
        # If text contains job posting indicators, it's NOT just an address
        for indicator in job_posting_indicators:
            if re.search(indicator, text, re.IGNORECASE):
                return False
        
        # Additional check: if text contains numbers followed by job-related terms, it's not an address
        job_quantity_patterns = [
            r'\b\d+\s+[A-Za-z\s]*?(?:jobs?|positions?|openings?)\b',  # "185 Airport jobs"
            r'\b\d+\s+[A-Za-z\s]*?(?:technician|mechanic|specialist|assistant|manager|pilot|driver)\b'
        ]
        
        for pattern in job_quantity_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        # Now check for address patterns only if no job context was found
        address_match_count = 0
        for pattern in self.address_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                address_match_count += 1
        
        # Require multiple address pattern matches OR specific standalone address patterns
        # to avoid false positives from job postings that mention locations
        standalone_address_patterns = [
            r'^\d+\s+[A-Za-z\s]+(road|rd|street|st|avenue|ave|drive|dr|lane|ln|boulevard|blvd)',  # Starts with street address
            r'\bemail:\s*[A-Za-z\s]+::\b',  # Email pattern
            r'^\d{5}\s*::\b'  # Starts with ZIP code
        ]
        
        # Check for standalone address patterns (high confidence)
        for pattern in standalone_address_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Special check for email/contact patterns
        if re.search(r'\bemail:\s*[A-Za-z\s:]+::\b', text, re.IGNORECASE) or re.search(r'\d{5}\s*::\b', text, re.IGNORECASE):
            return True
        
        # For other patterns, require the text to be short and primarily address-focused
        if address_match_count > 0 and len(text) < 100 and not re.search(r'\b(?:job|position|work|career|employment|hiring|apply)\b', text, re.IGNORECASE):
            return True
        
        return False

    def extract_job_count(self, text: str) -> str:
        """Extract the total number of job listings from text."""
        if not text or pd.isna(text):
            return ""
        
        text = str(text).strip()
        
        # Check if this is an address first
        if self.is_address(text):
            return ""
        
        # Pattern 1: Numbers with + (like "50+ jobs", "100+ jobs")
        plus_pattern = r'(\d+)\+\s+jobs?'
        plus_match = re.search(plus_pattern, text, re.IGNORECASE)
        if plus_match:
            return plus_match.group(1)
        
        # Pattern 2: First number in text if not an address and reasonable job count
        first_number_pattern = r'^(\d+)\s+'
        first_match = re.match(first_number_pattern, text)
        if first_match:
            number = int(first_match.group(1))
            # Reasonable job count range (1-10000)
            if 1 <= number <= 10000:
                return str(number)
        
        # Pattern 3: Numbers followed by job-related words
        job_count_pattern = r'(\d+)\s+(?:job|position|opening|vacancy|role)s?\s+(?:available|posted|found|listed|in\s+)'
        job_match = re.search(job_count_pattern, text, re.IGNORECASE)
        if job_match:
            return job_match.group(1)
        
        return ""

    def extract_city(self, text: str) -> str:
        """Extract city name from location patterns in text."""
        if not text or pd.isna(text):
            return ""
        
        text = str(text).strip()
        
        # Check if this is an address first
        if self.is_address(text):
            return ""
        
        # Pattern 1: "jobs available in CITY, STATE" or "jobs in CITY, STATE"
        available_pattern = r'jobs?\s+(?:available\s+)?in\s+([A-Za-z\s]{2,30}),\s*([A-Za-z]+)(?:\s+on|\s+at|\s|$)'
        available_match = re.search(available_pattern, text, re.IGNORECASE)
        if available_match:
            city = available_match.group(1).strip()
            # Clean up city name (remove extra spaces, capitalize properly)
            return self._clean_city_name(city)
        
        # Pattern 2: After number at start, look for city pattern "NUMBER CITY, STATE DESCRIPTION"
        # Examples: "47 BUCKEYE, AZ AIRCRAFT", "76 CHANDLER, AZ AIRCRAFT PARTS", "33 FLAGSTAFF, AZ AIRCRAFT"
        number_city_pattern = r'^\d+\s+([A-Z][A-Za-z\s]{1,25}),\s*([A-Z]{2})\s+'
        number_match = re.match(number_city_pattern, text)
        if number_match:
            city = number_match.group(1).strip()
            state = number_match.group(2).strip()
            # Validate that the state is actually a valid US state
            if self._is_valid_state(state):
                return self._clean_city_name(city)
        
        # Pattern 3: General city, state pattern "CITY, STATE" 
        general_pattern = r'\b([A-Za-z\s]{2,30}),\s*([A-Za-z\s]{2,20})\b'
        general_matches = re.findall(general_pattern, text, re.IGNORECASE)
        
        if general_matches:
            # Take the first match that looks like a real city (not all caps, reasonable length)
            for city, state in general_matches:
                city = city.strip()
                state = state.strip()
                if (len(city.split()) <= 3 and  # City is 1-3 words
                    not city.isupper() and  # Not all caps (avoids company names)
                    len(city) >= 2 and  # At least 2 characters
                    self._is_valid_state(state)):  # Valid state
                    return self._clean_city_name(city)
        
        # Pattern 4: "services in CITY, STATE" or similar non-job patterns
        # Example: "services in Port St. Lucie, FL"
        services_pattern = r'\b(?:services?|work|business)\s+in\s+([A-Za-z\s\.]{2,30}),\s*([A-Z]{2})\b'
        services_match = re.search(services_pattern, text, re.IGNORECASE)
        if services_match:
            city = services_match.group(1).strip()
            state = services_match.group(2).strip()
            if self._is_valid_state(state):
                return self._clean_city_name(city)

        # Pattern 5: Single location that might be a state (handle as no city)
        single_location_pattern = r'jobs?\s+(?:available\s+)?in\s+([A-Za-z\s]{2,20})\b'
        single_match = re.search(single_location_pattern, text, re.IGNORECASE)
        if single_match:
            location = single_match.group(1).strip()
            # If it's a valid state, don't return it as city
            if self._is_valid_state(location):
                return ""
            # Otherwise, it might be a city without state
            return self._clean_city_name(location)
        
        return ""

    def extract_state(self, text: str) -> str:
        """Extract state name or abbreviation from location patterns in text."""
        if not text or pd.isna(text):
            return ""
        
        text = str(text).strip()
        
        # Check if this is an address first
        if self.is_address(text):
            return ""
        
        # Pattern 1: "jobs available in CITY, STATE" or "jobs in CITY, STATE"
        available_pattern = r'jobs?\s+(?:available\s+)?in\s+([A-Za-z\s]{2,30}),\s*([A-Za-z]+)(?:\s+on|\s+at|\s|$)'
        available_match = re.search(available_pattern, text, re.IGNORECASE)
        if available_match:
            state = available_match.group(2).strip()
            return self._normalize_state(state)
        
        # Pattern 2: After number at start, look for state pattern "NUMBER CITY, STATE DESCRIPTION"
        # Examples: "47 BUCKEYE, AZ AIRCRAFT", "76 CHANDLER, AZ AIRCRAFT PARTS", "33 FLAGSTAFF, AZ AIRCRAFT"
        number_city_pattern = r'^\d+\s+([A-Z][A-Za-z\s]{1,25}),\s*([A-Z]{2})\s+'
        number_match = re.match(number_city_pattern, text)
        if number_match:
            state = number_match.group(2).strip()
            # Validate that the state is actually a valid US state
            if self._is_valid_state(state):
                return self._normalize_state(state)
        
        # Pattern 3: General city, state pattern "CITY, STATE" 
        general_pattern = r'\b([A-Za-z\s]{2,30}),\s*([A-Za-z\s]{2,20})\b'
        general_matches = re.findall(general_pattern, text, re.IGNORECASE)
        
        if general_matches:
            # Take the first match with a valid state
            for city, state in general_matches:
                state = state.strip()
                if self._is_valid_state(state):
                    return self._normalize_state(state)
        
        # Pattern 4: "services in CITY, STATE" or similar non-job patterns
        # Example: "services in Port St. Lucie, FL"
        services_pattern = r'\b(?:services?|work|business)\s+in\s+([A-Za-z\s\.]{2,30}),\s*([A-Z]{2})\b'
        services_match = re.search(services_pattern, text, re.IGNORECASE)
        if services_match:
            state = services_match.group(2).strip()
            if self._is_valid_state(state):
                return self._normalize_state(state)

        # Pattern 5: Single location that is a state
        single_location_pattern = r'jobs?\s+(?:available\s+)?in\s+([A-Za-z\s]{2,20})\b'
        single_match = re.search(single_location_pattern, text, re.IGNORECASE)
        if single_match:
            location = single_match.group(1).strip()
            # If it's a valid state, return it normalized
            if self._is_valid_state(location):
                return self._normalize_state(location)
        
        return ""

    def _clean_city_name(self, city: str) -> str:
        """Clean and normalize city name."""
        if not city:
            return ""
        
        # Remove extra whitespace and capitalize properly
        words = city.strip().split()
        cleaned_words = []
        
        for word in words:
            # Skip empty words
            if not word:
                continue
                
            # Capitalize each word properly
            cleaned_words.append(word.capitalize())
        
        return ' '.join(cleaned_words)

    def _normalize_state(self, state: str) -> str:
        """Normalize state name to standard abbreviation."""
        if not state:
            return ""
        
        state = state.strip().upper()
        
        # State abbreviations mapping
        state_mapping = {
            'AL': 'AL', 'ALABAMA': 'AL',
            'AK': 'AK', 'ALASKA': 'AK', 
            'AZ': 'AZ', 'ARIZONA': 'AZ',
            'AR': 'AR', 'ARKANSAS': 'AR',
            'CA': 'CA', 'CALIFORNIA': 'CA',
            'CO': 'CO', 'COLORADO': 'CO',
            'CT': 'CT', 'CONNECTICUT': 'CT',
            'DE': 'DE', 'DELAWARE': 'DE',
            'FL': 'FL', 'FLORIDA': 'FL',
            'GA': 'GA', 'GEORGIA': 'GA',
            'HI': 'HI', 'HAWAII': 'HI',
            'ID': 'ID', 'IDAHO': 'ID',
            'IL': 'IL', 'ILLINOIS': 'IL',
            'IN': 'IN', 'INDIANA': 'IN',
            'IA': 'IA', 'IOWA': 'IA',
            'KS': 'KS', 'KANSAS': 'KS',
            'KY': 'KY', 'KENTUCKY': 'KY',
            'LA': 'LA', 'LOUISIANA': 'LA',
            'ME': 'ME', 'MAINE': 'ME',
            'MD': 'MD', 'MARYLAND': 'MD',
            'MA': 'MA', 'MASSACHUSETTS': 'MA',
            'MI': 'MI', 'MICHIGAN': 'MI',
            'MN': 'MN', 'MINNESOTA': 'MN',
            'MS': 'MS', 'MISSISSIPPI': 'MS',
            'MO': 'MO', 'MISSOURI': 'MO',
            'MT': 'MT', 'MONTANA': 'MT',
            'NE': 'NE', 'NEBRASKA': 'NE',
            'NV': 'NV', 'NEVADA': 'NV',
            'NH': 'NH', 'NEW HAMPSHIRE': 'NH',
            'NJ': 'NJ', 'NEW JERSEY': 'NJ',
            'NM': 'NM', 'NEW MEXICO': 'NM',
            'NY': 'NY', 'NEW YORK': 'NY',
            'NC': 'NC', 'NORTH CAROLINA': 'NC',
            'ND': 'ND', 'NORTH DAKOTA': 'ND',
            'OH': 'OH', 'OHIO': 'OH',
            'OK': 'OK', 'OKLAHOMA': 'OK',
            'OR': 'OR', 'OREGON': 'OR',
            'PA': 'PA', 'PENNSYLVANIA': 'PA',
            'RI': 'RI', 'RHODE ISLAND': 'RI',
            'SC': 'SC', 'SOUTH CAROLINA': 'SC',
            'SD': 'SD', 'SOUTH DAKOTA': 'SD',
            'TN': 'TN', 'TENNESSEE': 'TN',
            'TX': 'TX', 'TEXAS': 'TX',
            'UT': 'UT', 'UTAH': 'UT',
            'VT': 'VT', 'VERMONT': 'VT',
            'VA': 'VA', 'VIRGINIA': 'VA',
            'WA': 'WA', 'WASHINGTON': 'WA',
            'WV': 'WV', 'WEST VIRGINIA': 'WV',
            'WI': 'WI', 'WISCONSIN': 'WI',
            'WY': 'WY', 'WYOMING': 'WY',
            'DC': 'DC', 'DISTRICT OF COLUMBIA': 'DC'
        }
        
        return state_mapping.get(state, state if len(state) == 2 else "")

    def _is_valid_state(self, state: str) -> bool:
        """Check if the given string is a valid US state name or abbreviation."""
        if not state:
            return False
            
        state = state.strip().upper()
        
        valid_states = {
            'AL', 'ALABAMA', 'AK', 'ALASKA', 'AZ', 'ARIZONA', 'AR', 'ARKANSAS',
            'CA', 'CALIFORNIA', 'CO', 'COLORADO', 'CT', 'CONNECTICUT', 'DE', 'DELAWARE',
            'FL', 'FLORIDA', 'GA', 'GEORGIA', 'HI', 'HAWAII', 'ID', 'IDAHO',
            'IL', 'ILLINOIS', 'IN', 'INDIANA', 'IA', 'IOWA', 'KS', 'KANSAS',
            'KY', 'KENTUCKY', 'LA', 'LOUISIANA', 'ME', 'MAINE', 'MD', 'MARYLAND',
            'MA', 'MASSACHUSETTS', 'MI', 'MICHIGAN', 'MN', 'MINNESOTA', 'MS', 'MISSISSIPPI',
            'MO', 'MISSOURI', 'MT', 'MONTANA', 'NE', 'NEBRASKA', 'NV', 'NEVADA',
            'NH', 'NEW HAMPSHIRE', 'NJ', 'NEW JERSEY', 'NM', 'NEW MEXICO', 'NY', 'NEW YORK',
            'NC', 'NORTH CAROLINA', 'ND', 'NORTH DAKOTA', 'OH', 'OHIO', 'OK', 'OKLAHOMA',
            'OR', 'OREGON', 'PA', 'PENNSYLVANIA', 'RI', 'RHODE ISLAND', 'SC', 'SOUTH CAROLINA',
            'SD', 'SOUTH DAKOTA', 'TN', 'TENNESSEE', 'TX', 'TEXAS', 'UT', 'UTAH',
            'VT', 'VERMONT', 'VA', 'VIRGINIA', 'WA', 'WASHINGTON', 'WV', 'WEST VIRGINIA',
            'WI', 'WISCONSIN', 'WY', 'WYOMING', 'DC', 'DISTRICT OF COLUMBIA'
        }
        
        return state in valid_states

    def process_row(self, text: str, row_id: Optional[str] = None, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a single row and return enhanced classification results with job details."""
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
                    'job_details': '',
                    'job_count': '',  # No job count for addresses
                    'city': '',       # No city extraction for addresses
                    'state': '',      # No state extraction for addresses
                    'processing_status': 'success',
                    'extraction_method': 'address_detection'
                }
            else:
                # Extract job title
                job_title = self.extract_job_title(text)
                
                # Extract job details from "Apply to..." section
                job_details = self._extract_apply_to_section(text)
                job_details_str = ', '.join(job_details) if job_details else ''
                
                # Extract new data: job count, city, state
                job_count = self.extract_job_count(text)
                city = self.extract_city(text)
                state = self.extract_state(text)
                
                # Classify job category
                category = self.classify_job_category(job_title, text)
                
                # Classify general category using job details context
                general_category = self.classify_general_category(job_title, category, text, job_details)
                
                # Calculate confidence
                confidence = self.calculate_confidence(text, job_title, category)
                
                result = {
                    'extracted_job_title': job_title,
                    'job_category': category,
                    'general_category': general_category,
                    'confidence': confidence,
                    'original_content': text,
                    'job_details': job_details_str,
                    'job_count': job_count,  # NEW: Total number of jobs
                    'city': city,            # NEW: City extracted from location
                    'state': state,          # NEW: State extracted from location
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
            'job_details': '',
            'job_count': '',     # NEW: Empty for errors
            'city': '',          # NEW: Empty for errors
            'state': '',         # NEW: Empty for errors
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
                         'original_content', 'job_details', 'job_count', 'city', 'state', 'row_id']  # Added new columns
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