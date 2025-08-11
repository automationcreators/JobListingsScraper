#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.advanced_classifier import AdvancedJobClassifier

def test_single_pattern():
    classifier = AdvancedJobClassifier(use_ai=False)
    text = "25 HVAC Technician jobs available in Phoenix, Arizona on job site"
    
    print(f"Input: {text}")
    city = classifier.extract_city(text)
    state = classifier.extract_state(text)
    
    print(f"City: '{city}'")
    print(f"State: '{state}'")

if __name__ == "__main__":
    test_single_pattern()