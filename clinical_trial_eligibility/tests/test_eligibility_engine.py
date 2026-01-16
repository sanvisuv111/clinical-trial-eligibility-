"""
Unit tests for the Clinical Trial Eligibility Engine.
"""

import unittest
import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ehr_parser import PatientRecord, EHRParser
from criteria_evaluator import CriteriaEvaluator, CriteriaType, EligibilityCriterion
from trial_protocol import TrialProtocol, TrialBuilder, TrialEligibilityFilter
from main import ClinicalTrialEligibilityEngine


class TestEHRParser(unittest.TestCase):
    """Test cases for EHR parsing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_patient_data = {
            "patient_id": "TEST-001",
            "name": "Test Patient",
            "date_of_birth": "1980-01-15",
            "gender": "Male",
            "medical_history": ["Diabetes", "Hypertension"],
            "current_medications": ["Metformin", "Lisinopril"],
            "allergies": ["Penicillin"],
            "lab_results": {"HbA1c": 8.0},
            "vital_signs": {"blood_pressure": "140/90"}
        }
    
    def test_parse_valid_json(self):
        """Test parsing valid JSON patient data."""
        json_str = json.dumps(self.valid_patient_data)
        patient = EHRParser.parse_json(json_str)
        
        self.assertEqual(patient.patient_id, "TEST-001")
        self.assertEqual(patient.name, "Test Patient")
        self.assertEqual(patient.gender, "Male")
        self.assertIn("Diabetes", patient.medical_history)
    
    def test_parse_dict(self):
        """Test parsing dictionary patient data."""
        patient = EHRParser.parse_dict(self.valid_patient_data)
        
        self.assertEqual(patient.patient_id, "TEST-001")
        self.assertEqual(patient.get_age(), 46)
    
    def test_invalid_json(self):
        """Test error handling for invalid JSON."""
        with self.assertRaises(ValueError):
            EHRParser.parse_json("invalid json")
    
    def test_missing_required_field(self):
        """Test error handling for missing required fields."""
        incomplete_data = self.valid_patient_data.copy()
        del incomplete_data["patient_id"]
        
        with self.assertRaises(ValueError):
            EHRParser.parse_dict(incomplete_data)
    
    def test_age_calculation(self):
        """Test age calculation from date of birth."""
        patient = EHRParser.parse_dict(self.valid_patient_data)
        age = patient.get_age()
        self.assertGreaterEqual(age, 40)
        self.assertLessEqual(age, 50)


class TestCriteriaEvaluator(unittest.TestCase):
    """Test cases for criteria evaluation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.evaluator = CriteriaEvaluator()
        self.patient = EHRParser.parse_dict({
            "patient_id": "TEST-002",
            "name": "Test Patient",
            "date_of_birth": "1970-01-01",
            "gender": "Female",
            "medical_history": ["Type 2 Diabetes"],
            "current_medications": ["Metformin", "Lisinopril"],
            "allergies": ["Metformin"],
            "lab_results": {"HbA1c": 7.5, "creatinine": 1.0},
            "vital_signs": {}
        })
    
    def test_age_criterion_pass(self):
        """Test age criterion when patient meets requirements."""
        self.evaluator.add_age_criterion(min_age=50, max_age=100)
        result = self.evaluator.evaluate_patient(self.patient)
        
        self.assertEqual(len(result.inclusion_results), 1)
        self.assertTrue(result.inclusion_results[0].passed)
    
    def test_age_criterion_fail(self):
        """Test age criterion when patient doesn't meet requirements."""
        self.evaluator.add_age_criterion(min_age=20, max_age=30)
        result = self.evaluator.evaluate_patient(self.patient)
        
        self.assertFalse(result.inclusion_results[0].passed)
    
    def test_condition_criterion_present(self):
        """Test condition criterion when patient has condition."""
        self.evaluator.add_condition_criterion("Type 2 Diabetes", required=True)
        result = self.evaluator.evaluate_patient(self.patient)
        
        self.assertTrue(result.inclusion_results[0].passed)
    
    def test_condition_criterion_absent(self):
        """Test condition criterion when patient doesn't have condition."""
        self.evaluator.add_condition_criterion("Heart Disease", required=True)
        result = self.evaluator.evaluate_patient(self.patient)
        
        self.assertFalse(result.inclusion_results[0].passed)
    
    def test_exclusion_criterion(self):
        """Test exclusion criterion."""
        self.evaluator.add_condition_criterion("Type 2 Diabetes", required=False,
                                              criterion_type=CriteriaType.EXCLUSION)
        result = self.evaluator.evaluate_patient(self.patient)
        
        # Exclusion criterion should fail because patient HAS the condition
        self.assertFalse(result.exclusion_results[0].passed)
    
    def test_medication_criterion(self):
        """Test medication-based criterion."""
        self.evaluator.add_medication_criterion("Metformin", required=True)
        result = self.evaluator.evaluate_patient(self.patient)
        
        self.assertTrue(result.inclusion_results[0].passed)
    
    def test_lab_criterion_range(self):
        """Test laboratory value range criterion."""
        self.evaluator.add_lab_criterion("HbA1c", min_value=6.5, max_value=9.0)
        result = self.evaluator.evaluate_patient(self.patient)
        
        self.assertTrue(result.inclusion_results[0].passed)
    
    def test_allergy_exclusion(self):
        """Test allergy-based exclusion criterion."""
        self.evaluator.add_allergy_exclusion("Metformin")
        result = self.evaluator.evaluate_patient(self.patient)
        
        # Should fail because patient IS allergic to Metformin
        self.assertFalse(result.exclusion_results[0].passed)


class TestTrialProtocol(unittest.TestCase):
    """Test cases for trial protocol and evaluation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trial = TrialBuilder.create_diabetes_management_trial()
        self.eligible_patient = EHRParser.parse_dict({
            "patient_id": "TEST-003",
            "name": "Eligible Patient",
            "date_of_birth": "1960-01-01",
            "gender": "Male",
            "medical_history": ["Type 2 Diabetes"],
            "current_medications": ["Metformin"],
            "allergies": [],
            "lab_results": {"HbA1c": 8.0, "creatinine": 1.0},
            "vital_signs": {}
        })
        
        self.ineligible_patient = EHRParser.parse_dict({
            "patient_id": "TEST-004",
            "name": "Ineligible Patient",
            "date_of_birth": "2010-01-01",
            "gender": "Male",
            "medical_history": ["Type 1 Diabetes"],
            "current_medications": [],
            "allergies": [],
            "lab_results": {"HbA1c": 5.0, "creatinine": 1.0},
            "vital_signs": {}
        })
    
    def test_trial_evaluation_eligible(self):
        """Test trial evaluation for eligible patient."""
        report = self.trial.evaluate_patient(self.eligible_patient)
        
        self.assertTrue(report.is_eligible)
        self.assertGreater(report.eligibility_score, 0)
    
    def test_trial_evaluation_ineligible(self):
        """Test trial evaluation for ineligible patient."""
        report = self.trial.evaluate_patient(self.ineligible_patient)
        
        self.assertFalse(report.is_eligible)


class TestTrialFilter(unittest.TestCase):
    """Test cases for trial eligibility filtering."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trial = TrialBuilder.create_diabetes_management_trial()
        
        self.patients = [
            EHRParser.parse_dict({
                "patient_id": f"PT-{i:03d}",
                "name": f"Patient {i}",
                "date_of_birth": f"195{i}-01-15",
                "gender": "Male",
                "medical_history": ["Type 2 Diabetes"],
                "current_medications": ["Metformin"],
                "allergies": [],
                "lab_results": {"HbA1c": 8.0 + i, "creatinine": 1.0},
                "vital_signs": {}
            }) for i in range(5)
        ]
    
    def test_filter_patients(self):
        """Test filtering patients for a trial."""
        results = TrialEligibilityFilter.filter_patients(self.patients, self.trial)
        
        self.assertEqual(results["total_patients_screened"], 5)
        self.assertIn("eligible_patients", results)
        self.assertIn("ineligible_patients", results)
        self.assertGreater(len(results["eligible_patients"]) + len(results["ineligible_patients"]), 0)


class TestClinicalTrialEngine(unittest.TestCase):
    """Test cases for the main engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = ClinicalTrialEligibilityEngine()
        self.engine.register_trial(TrialBuilder.create_diabetes_management_trial())
        
        self.patient = EHRParser.parse_dict({
            "patient_id": "TEST-005",
            "name": "Engine Test Patient",
            "date_of_birth": "1965-01-01",
            "gender": "Male",
            "medical_history": ["Type 2 Diabetes"],
            "current_medications": ["Metformin"],
            "allergies": [],
            "lab_results": {"HbA1c": 8.0, "creatinine": 1.0},
            "vital_signs": {}
        })
        
        self.engine.load_patient(self.patient)
    
    def test_screen_patient_for_trial(self):
        """Test screening a patient for a specific trial."""
        result = self.engine.screen_patient_for_trial("TEST-005", "TRIAL-DM-2024-001")
        
        self.assertEqual(result["patient_id"], "TEST-005")
        self.assertEqual(result["trial_id"], "TRIAL-DM-2024-001")
        self.assertIn("is_eligible", result)
        self.assertIn("eligibility_score", result)
    
    def test_screen_patients_for_trial(self):
        """Test screening all patients for a trial."""
        result = self.engine.screen_patients_for_trial("TRIAL-DM-2024-001")
        
        self.assertEqual(result["total_patients_screened"], 1)
        self.assertIn("summary", result)
    
    def test_patient_not_found(self):
        """Test error handling for non-existent patient."""
        with self.assertRaises(ValueError):
            self.engine.screen_patient_for_trial("NONEXISTENT", "TRIAL-DM-2024-001")
    
    def test_trial_not_found(self):
        """Test error handling for non-existent trial."""
        with self.assertRaises(ValueError):
            self.engine.screen_patient_for_trial("TEST-005", "NONEXISTENT")


if __name__ == "__main__":
    unittest.main()
