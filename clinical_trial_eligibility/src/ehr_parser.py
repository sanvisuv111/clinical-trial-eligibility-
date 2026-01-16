"""
EHR Parser Module
Parses and validates electronic health records data.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


@dataclass
class PatientRecord:
    """Represents a patient's electronic health record."""
    patient_id: str
    name: str
    date_of_birth: str
    gender: str
    medical_history: List[str]
    current_medications: List[str]
    allergies: List[str]
    lab_results: Dict[str, Any]
    vital_signs: Dict[str, float]
    comorbidities: List[str]
    
    def get_age(self) -> int:
        """Calculate patient age in years."""
        dob = datetime.strptime(self.date_of_birth, "%Y-%m-%d")
        today = datetime.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    def has_condition(self, condition: str) -> bool:
        """Check if patient has a specific medical condition."""
        condition_lower = condition.lower()
        return any(condition_lower in hist.lower() for hist in self.medical_history) or \
               any(condition_lower in cond.lower() for cond in self.comorbidities)
    
    def is_on_medication(self, medication: str) -> bool:
        """Check if patient is taking a specific medication."""
        med_lower = medication.lower()
        return any(med_lower in med.lower() for med in self.current_medications)


class EHRParser:
    """Parses electronic health records from various formats."""
    
    @staticmethod
    def parse_json(json_data: str) -> PatientRecord:
        """
        Parse EHR data from JSON format.
        
        Args:
            json_data: JSON string containing patient data
            
        Returns:
            PatientRecord object
            
        Raises:
            ValueError: If JSON data is invalid or missing required fields
        """
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        
        required_fields = {
            'patient_id', 'name', 'date_of_birth', 'gender',
            'medical_history', 'current_medications', 'allergies',
            'lab_results', 'vital_signs'
        }
        
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        return PatientRecord(
            patient_id=data['patient_id'],
            name=data['name'],
            date_of_birth=data['date_of_birth'],
            gender=data['gender'],
            medical_history=data.get('medical_history', []),
            current_medications=data.get('current_medications', []),
            allergies=data.get('allergies', []),
            lab_results=data.get('lab_results', {}),
            vital_signs=data.get('vital_signs', {}),
            comorbidities=data.get('comorbidities', [])
        )
    
    @staticmethod
    def parse_dict(data: Dict[str, Any]) -> PatientRecord:
        """
        Parse EHR data from dictionary format.
        
        Args:
            data: Dictionary containing patient data
            
        Returns:
            PatientRecord object
        """
        json_str = json.dumps(data)
        return EHRParser.parse_json(json_str)


def load_ehr_from_file(filepath: str) -> PatientRecord:
    """
    Load EHR data from a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        PatientRecord object
    """
    with open(filepath, 'r') as f:
        json_data = f.read()
    return EHRParser.parse_json(json_data)
