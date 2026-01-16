"""
Database Usage Examples and CLI Interface
Demonstrates how to use the database module.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database import DatabaseManager
from ehr_parser import EHRParser
from trial_protocol import TrialBuilder


def demo_database_operations():
    """Demonstrate all database operations."""
    
    print("\n" + "="*70)
    print("CLINICAL TRIAL ELIGIBILITY ENGINE - DATABASE DEMO")
    print("="*70 + "\n")
    
    # Initialize database
    db = DatabaseManager("clinical_trial_data.db")
    
    # Load sample patients
    print("Step 1: Loading sample patients into database...")
    sample_patients = [
        {
            "patient_id": "PT-001",
            "name": "John Smith",
            "date_of_birth": "1968-03-15",
            "gender": "Male",
            "medical_history": ["Type 2 Diabetes", "Hypertension"],
            "current_medications": ["Metformin", "Lisinopril"],
            "allergies": [],
            "lab_results": {"HbA1c": 8.2, "creatinine": 1.1},
            "vital_signs": {"blood_pressure": "155/92", "heart_rate": 72}
        },
        {
            "patient_id": "PT-002",
            "name": "Mary Johnson",
            "date_of_birth": "1992-07-22",
            "gender": "Female",
            "medical_history": ["Asthma"],
            "current_medications": ["Albuterol", "Fluticasone"],
            "allergies": ["Penicillin"],
            "lab_results": {"FEV1": 78},
            "vital_signs": {"blood_pressure": "118/75"}
        }
    ]
    
    for patient in sample_patients:
        if db.add_patient(patient):
            print(f"  ✓ Added: {patient['name']}")
    
    # Add trials
    print("\nStep 2: Adding trials to database...")
    trials = [
        TrialBuilder.create_diabetes_management_trial(),
        TrialBuilder.create_cardiovascular_trial(),
        TrialBuilder.create_respiratory_trial()
    ]
    
    for trial in trials:
        trial_data = {
            'trial_id': trial.trial_id,
            'trial_name': trial.trial_name,
            'description': trial.description,
            'phase': trial.phase,
            'target_enrollment': trial.target_enrollment,
            'disease_area': trial.disease_area,
            'primary_objective': trial.primary_objective
        }
        if db.add_trial(trial_data):
            print(f"  ✓ Added: {trial.trial_name}")
    
    # Screen patients and save results
    print("\nStep 3: Screening patients and saving results...")
    for patient_data in sample_patients:
        patient = EHRParser.parse_dict(patient_data)
        
        for trial in trials:
            report = trial.evaluate_patient(patient)
            
            result_data = {
                'patient_id': patient.patient_id,
                'trial_id': trial.trial_id,
                'is_eligible': report.is_eligible,
                'eligibility_score': report.eligibility_score,
                'total_criteria': report.total_criteria,
                'passed_criteria': report.passed_criteria,
                'failed_criteria': report.failed_criteria,
                'inclusion_results': [
                    {'criterion': r.criterion_name, 'passed': r.passed}
                    for r in report.inclusion_results
                ],
                'exclusion_results': [
                    {'criterion': r.criterion_name, 'passed': r.passed}
                    for r in report.exclusion_results
                ]
            }
            
            if db.save_screening_result(result_data):
                status = "✓ ELIGIBLE" if report.is_eligible else "✗ NOT ELIGIBLE"
                print(f"  {status}: {patient.name} → {trial.trial_name}")
    
    # Retrieve and display results
    print("\nStep 4: Retrieving results from database...")
    
    all_patients = db.get_all_patients()
    print(f"\n  Total Patients in DB: {len(all_patients)}")
    for patient in all_patients:
        print(f"    - {patient['name']} ({patient['patient_id']})")
    
    all_trials = db.get_all_trials()
    print(f"\n  Total Trials in DB: {len(all_trials)}")
    for trial in all_trials:
        print(f"    - {trial['trial_name']} ({trial['trial_id']})")
    
    # Get specific patient results
    print("\nStep 5: Patient-specific results...")
    patient_results = db.get_patient_screening_results("PT-001")
    print(f"  Screening results for John Smith: {len(patient_results)} trials")
    for result in patient_results:
        status = "✓" if result['is_eligible'] else "✗"
        print(f"    {status} {result['trial_id']}: {result['eligibility_score']:.1f}%")
    
    # Get trial statistics
    print("\nStep 6: Trial statistics...")
    for trial in trials:
        stats = db.get_eligibility_stats(trial.trial_id)
        if stats.get('total'):
            print(f"\n  {trial.trial_name}:")
            print(f"    Total Screened: {stats['total']}")
            print(f"    Eligible: {stats['eligible_count']}")
            print(f"    Eligibility Rate: {stats['eligibility_rate']:.1f}%")
            print(f"    Avg Score: {stats['avg_score']:.1f}%")
    
    # Display database info
    print("\nStep 7: Database Information...")
    db_info = db.get_database_info()
    print(f"  Database File: {db_info['database']}")
    print(f"  Patients: {db_info['patients']}")
    print(f"  Screening Results: {db_info['screening_results']}")
    print(f"  Trials: {db_info['trials']}")
    print(f"  Test Results: {db_info['test_results']}")
    print(f"  Database Size: {db_info['database_size_mb']:.2f} MB")
    
    db.close()
    
    print("\n" + "="*70)
    print("DATABASE DEMO COMPLETE!")
    print("="*70 + "\n")


def interactive_database_menu():
    """Interactive database management menu."""
    db = DatabaseManager("clinical_trial_data.db")
    
    while True:
        print("\n" + "="*70)
        print("DATABASE MANAGEMENT MENU")
        print("="*70)
        print("\n1. View all patients")
        print("2. View patient details")
        print("3. View all trials")
        print("4. View screening results for patient")
        print("5. View screening results for trial")
        print("6. View trial statistics")
        print("7. View database information")
        print("8. Clear all data (WARNING!)")
        print("9. Run demo (load sample data)")
        print("0. Exit")
        
        choice = input("\nSelect option (0-9): ").strip()
        
        if choice == "1":
            patients = db.get_all_patients()
            print(f"\nTotal Patients: {len(patients)}")
            for p in patients:
                print(f"  - {p['name']} ({p['patient_id']}) - {p['gender']}")
        
        elif choice == "2":
            patient_id = input("Enter patient ID: ").strip()
            patient = db.get_patient(patient_id)
            if patient:
                print(f"\nPatient Details:")
                print(f"  Name: {patient['name']}")
                print(f"  DOB: {patient['date_of_birth']}")
                print(f"  Gender: {patient['gender']}")
                print(f"  Medical History: {', '.join(patient.get('medical_history', []))}")
                print(f"  Medications: {', '.join(patient.get('current_medications', []))}")
            else:
                print("Patient not found!")
        
        elif choice == "3":
            trials = db.get_all_trials()
            print(f"\nTotal Trials: {len(trials)}")
            for t in trials:
                print(f"  - {t['trial_name']} ({t['trial_id']})")
                print(f"    Phase: {t['phase']}, Target: {t['target_enrollment']} patients")
        
        elif choice == "4":
            patient_id = input("Enter patient ID: ").strip()
            results = db.get_patient_screening_results(patient_id)
            print(f"\nScreening Results for {patient_id}: {len(results)} trials")
            for r in results:
                status = "✓ ELIGIBLE" if r['is_eligible'] else "✗ NOT ELIGIBLE"
                print(f"  {status}: {r['trial_id']}")
                print(f"    Score: {r['eligibility_score']:.1f}% ({r['passed_criteria']}/{r['total_criteria']})")
        
        elif choice == "5":
            trial_id = input("Enter trial ID: ").strip()
            results = db.get_trial_results(trial_id)
            print(f"\nScreening Results for {trial_id}: {len(results)} patients")
            for r in results:
                status = "✓" if r['is_eligible'] else "✗"
                print(f"  {status} {r['patient_id']}: {r['eligibility_score']:.1f}%")
        
        elif choice == "6":
            trial_id = input("Enter trial ID: ").strip()
            stats = db.get_eligibility_stats(trial_id)
            if stats.get('total'):
                print(f"\nTrial Statistics for {trial_id}:")
                print(f"  Total Screened: {stats['total']}")
                print(f"  Eligible: {stats['eligible_count']}")
                print(f"  Eligibility Rate: {stats['eligibility_rate']:.1f}%")
                print(f"  Average Score: {stats['avg_score']:.1f}%")
                print(f"  Score Range: {stats['min_score']:.1f}% - {stats['max_score']:.1f}%")
            else:
                print("No screening results found!")
        
        elif choice == "7":
            info = db.get_database_info()
            print(f"\nDatabase Information:")
            print(f"  File: {info['database']}")
            print(f"  Patients: {info['patients']}")
            print(f"  Screening Results: {info['screening_results']}")
            print(f"  Trials: {info['trials']}")
            print(f"  Test Results: {info['test_results']}")
            print(f"  Size: {info['database_size_mb']:.2f} MB")
        
        elif choice == "8":
            confirm = input("WARNING: This will delete ALL data. Continue? (yes/no): ").strip().lower()
            if confirm == "yes":
                if db.clear_all_data():
                    print("✓ Database cleared!")
            else:
                print("Operation cancelled.")
        
        elif choice == "9":
            demo_database_operations()
        
        elif choice == "0":
            break
        
        else:
            print("Invalid option!")
    
    db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_database_operations()
    else:
        interactive_database_menu()
