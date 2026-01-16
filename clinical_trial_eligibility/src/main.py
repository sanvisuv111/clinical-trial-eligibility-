"""
Main application module for Clinical Trial Eligibility Engine.
Orchestrates patient screening and trial matching.
"""

import json
from typing import List, Dict, Any
from ehr_parser import PatientRecord, load_ehr_from_file
from trial_protocol import TrialProtocol, TrialBuilder, TrialEligibilityFilter


class ClinicalTrialEligibilityEngine:
    """Main engine for evaluating patient eligibility for clinical trials."""
    
    def __init__(self):
        """Initialize the engine."""
        self.patients: List[PatientRecord] = []
        self.trials: Dict[str, TrialProtocol] = {}
    
    def load_patient(self, patient_record: PatientRecord) -> None:
        """Add a patient to the engine."""
        self.patients.append(patient_record)
    
    def load_patients_from_file(self, filepath: str) -> None:
        """Load patient records from a JSON file."""
        patient = load_ehr_from_file(filepath)
        self.load_patient(patient)
    
    def register_trial(self, trial: TrialProtocol) -> None:
        """Register a trial protocol."""
        self.trials[trial.trial_id] = trial
    
    def screen_patient_for_trial(self, patient_id: str, trial_id: str) -> Dict[str, Any]:
        """
        Screen a single patient for a specific trial.
        
        Args:
            patient_id: ID of the patient to screen
            trial_id: ID of the trial
            
        Returns:
            Dictionary with screening results
        """
        patient = self._find_patient(patient_id)
        trial = self._find_trial(trial_id)
        
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        if not trial:
            raise ValueError(f"Trial {trial_id} not found")
        
        report = trial.evaluate_patient(patient)
        
        return {
            "patient_id": patient.patient_id,
            "patient_name": patient.name,
            "trial_id": trial.trial_id,
            "trial_name": trial.trial_name,
            "is_eligible": report.is_eligible,
            "eligibility_score": report.eligibility_score,
            "total_criteria": report.total_criteria,
            "passed_criteria": report.passed_criteria,
            "failed_criteria": report.failed_criteria,
            "inclusion_results": [
                {
                    "criterion": r.criterion_name,
                    "passed": r.passed,
                    "reason": r.reason
                } for r in report.inclusion_results
            ],
            "exclusion_results": [
                {
                    "criterion": r.criterion_name,
                    "passed": r.passed,
                    "reason": r.reason
                } for r in report.exclusion_results
            ]
        }
    
    def screen_patients_for_trial(self, trial_id: str) -> Dict[str, Any]:
        """
        Screen all patients for a specific trial.
        
        Args:
            trial_id: ID of the trial
            
        Returns:
            Dictionary with screening results for all patients
        """
        trial = self._find_trial(trial_id)
        if not trial:
            raise ValueError(f"Trial {trial_id} not found")
        
        return TrialEligibilityFilter.filter_patients(self.patients, trial)
    
    def screen_patient_for_all_trials(self, patient_id: str) -> Dict[str, Any]:
        """
        Screen a patient against all registered trials.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            Dictionary with screening results for all trials
        """
        patient = self._find_patient(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        results = {
            "patient_id": patient.patient_id,
            "patient_name": patient.name,
            "trial_matches": []
        }
        
        for trial_id, trial in self.trials.items():
            report = trial.evaluate_patient(patient)
            results["trial_matches"].append({
                "trial_id": trial.trial_id,
                "trial_name": trial.trial_name,
                "is_eligible": report.is_eligible,
                "eligibility_score": report.eligibility_score
            })
        
        results["eligible_trials"] = [t for t in results["trial_matches"] if t["is_eligible"]]
        results["ineligible_trials"] = [t for t in results["trial_matches"] if not t["is_eligible"]]
        
        return results
    
    def generate_recruitment_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive recruitment report for all trials.
        
        Returns:
            Dictionary with recruitment statistics and recommendations
        """
        report = {
            "total_patients_screened": len(self.patients),
            "total_trials": len(self.trials),
            "trial_summaries": []
        }
        
        for trial_id, trial in self.trials.items():
            trial_results = TrialEligibilityFilter.filter_patients(self.patients, trial)
            
            summary = {
                "trial_id": trial.trial_id,
                "trial_name": trial.trial_name,
                "phase": trial.phase,
                "target_enrollment": trial.target_enrollment,
                "eligible_candidates": len(trial_results["eligible_patients"]),
                "eligible_rate": trial_results["summary"]["eligibility_rate"],
                "recruitment_status": self._assess_recruitment_status(
                    len(trial_results["eligible_patients"]),
                    trial.target_enrollment
                )
            }
            report["trial_summaries"].append(summary)
        
        return report
    
    def _find_patient(self, patient_id: str) -> PatientRecord:
        """Find a patient by ID."""
        for patient in self.patients:
            if patient.patient_id == patient_id:
                return patient
        return None
    
    def _find_trial(self, trial_id: str) -> TrialProtocol:
        """Find a trial by ID."""
        return self.trials.get(trial_id)
    
    @staticmethod
    def _assess_recruitment_status(eligible_count: int, target: int) -> str:
        """Assess the recruitment status of a trial."""
        if eligible_count >= target:
            return "RECRUITING - GOAL MET"
        elif eligible_count >= target * 0.75:
            return "ACTIVELY RECRUITING"
        elif eligible_count > 0:
            return "RECRUITING - EXPANSION NEEDED"
        else:
            return "INSUFFICIENT ELIGIBLE CANDIDATES"


def demo_application():
    """Demonstrate the clinical trial eligibility engine."""
    print("=" * 70)
    print("CLINICAL TRIAL ELIGIBILITY ENGINE - DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Initialize engine
    engine = ClinicalTrialEligibilityEngine()
    
    # Register sample trials
    engine.register_trial(TrialBuilder.create_diabetes_management_trial())
    engine.register_trial(TrialBuilder.create_cardiovascular_trial())
    engine.register_trial(TrialBuilder.create_respiratory_trial())
    
    # Create sample patients
    sample_patients = [
        {
            "patient_id": "PT-001",
            "name": "John Smith",
            "date_of_birth": "1968-03-15",
            "gender": "Male",
            "medical_history": ["Type 2 Diabetes", "Hypertension", "Hyperlipidemia"],
            "current_medications": ["Metformin", "Lisinopril", "Atorvastatin"],
            "allergies": [],
            "lab_results": {
                "HbA1c": 8.2,
                "creatinine": 1.1,
                "systolic_bp": 155,
                "diastolic_bp": 92
            },
            "vital_signs": {
                "blood_pressure": "155/92",
                "heart_rate": 72,
                "temperature": 98.6
            },
            "comorbidities": ["Metabolic Syndrome"]
        },
        {
            "patient_id": "PT-002",
            "name": "Mary Johnson",
            "date_of_birth": "1992-07-22",
            "gender": "Female",
            "medical_history": ["Asthma"],
            "current_medications": ["Albuterol", "Fluticasone"],
            "allergies": ["Penicillin"],
            "lab_results": {
                "FEV1": 78,
                "systolic_bp": 118,
                "diastolic_bp": 75
            },
            "vital_signs": {
                "blood_pressure": "118/75",
                "heart_rate": 68,
                "temperature": 98.4
            },
            "comorbidities": []
        },
        {
            "patient_id": "PT-003",
            "name": "Robert Davis",
            "date_of_birth": "1955-11-10",
            "gender": "Male",
            "medical_history": ["Type 2 Diabetes", "Chronic Kidney Disease Stage 3", "Hypertension"],
            "current_medications": ["Insulin Glargine", "Amlodipine", "Allopurinol"],
            "allergies": ["Metformin"],
            "lab_results": {
                "HbA1c": 7.8,
                "creatinine": 2.5,
                "eGFR": 28,
                "systolic_bp": 162,
                "diastolic_bp": 88
            },
            "vital_signs": {
                "blood_pressure": "162/88",
                "heart_rate": 76,
                "temperature": 98.8
            },
            "comorbidities": ["Chronic Kidney Disease"]
        },
        {
            "patient_id": "PT-004",
            "name": "Sarah Williams",
            "date_of_birth": "1988-05-18",
            "gender": "Female",
            "medical_history": ["Moderate Asthma"],
            "current_medications": ["Fluticasone-Salmeterol", "Omalizumab"],
            "allergies": [],
            "lab_results": {
                "FEV1": 72,
                "IgE": 250,
                "systolic_bp": 122,
                "diastolic_bp": 78
            },
            "vital_signs": {
                "blood_pressure": "122/78",
                "heart_rate": 70,
                "temperature": 98.5
            },
            "comorbidities": []
        }
    ]
    
    # Load patients
    for patient_data in sample_patients:
        from ehr_parser import EHRParser
        patient = EHRParser.parse_dict(patient_data)
        engine.load_patient(patient)
    
    print("STEP 1: Patient Screening for Individual Trials")
    print("-" * 70)
    print()
    
    # Screen patient for specific trial
    result = engine.screen_patient_for_trial("PT-001", "TRIAL-DM-2024-001")
    print(f"Patient: {result['patient_name']} ({result['patient_id']})")
    print(f"Trial: {result['trial_name']}")
    print(f"Eligible: {'YES' if result['is_eligible'] else 'NO'}")
    print(f"Eligibility Score: {result['eligibility_score']:.1f}%")
    print(f"Passed Criteria: {result['passed_criteria']}/{result['total_criteria']}")
    print()
    print("Inclusion Criteria:")
    for criterion in result['inclusion_results']:
        status = "✓ PASS" if criterion['passed'] else "✗ FAIL"
        print(f"  {status}: {criterion['criterion']}")
    print()
    print("Exclusion Criteria:")
    for criterion in result['exclusion_results']:
        status = "✓ PASS" if criterion['passed'] else "✗ FAIL"
        print(f"  {status}: {criterion['criterion']}")
    print()
    print()
    
    print("STEP 2: Trial-Wide Screening")
    print("-" * 70)
    print()
    
    # Screen all patients for a trial
    trial_results = engine.screen_patients_for_trial("TRIAL-RESP-2024-003")
    print(f"Trial: {trial_results['trial_name']}")
    print(f"Total Patients Screened: {trial_results['total_patients_screened']}")
    print(f"Eligible Candidates: {trial_results['summary']['eligible_count']}")
    print(f"Eligibility Rate: {trial_results['summary']['eligibility_rate']:.1f}%")
    print()
    print("Eligible Patients:")
    for patient in trial_results['eligible_patients']:
        print(f"  - {patient['name']} ({patient['patient_id']})")
    print()
    print("Ineligible Patients and Reasons:")
    for patient in trial_results['ineligible_patients']:
        print(f"  - {patient['name']} ({patient['patient_id']})")
        for reason in patient['reasons']:
            print(f"    • {reason}")
    print()
    print()
    
    print("STEP 3: Patient-Trial Matching")
    print("-" * 70)
    print()
    
    # Find best trial matches for a patient
    patient_matches = engine.screen_patient_for_all_trials("PT-002")
    print(f"Patient: {patient_matches['patient_name']} ({patient_matches['patient_id']})")
    print()
    print("Eligible Trials:")
    for trial in patient_matches['eligible_trials']:
        print(f"  ✓ {trial['trial_name']} (Score: {trial['eligibility_score']:.1f}%)")
    print()
    print("Ineligible Trials:")
    for trial in patient_matches['ineligible_trials']:
        print(f"  ✗ {trial['trial_name']}")
    print()
    print()
    
    print("STEP 4: Recruitment Report")
    print("-" * 70)
    print()
    
    # Generate comprehensive recruitment report
    recruitment_report = engine.generate_recruitment_report()
    print(f"Total Patients Screened: {recruitment_report['total_patients_screened']}")
    print(f"Total Trials: {recruitment_report['total_trials']}")
    print()
    print("Trial Recruitment Status:")
    for trial in recruitment_report['trial_summaries']:
        print(f"  {trial['trial_name']} ({trial['phase']})")
        print(f"    Target Enrollment: {trial['target_enrollment']}")
        print(f"    Eligible Candidates: {trial['eligible_candidates']}")
        print(f"    Eligibility Rate: {trial['eligible_rate']:.1f}%")
        print(f"    Status: {trial['recruitment_status']}")
        print()
    
    print("=" * 70)
    print("END OF DEMONSTRATION")
    print("=" * 70)


if __name__ == "__main__":
    demo_application()
