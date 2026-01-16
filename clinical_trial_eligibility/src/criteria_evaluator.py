"""
Criteria Evaluator Module
Evaluates patient eligibility against trial inclusion/exclusion criteria.
"""

from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any, Optional
from enum import Enum
from ehr_parser import PatientRecord


class CriteriaType(Enum):
    """Types of eligibility criteria."""
    INCLUSION = "inclusion"
    EXCLUSION = "exclusion"


@dataclass
class EligibilityCriterion:
    """Represents a single eligibility criterion."""
    criterion_id: str
    name: str
    description: str
    criterion_type: CriteriaType
    evaluator: Callable[[PatientRecord], bool]
    weight: float = 1.0  # Importance weight for scoring


@dataclass
class EvaluationResult:
    """Result of evaluating a single criterion."""
    criterion_id: str
    criterion_name: str
    passed: bool
    reason: str
    criterion_type: CriteriaType


@dataclass
class PatientEligibilityReport:
    """Complete eligibility evaluation report for a patient."""
    patient_id: str
    patient_name: str
    is_eligible: bool
    total_criteria: int
    passed_criteria: int
    failed_criteria: int
    eligibility_score: float
    inclusion_results: List[EvaluationResult] = field(default_factory=list)
    exclusion_results: List[EvaluationResult] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate eligibility score."""
        total = self.passed_criteria + self.failed_criteria
        if total > 0:
            self.eligibility_score = (self.passed_criteria / total) * 100
        else:
            self.eligibility_score = 0.0


class CriteriaEvaluator:
    """Evaluates patient records against trial criteria."""
    
    def __init__(self):
        """Initialize the evaluator."""
        self.criteria: List[EligibilityCriterion] = []
    
    def add_criterion(self, criterion: EligibilityCriterion) -> None:
        """Add an eligibility criterion."""
        self.criteria.append(criterion)
    
    def add_age_criterion(self, min_age: int, max_age: int,
                         criterion_id: str = "age",
                         criterion_type: CriteriaType = CriteriaType.INCLUSION) -> None:
        """Add age-based inclusion/exclusion criterion."""
        def age_evaluator(patient: PatientRecord) -> bool:
            age = patient.get_age()
            return min_age <= age <= max_age
        
        criterion = EligibilityCriterion(
            criterion_id=criterion_id,
            name=f"Age {min_age}-{max_age} years",
            description=f"Patient age must be between {min_age} and {max_age} years",
            criterion_type=criterion_type,
            evaluator=age_evaluator
        )
        self.add_criterion(criterion)
    
    def add_condition_criterion(self, condition: str, required: bool = True,
                               criterion_id: Optional[str] = None,
                               criterion_type: Optional[CriteriaType] = None) -> None:
        """Add criterion based on medical condition."""
        if criterion_type is None:
            criterion_type = CriteriaType.INCLUSION if required else CriteriaType.EXCLUSION
        
        if criterion_id is None:
            criterion_id = f"condition_{condition.lower().replace(' ', '_')}"
        
        def condition_evaluator(patient: PatientRecord) -> bool:
            return patient.has_condition(condition) if required else not patient.has_condition(condition)
        
        action = "has" if required else "does not have"
        criterion = EligibilityCriterion(
            criterion_id=criterion_id,
            name=f"Patient {action} {condition}",
            description=f"Patient must {'have' if required else 'not have'} {condition}",
            criterion_type=criterion_type,
            evaluator=condition_evaluator
        )
        self.add_criterion(criterion)
    
    def add_medication_criterion(self, medication: str, required: bool = True,
                                criterion_id: Optional[str] = None,
                                criterion_type: Optional[CriteriaType] = None) -> None:
        """Add criterion based on current medications."""
        if criterion_type is None:
            criterion_type = CriteriaType.INCLUSION if required else CriteriaType.EXCLUSION
        
        if criterion_id is None:
            criterion_id = f"med_{medication.lower().replace(' ', '_')}"
        
        def medication_evaluator(patient: PatientRecord) -> bool:
            return patient.is_on_medication(medication) if required else not patient.is_on_medication(medication)
        
        action = "taking" if required else "not taking"
        criterion = EligibilityCriterion(
            criterion_id=criterion_id,
            name=f"Patient {action} {medication}",
            description=f"Patient must be {'on' if required else 'off'} {medication}",
            criterion_type=criterion_type,
            evaluator=medication_evaluator
        )
        self.add_criterion(criterion)
    
    def add_lab_criterion(self, lab_test: str, min_value: Optional[float] = None,
                         max_value: Optional[float] = None,
                         criterion_id: Optional[str] = None) -> None:
        """Add criterion based on laboratory results."""
        if criterion_id is None:
            criterion_id = f"lab_{lab_test.lower().replace(' ', '_')}"
        
        def lab_evaluator(patient: PatientRecord) -> bool:
            if lab_test not in patient.lab_results:
                return False
            
            value = patient.lab_results[lab_test]
            if min_value is not None and value < min_value:
                return False
            if max_value is not None and value > max_value:
                return False
            return True
        
        range_str = self._build_range_string(min_value, max_value)
        criterion = EligibilityCriterion(
            criterion_id=criterion_id,
            name=f"{lab_test} {range_str}",
            description=f"{lab_test} must be {range_str}",
            criterion_type=CriteriaType.INCLUSION,
            evaluator=lab_evaluator
        )
        self.add_criterion(criterion)
    
    def add_allergy_exclusion(self, allergen: str, criterion_id: Optional[str] = None) -> None:
        """Add exclusion criterion for specific allergen."""
        if criterion_id is None:
            criterion_id = f"allergy_{allergen.lower().replace(' ', '_')}"
        
        def allergy_evaluator(patient: PatientRecord) -> bool:
            allergen_lower = allergen.lower()
            return not any(allergen_lower in allergy.lower() for allergy in patient.allergies)
        
        criterion = EligibilityCriterion(
            criterion_id=criterion_id,
            name=f"No allergy to {allergen}",
            description=f"Patient must not be allergic to {allergen}",
            criterion_type=CriteriaType.EXCLUSION,
            evaluator=allergy_evaluator
        )
        self.add_criterion(criterion)
    
    def evaluate_patient(self, patient: PatientRecord) -> PatientEligibilityReport:
        """
        Evaluate a patient's eligibility against all criteria.
        
        Args:
            patient: PatientRecord to evaluate
            
        Returns:
            PatientEligibilityReport with detailed results
        """
        inclusion_results = []
        exclusion_results = []
        
        for criterion in self.criteria:
            passed = criterion.evaluator(patient)
            result = EvaluationResult(
                criterion_id=criterion.criterion_id,
                criterion_name=criterion.name,
                passed=passed,
                reason=criterion.description,
                criterion_type=criterion.criterion_type
            )
            
            if criterion.criterion_type == CriteriaType.INCLUSION:
                inclusion_results.append(result)
            else:
                exclusion_results.append(result)
        
        # Patient is eligible if ALL inclusion criteria pass AND NO exclusion criteria fail
        all_inclusion_pass = all(r.passed for r in inclusion_results) if inclusion_results else True
        no_exclusion_fail = all(r.passed for r in exclusion_results) if exclusion_results else True
        is_eligible = all_inclusion_pass and no_exclusion_fail
        
        passed_criteria = sum(1 for r in inclusion_results if r.passed) + \
                         sum(1 for r in exclusion_results if r.passed)
        failed_criteria = sum(1 for r in inclusion_results if not r.passed) + \
                         sum(1 for r in exclusion_results if not r.passed)
        
        return PatientEligibilityReport(
            patient_id=patient.patient_id,
            patient_name=patient.name,
            is_eligible=is_eligible,
            total_criteria=len(self.criteria),
            passed_criteria=passed_criteria,
            failed_criteria=failed_criteria,
            eligibility_score=0.0,  # Will be calculated in post_init
            inclusion_results=inclusion_results,
            exclusion_results=exclusion_results
        )
    
    @staticmethod
    def _build_range_string(min_val: Optional[float], max_val: Optional[float]) -> str:
        """Build a readable range string."""
        if min_val is not None and max_val is not None:
            return f"between {min_val} and {max_val}"
        elif min_val is not None:
            return f">= {min_val}"
        elif max_val is not None:
            return f"<= {max_val}"
        return "within acceptable range"
