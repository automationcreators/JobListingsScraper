#!/usr/bin/env python3
"""
Template Management System
Save and reuse processing configurations across different datasets
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

class TemplateManager:
    """Manages processing templates for reusable configurations"""
    
    def __init__(self, templates_dir: str = "data/templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def save_template(self, name: str, config: Dict[str, Any], description: str = "") -> bool:
        """Save a processing configuration as a template"""
        try:
            template = {
                "name": name,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "config": config
            }
            
            # Create safe filename
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_name.replace(' ', '_').lower()}.json"
            template_path = self.templates_dir / filename
            
            with open(template_path, 'w') as f:
                json.dump(template, f, indent=2)
            
            logging.info(f"Template '{name}' saved to {template_path}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to save template '{name}': {e}")
            return False
    
    def load_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a template by name"""
        try:
            # Try exact filename first
            template_path = self.templates_dir / f"{name}.json"
            if not template_path.exists():
                # Try with safe name conversion
                safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_name.replace(' ', '_').lower()}.json"
                template_path = self.templates_dir / filename
            
            if not template_path.exists():
                logging.warning(f"Template '{name}' not found")
                return None
            
            with open(template_path, 'r') as f:
                template = json.load(f)
            
            logging.info(f"Template '{name}' loaded successfully")
            return template
            
        except Exception as e:
            logging.error(f"Failed to load template '{name}': {e}")
            return None
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates with metadata"""
        templates = []
        
        try:
            for template_file in self.templates_dir.glob("*.json"):
                try:
                    with open(template_file, 'r') as f:
                        template = json.load(f)
                    
                    templates.append({
                        "name": template.get("name", template_file.stem),
                        "description": template.get("description", ""),
                        "created_at": template.get("created_at", ""),
                        "version": template.get("version", "1.0"),
                        "filename": template_file.name,
                        "file_size": template_file.stat().st_size
                    })
                except Exception as e:
                    logging.warning(f"Could not read template {template_file}: {e}")
                    
        except Exception as e:
            logging.error(f"Failed to list templates: {e}")
        
        return sorted(templates, key=lambda x: x["created_at"], reverse=True)
    
    def delete_template(self, name: str) -> bool:
        """Delete a template"""
        try:
            # Try exact filename first
            template_path = self.templates_dir / f"{name}.json"
            if not template_path.exists():
                # Try with safe name conversion
                safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_name.replace(' ', '_').lower()}.json"
                template_path = self.templates_dir / filename
            
            if template_path.exists():
                template_path.unlink()
                logging.info(f"Template '{name}' deleted")
                return True
            else:
                logging.warning(f"Template '{name}' not found for deletion")
                return False
                
        except Exception as e:
            logging.error(f"Failed to delete template '{name}': {e}")
            return False

class JobClassificationTemplate:
    """Specific template for job classification configurations"""
    
    @staticmethod
    def create_from_classifier(classifier) -> Dict[str, Any]:
        """Create template config from current classifier"""
        config = {
            "type": "job_classification",
            "categories": {
                "Aviation Mechanic": {
                    "keywords": ["aircraft", "aviation", "airplane", "airline", "airport", "mechanic", "maintenance"],
                    "priority": 1
                },
                "HVAC Technician": {
                    "keywords": ["hvac", "heating", "cooling", "air conditioning", "ventilation", "technician"],
                    "priority": 1
                },
                "Security Guard": {
                    "keywords": ["security", "guard", "safety", "protection", "officer"],
                    "priority": 1
                },
                "Construction Worker": {
                    "keywords": ["construction", "building", "contractor", "worker", "builder"],
                    "priority": 1
                },
                "Project Manager": {
                    "keywords": ["project", "manager", "management", "coordinator"],
                    "priority": 2
                },
                "Welder": {
                    "keywords": ["weld", "welding", "fabrication", "metal"],
                    "priority": 1
                },
                "Plumber": {
                    "keywords": ["plumb", "plumbing", "pipe", "water", "drain"],
                    "priority": 1
                },
                "Electrician": {
                    "keywords": ["electric", "electrical", "wiring", "power"],
                    "priority": 1
                },
                "CDL Driver": {
                    "keywords": ["cdl", "driver", "truck", "commercial", "transport"],
                    "priority": 1
                },
                "Registered Nurse": {
                    "keywords": ["registered nurse", "rn", "nursing"],
                    "priority": 1
                },
                "Technician": {
                    "keywords": ["technician", "tech", "specialist"],
                    "priority": 3
                }
            },
            "extraction_patterns": [
                r"(\d+)?\s*([A-Za-z\s&]+?)\s+jobs?\s+(?:available\s+)?in\s+",
                r"(\d+)?\s*([A-Za-z\s&]+?)\s+positions?\s+(?:available|open)",
                r"(?:hiring|seeking|looking for)\s+(\d+)?\s*([A-Za-z\s&]+?)(?:\s+in|\s+for|\s+jobs)",
                r"Apply to\s+([A-Za-z\s&,]+?)(?:\s+and more|\s*!|\s*$)",
                r"(\d+)?\s*([A-Za-z\s&]+?(?:technicians?|mechanics?|specialists?|assistants?|managers?|coordinators?|supervisors?|directors?|analysts?|engineers?|developers?|designers?|operators?|workers?|drivers?|nurses?|therapists?|pathologists?|electricians?|plumbers?|welders?|guards?|officers?|pilots?))\s+(?:jobs?|positions?|openings?)"
            ],
            "location_patterns": [
                r"in\s+([A-Za-z\s\.']{2,30}),\s*([A-Z]{2})(?:\s+\d{5})?",
                r"(\w+),\s*([A-Z]{2})\s+",
                r"^\d+\s+([A-Z][A-Za-z\s]{1,25}),\s*([A-Z]{2})\s+"
            ],
            "job_count_patterns": [
                r"(\d+)\+\s+jobs?",
                r"^(\d+)\s+",
                r"(\d+)\s+(?:job|position|opening|vacancy|role)s?\s+(?:available|posted|found|listed|in\s+)"
            ],
            "processing_settings": {
                "use_ai": False,
                "confidence_threshold": 0.5,
                "extract_job_count": True,
                "extract_city": True,
                "extract_state": True,
                "extract_job_details": True
            },
            "output_columns": [
                "row_id", "extracted_job_title", "job_category", "general_category", 
                "confidence", "job_count", "city", "state", "job_details", 
                "original_content", "processing_status", "extraction_method"
            ]
        }
        
        return config
    
    @staticmethod
    def apply_to_classifier(config: Dict[str, Any], classifier):
        """Apply template config to classifier (future functionality)"""
        # This would be used to configure a classifier from a template
        # For now, we'll store the config and use it during processing
        return config

# Global template manager instance
template_manager = TemplateManager()