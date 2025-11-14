"""Service for importing employee master CSV from HR."""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
from decimal import Decimal
from contributions.exceptions import ValidationException


def parse_employee_master_csv(file_path: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Parse employee master CSV file.
    
    Expected format:
    employee_code,name,email,department,pod,pod_head
    
    Returns:
        Tuple of (parsed_rows, errors)
    """
    parsed_rows = []
    errors = []
    
    try:
        # Try different encodings
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path, encoding='latin-1')
            except:
                df = pd.read_csv(file_path, encoding='cp1252')
        
        # Normalize column names
        df.columns = [col.strip().lower() for col in df.columns]
        
        # Required columns
        required_columns = ['employee_code', 'name', 'email', 'department', 'pod', 'pod_head']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            errors.append({
                'row': 0,
                'field': 'headers',
                'message': f"Missing required columns: {', '.join(missing_columns)}"
            })
            return parsed_rows, errors
        
        # Process each row
        for idx, row in df.iterrows():
            row_num = idx + 2  # CSV row number (1-indexed + header)
            row_errors = []
            
            # Extract and validate fields
            employee_code = str(row.get('employee_code', '')).strip()
            name = str(row.get('name', '')).strip()
            email = str(row.get('email', '')).strip()
            department = str(row.get('department', '')).strip()
            pod = str(row.get('pod', '')).strip()
            pod_head = str(row.get('pod_head', '')).strip() if pd.notna(row.get('pod_head')) else None
            
            # Validate required fields
            if not employee_code:
                row_errors.append({
                    'row': row_num,
                    'field': 'employee_code',
                    'message': 'employee_code is required'
                })
            if not name:
                row_errors.append({
                    'row': row_num,
                    'field': 'name',
                    'message': 'name is required'
                })
            if not email:
                row_errors.append({
                    'row': row_num,
                    'field': 'email',
                    'message': 'email is required'
                })
            if not department:
                row_errors.append({
                    'row': row_num,
                    'field': 'department',
                    'message': 'department is required'
                })
            if not pod:
                row_errors.append({
                    'row': row_num,
                    'field': 'pod',
                    'message': 'pod is required'
                })
            
            # Validate email format
            if email and '@' not in email:
                row_errors.append({
                    'row': row_num,
                    'field': 'email',
                    'message': f'Invalid email format: {email}'
                })
            
            if row_errors:
                errors.extend(row_errors)
            else:
                parsed_rows.append({
                    'employee_code': employee_code,
                    'name': name,
                    'email': email,
                    'department': department,
                    'pod': pod,
                    'pod_head': pod_head,
                })
    
    except Exception as e:
        errors.append({
            'row': 0,
            'field': 'file',
            'message': f"Error parsing file: {str(e)}"
        })
    
    return parsed_rows, errors


def import_employees(parsed_rows: List[Dict]) -> Dict:
    """
    Import employees from parsed data.
    
    Returns:
        Dict with summary statistics
    """
    from contributions.storages import (
        department_storage, pod_storage, employee_storage
    )
    
    created_employees = 0
    updated_employees = 0
    created_departments = set()
    created_pods = set()
    
    for row in parsed_rows:
        # Get or create department
        dept = department_storage.get_or_create_department(row['department'])
        created_departments.add(dept.id)
        
        # Get or create pod
        pod = pod_storage.get_or_create_pod(row['pod'], dept.id)
        created_pods.add(pod.id)
        
        # Get pod_head employee if specified
        pod_head_id = None
        if row['pod_head']:
            try:
                pod_head = employee_storage.get_employee_by_code(row['pod_head'])
                pod_head_id = pod_head.id
            except:
                # Pod head not found, will be set later
                pass
        
        # Get or create employee
        try:
            existing = employee_storage.get_employee_by_code(row['employee_code'])
            # Employee exists, will be updated by get_or_create_employee
            updated_employees += 1
        except:
            # Employee doesn't exist, will be created
            created_employees += 1
        
        # Get or create employee (updates if exists)
        employee_storage.get_or_create_employee(
            employee_code=row['employee_code'],
            name=row['name'],
            email=row['email'],
            department_id=dept.id,
            pod_id=pod.id,
            pod_head_id=pod_head_id,
            role='EMPLOYEE'
        )
    
    return {
        'created_employees': created_employees,
        'updated_employees': updated_employees,
        'created_departments': len(created_departments),
        'created_pods': len(created_pods),
        'total_rows': len(parsed_rows)
    }

