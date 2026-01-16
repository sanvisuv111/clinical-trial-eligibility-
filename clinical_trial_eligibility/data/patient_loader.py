"""
Patient Data Loader - Utility for loading sample EHR data for testing
"""

import json
import os
from pathlib import Path


def load_sample_patients():
    """Load all sample patient data from the data directory."""
    data_dir = Path(__file__).parent
    patients = []
    
    for json_file in data_dir.glob('*.json'):
        with open(json_file, 'r') as f:
            patient_data = json.load(f)
            patients.append(patient_data)
    
    return patients


def get_sample_patient_by_id(patient_id: str):
    """Retrieve a specific sample patient by ID."""
    patients = load_sample_patients()
    for patient in patients:
        if patient['patient_id'] == patient_id:
            return patient
    return None


if __name__ == "__main__":
    patients = load_sample_patients()
    print(f"Loaded {len(patients)} sample patients:")
    for patient in patients:
        print(f"  - {patient['name']} ({patient['patient_id']})")
