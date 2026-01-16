"""
Trial Protocol Module
Defines and manages clinical trial protocols with their eligibility criteria.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from criteria_evaluator import CriteriaEvaluator, CriteriaType, PatientEligibilityReport
from ehr_parser import PatientRecord


@dataclass
class TrialProtocol:
    """Represents a clinical trial protocol."""
    trial_id: str
    trial_name: str
    description: str
    phase: str  # Phase I, II, III, IV
    target_enrollment: int
    disease_area: str
    primary_objective: str
    evaluator: CriteriaEvaluator = field(default_factory=CriteriaEvaluator)
    
    def evaluate_patient(self, patient: PatientRecord) -> PatientEligibilityReport:
        """Evaluate a patient against this trial's criteria."""
        return self.evaluator.evaluate_patient(patient)


class TrialBuilder:
    """Builder pattern for creating trial protocols with predefined criteria sets."""
    
    @staticmethod
    def create_diabetes_management_trial() -> TrialProtocol:
        """Create a sample diabetes management clinical trial."""
        trial = TrialProtocol(
            trial_id="TRIAL-DM-2024-001",
            trial_name="Advanced Diabetes Management Study",
            description="A phase III randomized controlled trial evaluating new glycemic control approaches",
            phase="Phase III",
            target_enrollment=250,
            disease_area="Endocrinology",
            primary_objective="Evaluate HbA1c reduction with new treatment protocol"
        )
        
        # Inclusion criteria
        trial.evaluator.add_age_criterion(
            min_age=18,
            max_age=75,
            criterion_id="age_inclusion"
        )
        trial.evaluator.add_condition_criterion(
            condition="Type 2 Diabetes",
            required=True,
            criterion_id="diabetes_inclusion"
        )
        trial.evaluator.add_lab_criterion(
            lab_test="HbA1c",
            min_value=6.5,
            max_value=11.0,
            criterion_id="hba1c_range"
        )
        trial.evaluator.add_lab_criterion(
            lab_test="creatinine",
            min_value=0.5,
            max_value=2.0,
            criterion_id="kidney_function"
        )
        
        # Exclusion criteria
        trial.evaluator.add_condition_criterion(
            condition="Type 1 Diabetes",
            required=False,
            criterion_type=CriteriaType.EXCLUSION,
            criterion_id="type1_exclusion"
        )
        trial.evaluator.add_condition_criterion(
            condition="Severe renal impairment",
            required=False,
            criterion_type=CriteriaType.EXCLUSION,
            criterion_id="renal_exclusion"
        )
        trial.evaluator.add_allergy_exclusion("metformin")
        
        return trial
    
    @staticmethod
    def create_cardiovascular_trial() -> TrialProtocol:
        """Create a sample cardiovascular disease clinical trial."""
        trial = TrialProtocol(
            trial_id="TRIAL-CV-2024-002",
            trial_name="Hypertension and Cardiovascular Outcomes Study",
            description="A phase III trial assessing new antihypertensive agent efficacy and safety",
            phase="Phase III",
            target_enrollment=500,
            disease_area="Cardiology",
            primary_objective="Demonstrate non-inferiority vs standard treatment in blood pressure control"
        )
        
        # Inclusion criteria
        trial.evaluator.add_age_criterion(
            min_age=40,
            max_age=80,
            criterion_id="age_inclusion"
        )
        trial.evaluator.add_condition_criterion(
            condition="hypertension",
            required=True,
            criterion_id="hypertension_inclusion"
        )
        trial.evaluator.add_lab_criterion(
            lab_test="systolic_bp",
            min_value=140,
            max_value=200,
            criterion_id="systolic_bp"
        )
        
        # Exclusion criteria
        trial.evaluator.add_condition_criterion(
            condition="acute coronary syndrome",
            required=False,
            criterion_type=CriteriaType.EXCLUSION,
            criterion_id="acs_exclusion"
        )
        trial.evaluator.add_medication_criterion(
            medication="ACE inhibitor",
            required=False,
            criterion_type=CriteriaType.EXCLUSION,
            criterion_id="ace_exclusion"
        )
        trial.evaluator.add_allergy_exclusion("lisinopril")
        
        return trial
    
    @staticmethod
    def create_respiratory_trial() -> TrialProtocol:
        """Create a sample respiratory disease clinical trial."""
        trial = TrialProtocol(
            trial_id="TRIAL-RESP-2024-003",
            trial_name="Asthma Control Enhancement Study",
            description="A phase II/III trial evaluating biologic therapy in moderate-to-severe asthma",
            phase="Phase II/III",
            target_enrollment=150,
            disease_area="Pulmonology",
            primary_objective="Assess asthma exacerbation reduction rate"
        )
        
        # Inclusion criteria
        trial.evaluator.add_age_criterion(
            min_age=12,
            max_age=70,
            criterion_id="age_inclusion"
        )
        trial.evaluator.add_condition_criterion(
            condition="asthma",
            required=True,
            criterion_id="asthma_inclusion"
        )
        trial.evaluator.add_medication_criterion(
            medication="inhaled corticosteroid",
            required=True,
            criterion_id="ics_requirement"
        )
        
        # Exclusion criteria
        trial.evaluator.add_condition_criterion(
            condition="COPD",
            required=False,
            criterion_type=CriteriaType.EXCLUSION,
            criterion_id="copd_exclusion"
        )
        trial.evaluator.add_condition_criterion(
            condition="severe immunosuppression",
            required=False,
            criterion_type=CriteriaType.EXCLUSION,
            criterion_id="immunosupp_exclusion"
        )
        trial.evaluator.add_allergy_exclusion("omalizumab")
        
        return trial


class TrialEligibilityFilter:
    """Filters patients against trial criteria."""
    
    @staticmethod
    def filter_patients(patients: List[PatientRecord],
                       trial: TrialProtocol) -> Dict[str, Any]:
        """
        Filter a list of patients for trial eligibility.
        
        Args:
            patients: List of patient records to evaluate
            trial: Trial protocol to match against
            
        Returns:
            Dictionary with eligible and ineligible patients and summary statistics
        """
        results = {
            "trial_id": trial.trial_id,
            "trial_name": trial.trial_name,
            "total_patients_screened": len(patients),
            "eligible_patients": [],
            "ineligible_patients": [],
            "eligibility_reports": []
        }
        
        for patient in patients:
            report = trial.evaluate_patient(patient)
            results["eligibility_reports"].append(report)
            
            if report.is_eligible:
                results["eligible_patients"].append({
                    "patient_id": patient.patient_id,
                    "name": patient.name,
                    "eligibility_score": report.eligibility_score
                })
            else:
                ineligible_reasons = []
                for result in report.inclusion_results:
                    if not result.passed:
                        ineligible_reasons.append(f"Failed: {result.criterion_name}")
                for result in report.exclusion_results:
                    if not result.passed:
                        ineligible_reasons.append(f"Excluded: {result.criterion_name}")
                
                results["ineligible_patients"].append({
                    "patient_id": patient.patient_id,
                    "name": patient.name,
                    "reasons": ineligible_reasons
                })
        
        results["summary"] = {
            "eligible_count": len(results["eligible_patients"]),
            "ineligible_count": len(results["ineligible_patients"]),
            "eligibility_rate": (len(results["eligible_patients"]) / len(patients) * 100) if patients else 0
        }
        
        return results
