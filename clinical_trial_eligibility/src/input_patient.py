"""
Interactive Patient Data Input Module
Allows users to input patient data through the command line.
"""

import json
from datetime import datetime
from ehr_parser import EHRParser, PatientRecord


def input_patient_data() -> dict:
    """
    Interactively collect patient data from user input.
    
    Returns:
        Dictionary with patient data ready for EHRParser
    """
    print("\n" + "="*60)
    print("PATIENT DATA INPUT FORM")
    print("="*60 + "\n")
    
    # Basic Information
    print("--- BASIC INFORMATION ---")
    patient_id = input("Patient ID (e.g., PT-001): ").strip()
    name = input("Full Name: ").strip()
    
    # Date of Birth
    while True:
        dob = input("Date of Birth (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(dob, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid format! Please use YYYY-MM-DD (e.g., 1965-05-15)")
    
    gender = input("Gender (Male/Female/Other): ").strip()
    
    # Medical History
    print("\n--- MEDICAL HISTORY ---")
    print("(Enter conditions separated by commas, or press Enter to skip)")
    medical_history_input = input("Medical Conditions: ").strip()
    medical_history = [c.strip() for c in medical_history_input.split(",") if c.strip()]
    
    # Current Medications
    print("\n--- CURRENT MEDICATIONS ---")
    print("(Enter medications separated by commas, or press Enter to skip)")
    medications_input = input("Current Medications: ").strip()
    current_medications = [m.strip() for m in medications_input.split(",") if m.strip()]
    
    # Allergies
    print("\n--- ALLERGIES ---")
    print("(Enter allergies separated by commas, or press Enter to skip)")
    allergies_input = input("Allergies: ").strip()
    allergies = [a.strip() for a in allergies_input.split(",") if a.strip()]
    
    # Laboratory Results
    print("\n--- LABORATORY RESULTS ---")
    lab_results = {}
    print("(Enter lab test results, or press Enter to skip)")
    print("Common lab tests: HbA1c, glucose_fasting, creatinine, systolic_bp, diastolic_bp")
    
    while True:
        lab_test = input("Lab Test Name (or 'done' to finish): ").strip().lower()
        if lab_test == "done" or lab_test == "":
            break
        
        try:
            value = float(input(f"Value for {lab_test}: "))
            lab_results[lab_test] = value
        except ValueError:
            print("Invalid number! Please enter a numeric value.")
    
    # Vital Signs
    print("\n--- VITAL SIGNS ---")
    vital_signs = {}
    print("(Enter vital signs, or press Enter to skip)")
    
    while True:
        vital = input("Vital Sign Name (e.g., heart_rate, or 'done' to finish): ").strip().lower()
        if vital == "done" or vital == "":
            break
        
        try:
            value = float(input(f"Value for {vital}: "))
            vital_signs[vital] = value
        except ValueError:
            print("Invalid number! Please enter a numeric value.")
    
    # Comorbidities
    print("\n--- COMORBIDITIES ---")
    print("(Enter additional comorbidities separated by commas, or press Enter to skip)")
    comorbidities_input = input("Comorbidities: ").strip()
    comorbidities = [c.strip() for c in comorbidities_input.split(",") if c.strip()]
    
    # Create patient data dictionary
    patient_data = {
        "patient_id": patient_id,
        "name": name,
        "date_of_birth": dob,
        "gender": gender,
        "medical_history": medical_history,
        "current_medications": current_medications,
        "allergies": allergies,
        "lab_results": lab_results,
        "vital_signs": vital_signs,
        "comorbidities": comorbidities
    }
    
    return patient_data


def display_patient_summary(patient_data: dict) -> None:
    """Display a summary of the entered patient data."""
    print("\n" + "="*60)
    print("PATIENT SUMMARY")
    print("="*60)
    print(f"ID: {patient_data['patient_id']}")
    print(f"Name: {patient_data['name']}")
    print(f"DOB: {patient_data['date_of_birth']}")
    print(f"Gender: {patient_data['gender']}")
    
    if patient_data['medical_history']:
        print(f"Medical History: {', '.join(patient_data['medical_history'])}")
    
    if patient_data['current_medications']:
        print(f"Medications: {', '.join(patient_data['current_medications'])}")
    
    if patient_data['allergies']:
        print(f"Allergies: {', '.join(patient_data['allergies'])}")
    
    if patient_data['lab_results']:
        print("Lab Results:")
        for test, value in patient_data['lab_results'].items():
            print(f"  {test}: {value}")
    
    if patient_data['vital_signs']:
        print("Vital Signs:")
        for vital, value in patient_data['vital_signs'].items():
            print(f"  {vital}: {value}")
    
    if patient_data['comorbidities']:
        print(f"Comorbidities: {', '.join(patient_data['comorbidities'])}")
    
    print("="*60 + "\n")


def save_patient_to_file(patient_data: dict, filepath: str) -> None:
    """Save patient data to a JSON file."""
    with open(filepath, 'w') as f:
        json.dump(patient_data, f, indent=2)
    print(f"✓ Patient data saved to: {filepath}")


def input_and_process_patient():
    """Main function: Get patient input and process it."""
    try:
        # Get patient data
        patient_data = input_patient_data()
        
        # Display summary
        display_patient_summary(patient_data)
        
        # Validate data
        try:
            patient = EHRParser.parse_dict(patient_data)
            print(f"✓ Patient data validated successfully")
            print(f"✓ Patient age: {patient.get_age()} years")
        except ValueError as e:
            print(f"✗ Validation error: {e}")
            return None
        
        # Ask user what to do with the data
        print("\nWhat would you like to do?")
        print("1. Save to file")
        print("2. Screen against a trial")
        print("3. Both (save and screen)")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice in ["1", "3"]:
            filename = input("Enter filename (without .json): ").strip()
            if not filename:
                filename = f"patient_{patient_data['patient_id']}"
            filepath = f"data/{filename}.json"
            save_patient_to_file(patient_data, filepath)
        
        if choice in ["2", "3"]:
            screen_patient_for_trials(patient)
        
        return patient
        
    except KeyboardInterrupt:
        print("\n\nInput cancelled by user.")
        return None
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return None


def screen_patient_for_trials(patient: PatientRecord) -> None:
    """Screen a patient against available trials."""
    from trial_protocol import TrialBuilder
    
    print("\n" + "="*60)
    print("SCREENING PATIENT AGAINST TRIALS")
    print("="*60 + "\n")
    
    trials = [
        TrialBuilder.create_diabetes_management_trial(),
        TrialBuilder.create_cardiovascular_trial(),
        TrialBuilder.create_respiratory_trial()
    ]
    
    print(f"Screening {patient.name} against {len(trials)} trials...\n")
    
    eligible_count = 0
    
    for trial in trials:
        report = trial.evaluate_patient(patient)
        status = "✓ ELIGIBLE" if report.is_eligible else "✗ NOT ELIGIBLE"
        print(f"{status}: {trial.trial_name}")
        print(f"  Score: {report.eligibility_score:.1f}%")
        print(f"  Passed: {report.passed_criteria}/{report.total_criteria} criteria")
        
        if report.is_eligible:
            eligible_count += 1
        
        # Show failed inclusion criteria
        failed_inclusion = [r for r in report.inclusion_results if not r.passed]
        if failed_inclusion:
            print(f"  Failed Inclusion Criteria:")
            for result in failed_inclusion:
                print(f"    - {result.criterion_name}")
        
        # Show failed exclusion criteria
        failed_exclusion = [r for r in report.exclusion_results if not r.passed]
        if failed_exclusion:
            print(f"  Exclusion Issues:")
            for result in failed_exclusion:
                print(f"    - {result.criterion_name}")
        
        print()
    
    print("="*60)
    print(f"Summary: Patient is eligible for {eligible_count}/{len(trials)} trials")
    print("="*60 + "\n")


def interactive_menu():
    """Main interactive menu."""
    print("\n" + "="*60)
    print("CLINICAL TRIAL ELIGIBILITY ENGINE - PATIENT DATA INPUT")
    print("="*60 + "\n")
    
    while True:
        print("Options:")
        print("1. Input new patient data")
        print("2. Load patient from file")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            input_and_process_patient()
        
        elif choice == "2":
            filepath = input("Enter patient JSON file path: ").strip()
            try:
                patient = EHRParser.parse_json(open(filepath).read())
                print(f"\n✓ Loaded patient: {patient.name} ({patient.patient_id})")
                print(f"  Age: {patient.get_age()} years")
                
                screen_choice = input("\nScreen against trials? (y/n): ").strip().lower()
                if screen_choice == "y":
                    screen_patient_for_trials(patient)
            
            except FileNotFoundError:
                print(f"✗ File not found: {filepath}")
            except Exception as e:
                print(f"✗ Error loading file: {e}")
        
        elif choice == "3":
            print("\nExiting...")
            break
        
        else:
            print("Invalid option. Please select 1, 2, or 3.")


if __name__ == "__main__":
    interactive_menu()
