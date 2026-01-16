"""
Database Module - SQLite Database for Patient and Test Data
Manages all database operations for the Clinical Trial Eligibility Engine.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class DatabaseManager:
    """Manages SQLite database for patient and test results."""
    
    def __init__(self, db_path: str = "clinical_trial_data.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self.initialize_database()
    
    def initialize_database(self) -> None:
        """Create database and tables if they don't exist."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        
        # Create patients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                gender TEXT,
                medical_history TEXT,
                current_medications TEXT,
                allergies TEXT,
                lab_results TEXT,
                vital_signs TEXT,
                comorbidities TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create screening results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS screening_results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                trial_id TEXT NOT NULL,
                is_eligible BOOLEAN,
                eligibility_score REAL,
                total_criteria INTEGER,
                passed_criteria INTEGER,
                failed_criteria INTEGER,
                inclusion_results TEXT,
                exclusion_results TEXT,
                screened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                UNIQUE(patient_id, trial_id)
            )
        ''')
        
        # Create trials table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trials (
                trial_id TEXT PRIMARY KEY,
                trial_name TEXT NOT NULL,
                description TEXT,
                phase TEXT,
                target_enrollment INTEGER,
                disease_area TEXT,
                primary_objective TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create test results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                test_id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT NOT NULL,
                test_class TEXT,
                passed BOOLEAN,
                execution_time REAL,
                error_message TEXT,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.connection.commit()
        print(f"✓ Database initialized: {self.db_path}")
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
    
    # ============ PATIENT OPERATIONS ============
    
    def add_patient(self, patient_data: Dict[str, Any]) -> bool:
        """
        Add a patient to the database.
        
        Args:
            patient_data: Dictionary with patient information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO patients
                (patient_id, name, date_of_birth, gender, medical_history,
                 current_medications, allergies, lab_results, vital_signs, comorbidities)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_data['patient_id'],
                patient_data['name'],
                patient_data['date_of_birth'],
                patient_data.get('gender', ''),
                json.dumps(patient_data.get('medical_history', [])),
                json.dumps(patient_data.get('current_medications', [])),
                json.dumps(patient_data.get('allergies', [])),
                json.dumps(patient_data.get('lab_results', {})),
                json.dumps(patient_data.get('vital_signs', {})),
                json.dumps(patient_data.get('comorbidities', []))
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"✗ Error adding patient: {e}")
            return False
    
    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a patient from the database.
        
        Args:
            patient_id: ID of the patient to retrieve
            
        Returns:
            Dictionary with patient data or None
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,))
            row = cursor.fetchone()
            
            if row:
                return self._convert_row_to_dict(row)
            return None
        except Exception as e:
            print(f"✗ Error retrieving patient: {e}")
            return None
    
    def get_all_patients(self) -> List[Dict[str, Any]]:
        """
        Retrieve all patients from the database.
        
        Returns:
            List of patient dictionaries
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM patients ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [self._convert_row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"✗ Error retrieving patients: {e}")
            return []
    
    def delete_patient(self, patient_id: str) -> bool:
        """
        Delete a patient from the database.
        
        Args:
            patient_id: ID of the patient to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM patients WHERE patient_id = ?', (patient_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"✗ Error deleting patient: {e}")
            return False
    
    # ============ SCREENING RESULTS OPERATIONS ============
    
    def save_screening_result(self, result_data: Dict[str, Any]) -> bool:
        """
        Save a screening result to the database.
        
        Args:
            result_data: Dictionary with screening result
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO screening_results
                (patient_id, trial_id, is_eligible, eligibility_score,
                 total_criteria, passed_criteria, failed_criteria,
                 inclusion_results, exclusion_results)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result_data['patient_id'],
                result_data['trial_id'],
                result_data.get('is_eligible'),
                result_data.get('eligibility_score'),
                result_data.get('total_criteria'),
                result_data.get('passed_criteria'),
                result_data.get('failed_criteria'),
                json.dumps(result_data.get('inclusion_results', [])),
                json.dumps(result_data.get('exclusion_results', []))
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"✗ Error saving screening result: {e}")
            return False
    
    def get_screening_result(self, patient_id: str, trial_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific screening result.
        
        Args:
            patient_id: ID of the patient
            trial_id: ID of the trial
            
        Returns:
            Dictionary with screening result or None
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                'SELECT * FROM screening_results WHERE patient_id = ? AND trial_id = ?',
                (patient_id, trial_id)
            )
            row = cursor.fetchone()
            return self._convert_row_to_dict(row) if row else None
        except Exception as e:
            print(f"✗ Error retrieving screening result: {e}")
            return None
    
    def get_patient_screening_results(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get all screening results for a patient.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            List of screening results
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                'SELECT * FROM screening_results WHERE patient_id = ? ORDER BY screened_at DESC',
                (patient_id,)
            )
            rows = cursor.fetchall()
            return [self._convert_row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"✗ Error retrieving screening results: {e}")
            return []
    
    def get_trial_results(self, trial_id: str) -> List[Dict[str, Any]]:
        """
        Get all screening results for a trial.
        
        Args:
            trial_id: ID of the trial
            
        Returns:
            List of screening results
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                'SELECT * FROM screening_results WHERE trial_id = ? ORDER BY screened_at DESC',
                (trial_id,)
            )
            rows = cursor.fetchall()
            return [self._convert_row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"✗ Error retrieving trial results: {e}")
            return []
    
    def get_eligibility_stats(self, trial_id: str) -> Dict[str, Any]:
        """
        Get eligibility statistics for a trial.
        
        Args:
            trial_id: ID of the trial
            
        Returns:
            Dictionary with eligibility statistics
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN is_eligible = 1 THEN 1 ELSE 0 END) as eligible_count,
                    AVG(eligibility_score) as avg_score,
                    MAX(eligibility_score) as max_score,
                    MIN(eligibility_score) as min_score
                FROM screening_results
                WHERE trial_id = ?
            ''', (trial_id,))
            row = cursor.fetchone()
            
            if row:
                stats = dict(row)
                stats['eligible_count'] = stats['eligible_count'] or 0
                stats['eligibility_rate'] = (stats['eligible_count'] / stats['total'] * 100) if stats['total'] > 0 else 0
                return stats
            return {}
        except Exception as e:
            print(f"✗ Error getting stats: {e}")
            return {}
    
    # ============ TRIAL OPERATIONS ============
    
    def add_trial(self, trial_data: Dict[str, Any]) -> bool:
        """
        Add a trial to the database.
        
        Args:
            trial_data: Dictionary with trial information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO trials
                (trial_id, trial_name, description, phase, target_enrollment,
                 disease_area, primary_objective)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                trial_data['trial_id'],
                trial_data['trial_name'],
                trial_data.get('description', ''),
                trial_data.get('phase', ''),
                trial_data.get('target_enrollment', 0),
                trial_data.get('disease_area', ''),
                trial_data.get('primary_objective', '')
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"✗ Error adding trial: {e}")
            return False
    
    def get_trial(self, trial_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a trial from the database.
        
        Args:
            trial_id: ID of the trial to retrieve
            
        Returns:
            Dictionary with trial data or None
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM trials WHERE trial_id = ?', (trial_id,))
            row = cursor.fetchone()
            return self._convert_row_to_dict(row) if row else None
        except Exception as e:
            print(f"✗ Error retrieving trial: {e}")
            return None
    
    def get_all_trials(self) -> List[Dict[str, Any]]:
        """
        Retrieve all trials from the database.
        
        Returns:
            List of trial dictionaries
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM trials ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [self._convert_row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"✗ Error retrieving trials: {e}")
            return []
    
    # ============ TEST RESULTS OPERATIONS ============
    
    def save_test_result(self, test_result: Dict[str, Any]) -> bool:
        """
        Save a test result to the database.
        
        Args:
            test_result: Dictionary with test result information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO test_results
                (test_name, test_class, passed, execution_time, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                test_result.get('test_name', ''),
                test_result.get('test_class', ''),
                test_result.get('passed', False),
                test_result.get('execution_time', 0),
                test_result.get('error_message', '')
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"✗ Error saving test result: {e}")
            return False
    
    def get_test_results(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve recent test results.
        
        Args:
            limit: Maximum number of results to retrieve
            
        Returns:
            List of test result dictionaries
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                'SELECT * FROM test_results ORDER BY executed_at DESC LIMIT ?',
                (limit,)
            )
            rows = cursor.fetchall()
            return [self._convert_row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"✗ Error retrieving test results: {e}")
            return []
    
    def get_test_statistics(self) -> Dict[str, Any]:
        """
        Get test execution statistics.
        
        Returns:
            Dictionary with test statistics
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT
                    COUNT(*) as total_tests,
                    SUM(CASE WHEN passed = 1 THEN 1 ELSE 0 END) as passed_count,
                    SUM(CASE WHEN passed = 0 THEN 1 ELSE 0 END) as failed_count,
                    AVG(execution_time) as avg_execution_time,
                    MAX(execution_time) as max_execution_time,
                    MIN(execution_time) as min_execution_time
                FROM test_results
            ''')
            row = cursor.fetchone()
            
            if row:
                stats = dict(row)
                stats['pass_rate'] = (stats['passed_count'] / stats['total_tests'] * 100) if stats['total_tests'] > 0 else 0
                return stats
            return {}
        except Exception as e:
            print(f"✗ Error getting test statistics: {e}")
            return {}
    
    # ============ HELPER METHODS ============
    
    def _convert_row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert sqlite3.Row to dictionary."""
        if row is None:
            return {}
        
        data = dict(row)
        
        # Parse JSON fields
        json_fields = ['medical_history', 'current_medications', 'allergies', 
                       'lab_results', 'vital_signs', 'comorbidities',
                       'inclusion_results', 'exclusion_results']
        
        for field in json_fields:
            if field in data and data[field]:
                try:
                    data[field] = json.loads(data[field])
                except:
                    pass
        
        return data
    
    def clear_all_data(self) -> bool:
        """
        Clear all data from the database (use with caution!).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM screening_results')
            cursor.execute('DELETE FROM patients')
            cursor.execute('DELETE FROM trials')
            cursor.execute('DELETE FROM test_results')
            self.connection.commit()
            print("✓ Database cleared")
            return True
        except Exception as e:
            print(f"✗ Error clearing database: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get information about the database.
        
        Returns:
            Dictionary with database information
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM patients')
            patient_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM screening_results')
            result_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM trials')
            trial_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM test_results')
            test_count = cursor.fetchone()[0]
            
            db_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
            
            return {
                'database': self.db_path,
                'patients': patient_count,
                'screening_results': result_count,
                'trials': trial_count,
                'test_results': test_count,
                'database_size_bytes': db_size,
                'database_size_mb': db_size / (1024 * 1024)
            }
        except Exception as e:
            print(f"✗ Error getting database info: {e}")
            return {}
