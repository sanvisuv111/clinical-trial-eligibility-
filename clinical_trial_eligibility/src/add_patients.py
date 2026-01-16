"""
Add sample patients to the database.
Run this script to populate the database with additional patient records.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database import DatabaseManager


def add_sample_patients():
    """Add 4 new sample patients to the database."""
    
    db = DatabaseManager("clinical_trial_data.db")
    
    # 4 new sample patients
    new_patients = [
        {
            "patient_id": "PT-003",
            "name": "Patricia Davis",
            "date_of_birth": "1970-11-28",
            "gender": "Female",
            "medical_history": [
                "Type 2 Diabetes Mellitus",
                "Hypertension",
                "Chronic Kidney Disease Stage 2"
            ],
            "current_medications": [
                "Metformin 850mg twice daily",
                "Amlodipine 10mg daily",
                "Pravastatin 20mg daily"
            ],
            "allergies": [
                "ACE inhibitors"
            ],
            "lab_results": {
                "HbA1c": 8.5,
                "glucose_fasting": 165,
                "creatinine": 1.3,
                "eGFR": 55,
                "systolic_bp": 142,
                "diastolic_bp": 88
            },
            "vital_signs": {
                "blood_pressure": "142/88",
                "heart_rate": 75,
                "respiratory_rate": 16,
                "temperature": 98.5,
                "BMI": 29.8
            },
            "comorbidities": [
                "Chronic Kidney Disease",
                "Dyslipidemia"
            ]
        },
        {
            "patient_id": "PT-004",
            "name": "Robert Wilson",
            "date_of_birth": "1975-05-14",
            "gender": "Male",
            "medical_history": [
                "Essential Hypertension",
                "Hyperlipidemia",
                "Type 2 Diabetes"
            ],
            "current_medications": [
                "Lisinopril 20mg daily",
                "Atorvastatin 80mg daily",
                "Metformin 500mg three times daily",
                "Hydrochlorothiazide 25mg daily"
            ],
            "allergies": [],
            "lab_results": {
                "HbA1c": 7.2,
                "glucose_fasting": 128,
                "creatinine": 1.0,
                "eGFR": 80,
                "total_cholesterol": 195,
                "LDL": 110,
                "HDL": 45,
                "systolic_bp": 138,
                "diastolic_bp": 85
            },
            "vital_signs": {
                "blood_pressure": "138/85",
                "heart_rate": 72,
                "respiratory_rate": 15,
                "temperature": 98.4,
                "BMI": 30.1
            },
            "comorbidities": [
                "Metabolic Syndrome"
            ]
        },
        {
            "patient_id": "PT-005",
            "name": "Sandra Martinez",
            "date_of_birth": "1988-02-09",
            "gender": "Female",
            "medical_history": [
                "Asthma",
                "Allergic Rhinitis"
            ],
            "current_medications": [
                "Fluticasone-Salmeterol inhaler",
                "Albuterol rescue inhaler",
                "Cetirizine 10mg daily"
            ],
            "allergies": [
                "Penicillin",
                "Aspirin"
            ],
            "lab_results": {
                "FEV1": 82,
                "FVC": 95,
                "systolic_bp": 115,
                "diastolic_bp": 72
            },
            "vital_signs": {
                "blood_pressure": "115/72",
                "heart_rate": 68,
                "respiratory_rate": 14,
                "temperature": 98.3,
                "BMI": 24.5
            },
            "comorbidities": []
        },
        {
            "patient_id": "PT-006",
            "name": "Richard Anderson",
            "date_of_birth": "1958-09-03",
            "gender": "Male",
            "medical_history": [
                "Coronary Artery Disease",
                "Hypertension",
                "Hyperlipidemia",
                "Type 2 Diabetes"
            ],
            "current_medications": [
                "Metoprolol 50mg twice daily",
                "Lisinopril 10mg daily",
                "Rosuvastatin 20mg daily",
                "Aspirin 325mg daily",
                "Metformin 500mg twice daily"
            ],
            "allergies": [],
            "lab_results": {
                "HbA1c": 8.1,
                "glucose_fasting": 155,
                "creatinine": 1.2,
                "eGFR": 65,
                "total_cholesterol": 180,
                "LDL": 95,
                "HDL": 35,
                "triglycerides": 250,
                "systolic_bp": 145,
                "diastolic_bp": 90
            },
            "vital_signs": {
                "blood_pressure": "145/90",
                "heart_rate": 76,
                "respiratory_rate": 17,
                "temperature": 98.7,
                "BMI": 28.9
            },
            "comorbidities": [
                "Coronary Artery Disease",
                "Heart Failure Risk"
            ]
        }
    ]
    
    print("\n" + "="*70)
    print("ADDING 4 NEW PATIENTS TO DATABASE")
    print("="*70 + "\n")
    
    success_count = 0
    for patient in new_patients:
        if db.add_patient(patient):
            print(f"✓ Added: {patient['name']} ({patient['patient_id']})")
            print(f"  Age: {2026 - int(patient['date_of_birth'][:4])} years")
            print(f"  Conditions: {', '.join(patient['medical_history'][:2])}...")
            print()
            success_count += 1
        else:
            print(f"✗ Failed to add: {patient['name']}")
    
    # Display summary
    db_info = db.get_database_info()
    print("="*70)
    print(f"✓ Successfully added {success_count}/4 patients")
    print(f"Total patients in database: {db_info['patients']}")
    print("="*70 + "\n")
    
    db.close()


if __name__ == "__main__":
    add_sample_patients()
