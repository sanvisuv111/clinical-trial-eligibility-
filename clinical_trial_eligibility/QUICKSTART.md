# Quick Start - Clinical Trial Eligibility Engine

## 🚀 Get Started in 30 Seconds

### 1. Run the Demo
```bash
cd clinical_trial_eligibility
python src/main.py
```

This will demonstrate the full system with sample patients and trials.

### 2. Run Tests
```bash
python -m unittest tests.test_eligibility_engine -v
```

All 20 tests should pass.

---

## 5-Minute Integration

### Load Your First Patient
```python
from src.ehr_parser import EHRParser

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
print(f"Patient: {patient.name}, Age: {patient.get_age()}")
```

### Screen for a Trial
```python
from src.main import ClinicalTrialEligibilityEngine
from src.trial_protocol import TrialBuilder

engine = ClinicalTrialEligibilityEngine()
engine.register_trial(TrialBuilder.create_diabetes_management_trial())
engine.load_patient(patient)

result = engine.screen_patient_for_trial("PT-001", "TRIAL-DM-2024-001")
print(f"Eligible: {result['is_eligible']}")
print(f"Score: {result['eligibility_score']:.1f}%")
```

---

## File Structure
```
clinical_trial_eligibility/
├── src/              # Main application code
├── tests/            # Unit tests (20 tests, all passing)
├── data/             # Sample patient data
├── README.md         # Full documentation
├── API_REFERENCE.md  # API docs
├── USAGE_GUIDE.md    # Usage examples
└── PROJECT_SUMMARY.md # Project details
```

---

## Key Classes

| Class | Module | Purpose |
|-------|--------|---------|
| `PatientRecord` | ehr_parser | Patient health data |
| `EHRParser` | ehr_parser | Parse patient JSON/dict |
| `CriteriaEvaluator` | criteria_evaluator | Evaluate eligibility |
| `TrialProtocol` | trial_protocol | Trial definition |
| `TrialBuilder` | trial_protocol | Create trials |
| `ClinicalTrialEligibilityEngine` | main | Main orchestrator |

---

## Core Operations

### 1. Screen Single Patient for Single Trial
```python
result = engine.screen_patient_for_trial(patient_id, trial_id)
# Returns: dict with is_eligible, score, detailed criteria results
```

### 2. Screen All Patients for One Trial
```python
results = engine.screen_patients_for_trial(trial_id)
# Returns: dict with eligible/ineligible lists and statistics
```

### 3. Find Best Trials for One Patient
```python
matches = engine.screen_patient_for_all_trials(patient_id)
# Returns: dict with eligible and ineligible trials
```

### 4. Generate Recruitment Report
```python
report = engine.generate_recruitment_report()
# Returns: recruitment status for all trials
```

---

## Supported Criteria Types

- ✅ Age ranges (18-75 years)
- ✅ Medical conditions (required/excluded)
- ✅ Medications (required/excluded)
- ✅ Lab values (ranges)
- ✅ Allergies (exclusions)
- ✅ Custom functions

---

## Sample Output

```
Patient: John Smith (PT-001)
Trial: Advanced Diabetes Management Study
Eligible: YES
Score: 100.0%
Passed: 7/7 criteria

Inclusion Criteria:
  ✓ Age 18-75 years
  ✓ Patient has Type 2 Diabetes
  ✓ HbA1c between 6.5 and 11.0

Exclusion Criteria:
  ✓ Patient does not have Type 1 Diabetes
  ✓ No allergy to metformin
```

---

## Requirements

- **Python**: 3.8+
- **Dependencies**: None (uses standard library only)

---

## Next Steps

1. **Review README.md** for comprehensive documentation
2. **Check API_REFERENCE.md** for detailed API docs
3. **Read USAGE_GUIDE.md** for code examples
4. **Run src/main.py** to see the system in action
5. **Explore test cases** in tests/test_eligibility_engine.py

---

## Common Tasks

### Create Custom Trial
```python
from src.criteria_evaluator import CriteriaEvaluator
from src.trial_protocol import TrialProtocol

evaluator = CriteriaEvaluator()
evaluator.add_age_criterion(21, 65)
evaluator.add_condition_criterion("Target Disease", required=True)

trial = TrialProtocol(
    trial_id="CUSTOM-001",
    trial_name="My Trial",
    description="My custom trial",
    phase="Phase II",
    target_enrollment=100,
    disease_area="Oncology",
    primary_objective="Evaluate treatment",
    evaluator=evaluator
)
```

### Batch Load Patients
```python
patients = [EHRParser.parse_dict(p) for p in patient_list]
for patient in patients:
    engine.load_patient(patient)
```

### Export Results
```python
import json
results = engine.screen_patients_for_trial(trial_id)
with open('results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

---

## Troubleshooting

**ImportError**: Ensure you're in the project directory when importing  
**Patient not found**: Check patient_id spelling  
**Trial not found**: Use correct trial_id  
**Invalid data**: Verify JSON format and required fields  

---

## Support

- See **README.md** for full documentation
- See **USAGE_GUIDE.md** for detailed examples
- See **API_REFERENCE.md** for API details
- Review **tests/** for code examples

---

**Ready to go!** 🎉 Run `python src/main.py` to see the system in action.
