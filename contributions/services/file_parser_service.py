"""File parser service for parsing Excel/CSV contribution files."""
import pandas as pd
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Tuple
from pathlib import Path
import re
from contributions.exceptions import InvalidFileFormatException, ValidationException


def parse_excel_file(file_path: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Parse Excel or CSV file and return parsed rows and errors.
    
    Args:
        file_path: Path to Excel or CSV file
    
    Returns:
        Tuple of (parsed_rows, errors)
    """
    try:
        file_path_obj = Path(file_path)
        all_rows = []
        all_errors = []
        
        # Detect file type - check if it's actually Excel even if extension is .csv
        is_excel = False
        if file_path_obj.suffix.lower() in ['.xlsx', '.xls']:
            is_excel = True
        else:
            # Check if file is actually Excel by reading first bytes
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(8)
                    # Excel files start with PK (ZIP signature)
                    if header[:2] == b'PK':
                        is_excel = True
            except:
                pass
        
        if not is_excel:
            # Handle CSV file - try different encodings
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file_path, encoding='latin-1')
                except:
                    df = pd.read_csv(file_path, encoding='cp1252')
            
            # Validate headers - feature_name, reported_by, and source are optional
            required_columns = [
                'employee_code', 'employee_name', 'email', 'department', 'pod',
                'product', 'contribution_month', 'effort_hours'
            ]
            optional_columns = ['feature_name', 'description', 'reported_by', 'source']
            
            # Normalize column names (case-insensitive, strip whitespace)
            df.columns = [col.strip().lower() for col in df.columns]
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                all_errors.append({
                    'sheet': 'CSV',
                    'row': 0,
                    'field': 'headers',
                    'message': f"Missing required columns: {', '.join(missing_columns)}"
                })
            else:
                # Process each row
                for idx, row in df.iterrows():
                    row_num = idx + 2  # CSV row number (1-indexed + header)
                    normalized_row = normalize_row(row, df.columns)
                    
                    # Validate row
                    validation_errors = validate_row(normalized_row, row_num, 'CSV')
                    if validation_errors:
                        all_errors.extend(validation_errors)
                    else:
                        all_rows.append(normalized_row)
        else:
            # Handle Excel file
            excel_file = pd.ExcelFile(file_path)
            
            # Skip "Master" sheet if it exists (it's usually a summary)
            sheets_to_process = [s for s in excel_file.sheet_names if s.lower() != 'master']
            if not sheets_to_process:
                # If only Master sheet exists, process it anyway
                sheets_to_process = excel_file.sheet_names
            
            for sheet_name in sheets_to_process:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Validate headers - feature_name, reported_by, and source are optional
                required_columns = [
                    'employee_code', 'employee_name', 'email', 'department', 'pod',
                    'product', 'contribution_month', 'effort_hours'
                ]
                optional_columns = ['feature_name', 'description', 'reported_by', 'source']
                
                # Normalize column names (case-insensitive, strip whitespace)
                df.columns = [col.strip().lower() for col in df.columns]
                
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    all_errors.append({
                        'sheet': sheet_name,
                        'row': 0,
                        'field': 'headers',
                        'message': f"Missing required columns: {', '.join(missing_columns)}"
                    })
                    continue
                
                # Process each row
                for idx, row in df.iterrows():
                    row_num = idx + 2  # Excel row number (1-indexed + header)
                    normalized_row = normalize_row(row, df.columns)
                    
                    # Validate row
                    validation_errors = validate_row(normalized_row, row_num, sheet_name)
                    if validation_errors:
                        all_errors.extend(validation_errors)
                    else:
                        all_rows.append(normalized_row)
        
        return all_rows, all_errors
    
    except Exception as e:
        raise InvalidFileFormatException(f"Error parsing file: {str(e)}")


def normalize_row(row: pd.Series, headers: List[str]) -> Dict:
    """Normalize a row to canonical format."""
    normalized = {}
    for header in headers:
        value = row.get(header, '')
        # Convert to string and strip whitespace
        if pd.isna(value):
            normalized[header] = ''
        else:
            normalized[header] = str(value).strip()
    return normalized


def validate_row(row_dict: Dict, row_num: int, sheet_name: str) -> List[Dict]:
    """Validate a row and return list of errors."""
    errors = []
    
    # Required fields
    required_fields = [
        'employee_code', 'employee_name', 'email', 'department', 'pod',
        'product', 'contribution_month', 'effort_hours'
    ]
    
    for field in required_fields:
        if not row_dict.get(field) or row_dict[field] == '':
            errors.append({
                'sheet': sheet_name,
                'row': row_num,
                'field': field,
                'message': f"{field} is required"
            })
    
    # Validate email format
    email = row_dict.get('email', '')
    if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        errors.append({
            'sheet': sheet_name,
            'row': row_num,
            'field': 'email',
            'message': f"Invalid email format: {email}"
        })
    
    # Validate contribution_month format (YYYY-MM)
    month_str = row_dict.get('contribution_month', '')
    if month_str:
        try:
            # Try parsing as YYYY-MM
            if isinstance(month_str, str):
                if not re.match(r'^\d{4}-\d{2}$', month_str):
                    errors.append({
                        'sheet': sheet_name,
                        'row': row_num,
                        'field': 'contribution_month',
                        'message': f"Invalid month format: {month_str}. Expected YYYY-MM"
                    })
        except Exception:
            errors.append({
                'sheet': sheet_name,
                'row': row_num,
                'field': 'contribution_month',
                'message': f"Invalid month format: {month_str}"
            })
    
    # Validate effort_hours (numeric, non-negative)
    hours_str = row_dict.get('effort_hours', '')
    if hours_str:
        try:
            hours = Decimal(str(hours_str))
            if hours < 0:
                errors.append({
                    'sheet': sheet_name,
                    'row': row_num,
                    'field': 'effort_hours',
                    'message': f"effort_hours must be non-negative: {hours}"
                })
        except (ValueError, InvalidOperation):
            errors.append({
                'sheet': sheet_name,
                'row': row_num,
                'field': 'effort_hours',
                'message': f"Invalid effort_hours: {hours_str}. Must be numeric"
            })
    
    return errors


def normalize_month(month_str: str) -> date:
    """Convert YYYY-MM string to first-of-month Date."""
    try:
        # Parse YYYY-MM format
        year, month = map(int, month_str.split('-'))
        return date(year, month, 1)
    except (ValueError, AttributeError):
        raise ValidationException(f"Invalid month format: {month_str}. Expected YYYY-MM")


def generate_errors_csv(errors: List[Dict]) -> str:
    """Generate CSV content from errors."""
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['sheet', 'row', 'field', 'message'])
    
    # Write errors
    for error in errors:
        writer.writerow([
            error.get('sheet', ''),
            error.get('row', ''),
            error.get('field', ''),
            error.get('message', '')
        ])
    
    return output.getvalue()

