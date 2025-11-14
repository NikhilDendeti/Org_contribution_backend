"""Service for parsing feature CSV files."""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime, date
from decimal import Decimal
from contributions.exceptions import ValidationException


def parse_feature_csv(file_path: str) -> Tuple[Dict[str, str], List[Dict]]:
    """
    Parse feature CSV file.
    
    Expected format: Same as canonical template + 'features' column
    employee_code,employee_name,email,department,pod,product,feature_name,contribution_month,effort_hours,description,features
    
    Returns:
        Tuple of (employee_features_dict, errors)
        employee_features_dict: {employee_code: "Feature1, Feature2, Feature3"}
    """
    employee_features = {}
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
        
        # Check if features column exists
        if 'features' not in df.columns:
            errors.append({
                'row': 0,
                'field': 'headers',
                'message': "Missing required column: 'features'"
            })
            return employee_features, errors
        
        # Group by employee_code and collect features
        for idx, row in df.iterrows():
            row_num = idx + 2  # CSV row number (1-indexed + header)
            
            employee_code = str(row.get('employee_code', '')).strip()
            features = str(row.get('features', '')).strip() if pd.notna(row.get('features')) else ''
            
            if not employee_code:
                errors.append({
                    'row': row_num,
                    'field': 'employee_code',
                    'message': 'employee_code is required'
                })
                continue
            
            # Collect features for this employee
            if employee_code not in employee_features:
                employee_features[employee_code] = []
            
            if features:
                # Split features by comma and clean
                feature_list = [f.strip() for f in features.split(',') if f.strip()]
                employee_features[employee_code].extend(feature_list)
        
        # Deduplicate and join features per employee
        for emp_code in employee_features:
            unique_features = list(set(employee_features[emp_code]))
            employee_features[emp_code] = ', '.join(unique_features)
    
    except Exception as e:
        errors.append({
            'row': 0,
            'field': 'file',
            'message': f"Error parsing file: {str(e)}"
        })
    
    return employee_features, errors

