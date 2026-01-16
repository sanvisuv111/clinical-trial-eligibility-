# Clinical Trial Eligibility Engine

A sophisticated Python application designed to accelerate clinical trial patient identification by automatically evaluating electronic health records (EHRs) against trial protocols. This system replaces manual chart review, significantly boosting recruitment speed and accuracy.

## Overview

The Clinical Trial Eligibility Engine is an intelligent system that automates patient recruitment by:

- **Parses EHR Data**: Ingests patient health records in standardized formats
- **Evaluates Inclusion/Exclusion Criteria**: Automatically assesses patient eligibility based on complex medical criteria
- **Filters Candidates**: Rapidly identifies eligible patients from large patient populations
- **Generates Reports**: Produces comprehensive eligibility assessments and recruitment statistics
- **Matches Patients to Trials**: Recommends suitable trials for individual patients

## Key Features

### 1. EHR Parsing Module (`ehr_parser.py`)
Handles the intake and processing of patient health records with the following capabilities:
- Accepts patient data from JSON and dictionary formats
- Provides a structured PatientRecord class for consistent data representation
- Includes intelligent querying methods for medical history and medication searches
- Automatically calculates patient age from date of birth

### 2. Criteria Evaluation Engine (`criteria_evaluator.py`)
The heart of the eligibility assessment system with support for:
- Both inclusion and exclusion criteria
- Multiple criterion types:
  - Age-based criteria
  - Medical condition requirements
  - Current medication status
  - Laboratory value ranges
  - Allergy screening
- Flexible evaluation functions for specialized or custom criteria
- Detailed reporting on each evaluation result

### 3. Trial Protocol Management (`trial_protocol.py`)
Manages clinical trial definitions and screening with:
- Complete trial information and objectives
- Predefined trial templates for common conditions (Diabetes Management, Cardiovascular Disease, Respiratory Disease)
- Batch screening capability to evaluate multiple patients against a single trial
- Eligibility filtering with detailed reasoning for decisions

### 4. Main Application Engine (`main.py`)
Orchestrates the entire screening workflow:
- Patient record loading and management
- Trial registration and configuration
- Multiple screening operations (single patient, all patients, multi-trial matching)
- Recruitment analytics and reporting

## System Architecture

```
Clinical Trial Eligibility Engine
├── EHR Parser Module
│   ├── Load patient records
│   ├── Parse JSON/Dictionary data
│   └── Calculate patient metrics
├── Criteria Evaluator
│   ├── Define eligibility criteria
│   ├── Evaluate patient compliance
│   └── Generate detailed results
├── Trial Protocol Manager
│   ├── Define trial protocols
│   ├── Filter patients by trial
│   └── Generate statistics
└── Main Application Engine
    ├── Orchestrate screening
    ├── Match patients to trials
    └── Generate recruitment reports
```

## Getting Started

### Prerequisites
- Python 3.8 or higher
- No external dependencies required (uses only Python standard library)

### Installation

1. Clone or download the project
2. Navigate to the project directory:
```bash
cd clinical_trial_eligibility
```

3. No additional installation needed - all modules are self-contained

### Quick Start

Run the demonstration application:
```bash
python src/main.py
```

This will:
1. Load sample patient records
2. Register predefined clinical trials
3. Perform screening operations
4. Display eligibility assessments
5. Generate recruitment reports

## Usage Examples

### Basic Patient Screening

```python
from src.main import ClinicalTrialEligibilityEngine
from src.trial_protocol import TrialBuilder
from src.ehr_parser import EHRParser

# Initialize engine
engine = ClinicalTrialEligibilityEngine()

# Register a trial
trial = TrialBuilder.create_diabetes_management_trial()
engine.register_trial(trial)

# Load patient
patient_data = {
    "patient_id": "PT-001",
    "name": "John Doe",
    "date_of_birth": "1965-05-15",
    "gender": "Male",
    "medical_history": ["Type 2 Diabetes"],
    "current_medications": ["Metformin"],
    "allergies": [],
    "lab_results": {"HbA1c": 8.0, "creatinine": 1.1},
    "vital_signs": {}
}
patient = EHRParser.parse_dict(patient_data)
engine.load_patient(patient)

# Screen patient for trial
result = engine.screen_patient_for_trial("PT-001", "TRIAL-DM-2024-001")
print(f"Eligible: {result['is_eligible']}")
print(f"Score: {result['eligibility_score']:.1f}%")
```

### Custom Trial Definition

```python
from src.criteria_evaluator import CriteriaEvaluator, CriteriaType

# Create custom evaluator
evaluator = CriteriaEvaluator()

# Add inclusion criteria
evaluator.add_age_criterion(min_age=18, max_age=75)
evaluator.add_condition_criterion("Target Disease", required=True)
evaluator.add_lab_criterion("marker", min_value=10, max_value=100)

# Add exclusion criteria
evaluator.add_condition_criterion("Contraindication", required=False, 
                                 criterion_type=CriteriaType.EXCLUSION)
evaluator.add_allergy_exclusion("Study Drug")

# Create and register trial
trial = TrialProtocol(
    trial_id="CUSTOM-001",
    trial_name="Custom Study",
    description="A custom clinical trial",
    phase="Phase II",
    target_enrollment=100,
    disease_area="Custom",
    primary_objective="Custom objective",
    evaluator=evaluator
)
engine.register_trial(trial)
```

### Recruitment Analytics

```python
# Generate recruitment report
report = engine.generate_recruitment_report()

print(f"Total Patients Screened: {report['total_patients_screened']}")
print(f"Total Trials: {report['total_trials']}")

for trial_summary in report['trial_summaries']:
    print(f"\nTrial: {trial_summary['trial_name']}")
    print(f"  Eligible: {trial_summary['eligible_candidates']}")
    print(f"  Rate: {trial_summary['eligible_rate']:.1f}%")
    print(f"  Status: {trial_summary['recruitment_status']}")
```

## Project Structure

```
clinical_trial_eligibility/
├── src/
│   ├── ehr_parser.py              # EHR parsing and patient records
│   ├── criteria_evaluator.py      # Eligibility criteria evaluation
│   ├── trial_protocol.py          # Trial protocol management
│   └── main.py                    # Main application engine
├── tests/
│   └── test_eligibility_engine.py # Comprehensive unit tests
├── data/
│   ├── sample_patient_1.json      # Sample patient data
│   ├── sample_patient_2.json      # Sample patient data
│   └── patient_loader.py          # Data loading utility
├── README.md                       # This file
└── requirements.txt               # Python dependencies
```

## Testing

Run the comprehensive test suite using unittest:

```bash
python -m unittest tests.test_eligibility_engine -v
```

### Test Coverage

The test suite includes validation for:
- EHR parsing with JSON and dictionary formats
- All criterion evaluation types (age, condition, medication, lab results, allergies)
- Trial protocol evaluation and filtering
- Patient batch screening operations
- Engine operations and error handling
- Data validation and edge cases

## Sample Output

When you run the demonstration, you'll see:

```
STEP 1: Patient Screening for Individual Trials
- Individual eligibility assessment
- Criterion-by-criterion results
- Eligibility scoring

STEP 2: Trial-Wide Screening
- Batch patient evaluation
- Eligible/ineligible classification
- Detailed ineligibility reasons

STEP 3: Patient-Trial Matching
- Multi-trial matching
- Best fit identification
- Ranked trial recommendations

STEP 4: Recruitment Report
- Overall statistics
- Trial-by-trial status
- Recruitment assessment
```

## Workflow

1. **Data Ingestion**: Load patient EHR records
2. **Protocol Setup**: Define or load trial protocols with criteria
3. **Screening**: Evaluate patients against criteria
4. **Reporting**: Generate eligibility assessments and statistics
5. **Analytics**: Identify gaps and optimize recruitment

## Use Cases

### Clinical Research Teams
- Rapidly identify eligible patient populations
- Reduce manual chart review time
- Improve recruitment efficiency

### Patient Matching
- Find most suitable trials for individual patients
- Provide personalized trial recommendations
- Increase patient-trial matching accuracy

### Recruitment Analytics
- Monitor enrollment progress
- Identify recruitment challenges
- Optimize trial protocol criteria

### Regulatory Compliance
- Document eligibility assessment process
- Generate audit trails
- Ensure consistent criteria application

## Data Privacy and Security Considerations

This is a demonstration system designed for educational purposes. In a production environment, you would need to:
- Implement HIPAA compliance measures
- Encrypt sensitive patient information
- Maintain comprehensive audit logs
- Use role-based access control
- Implement appropriate data retention policies

## Sample Criteria Sets

### Diabetes Management Trial
- Age: 18-75 years
- Must have Type 2 Diabetes
- HbA1c: 6.5-11.0%
- Creatinine: 0.5-2.0
- Exclude: Type 1 Diabetes, severe renal impairment

### Cardiovascular Trial
- Age: 40-80 years
- Must have hypertension
- Systolic BP: 140-200 mmHg
- Exclude: Recent MI, on ACE inhibitors

### Respiratory Trial
- Age: 12-70 years
- Must have asthma
- Must be on inhaled corticosteroid
- Exclude: COPD, severe immunosuppression

## Future Enhancements

- Multi-criteria optimization algorithms
- Machine learning for criterion prediction
- Drug interaction checking
- Genetic/genomic criterion support
- Patient preference integration
- Real-time trial availability matching
- Integration with EHR systems (FHIR API)
- Advanced analytics and visualization

## Support and Documentation

For questions or issues:
1. Check the documentation
2. Review test cases for usage examples
3. Examine sample data files

## License

This project is provided as-is for educational and demonstration purposes.

---

**Note**: This is a demonstration system. Real clinical trial eligibility systems should be validated, tested, and certified for clinical use with appropriate regulatory oversight.
