"""Service for parsing initial XLSX file with product/description data."""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime, date
from decimal import Decimal
from contributions.exceptions import ValidationException


def parse_initial_xlsx(file_path: str) -> Tuple[Dict[str, Dict], List[Dict]]:
    """
    Parse initial XLSX file with format:
    employee_code, employee_name, email, department, pod, product, 
    description, contribution_month, effort_hours
    
    Returns:
        Tuple of (employee_data, errors)
        employee_data: {
            'EMP001': {
                'employee_code': 'EMP001',
                'employee_name': 'John Doe',
                'email': 'john@example.com',
                'department': 'Tech',
                'pod': 'Platform Pod',
                'products': [
                    {
                        'product': 'Academy',
                        'description': 'Feature X',
                        'contribution_month': '2025-10',
                        'effort_hours': 16
                    },
                    ...
                ]
            }
        }
    """
    employee_data = {}
    errors = []
    
    try:
        # Check if file is actually Excel (even if extension is .csv)
        is_excel = False
        try:
            with open(file_path, 'rb') as f:
                header = f.read(2)
                if header == b'PK':
                    is_excel = True
        except:
            pass
        
        if is_excel:
            # Handle Excel file
            excel_file = pd.ExcelFile(file_path)
            
            # Process ONLY sub-sheets (Tech, Finance, Sales, Marketing, Business)
            # Master sheet is explicitly skipped - we only process team/department sheets
            sub_sheets = [name for name in excel_file.sheet_names if name.lower() != 'master']
            
            if not sub_sheets:
                errors.append({
                    'sheet': 'File',
                    'row': 0,
                    'field': 'sheets',
                    'message': 'No valid sheets found (only Master sheet exists). Expected sub-sheets: Tech, Finance, Sales, Marketing, Business'
                })
                return employee_data, errors
            
            # Process each team/department sub-sheet
            for sheet_name in sub_sheets:
                
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Normalize column names
                df.columns = [col.strip().lower() for col in df.columns]
                
                # Required columns
                required_columns = ['employee_code', 'product', 'description', 'contribution_month']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    errors.append({
                        'sheet': sheet_name,
                        'row': 0,
                        'field': 'headers',
                        'message': f"Missing required columns: {', '.join(missing_columns)}"
                    })
                    continue
                
                # Process each row
                for idx, row in df.iterrows():
                    row_num = idx + 2  # Excel row number (1-indexed + header)
                    row_errors = []
                    
                    # Extract fields
                    employee_code = str(row.get('employee_code', '')).strip()
                    employee_name = str(row.get('employee_name', '')).strip() if pd.notna(row.get('employee_name')) else ''
                    email = str(row.get('email', '')).strip() if pd.notna(row.get('email')) else ''
                    department = str(row.get('department', '')).strip() if pd.notna(row.get('department')) else ''
                    pod = str(row.get('pod', '')).strip() if pd.notna(row.get('pod')) else ''
                    product = str(row.get('product', '')).strip()
                    description = str(row.get('description', '')).strip() if pd.notna(row.get('description')) else ''
                    contribution_month = str(row.get('contribution_month', '')).strip()
                    effort_hours = row.get('effort_hours', 0)
                    
                    # Validate required fields
                    if not employee_code:
                        row_errors.append({
                            'sheet': sheet_name,
                            'row': row_num,
                            'field': 'employee_code',
                            'message': 'employee_code is required'
                        })
                    if not product:
                        row_errors.append({
                            'sheet': sheet_name,
                            'row': row_num,
                            'field': 'product',
                            'message': 'product is required'
                        })
                    if not contribution_month:
                        row_errors.append({
                            'sheet': sheet_name,
                            'row': row_num,
                            'field': 'contribution_month',
                            'message': 'contribution_month is required'
                        })
                    
                    # Normalize month format
                    month_str = None
                    if contribution_month:
                        try:
                            # Try various formats
                            if len(contribution_month) == 7 and '-' in contribution_month:
                                # YYYY-MM format
                                month_str = contribution_month
                            else:
                                # Try parsing as date
                                if '/' in contribution_month:
                                    month_date = datetime.strptime(contribution_month, '%Y/%m/%d')
                                elif '-' in contribution_month:
                                    month_date = datetime.strptime(contribution_month, '%Y-%m-%d')
                                else:
                                    month_date = datetime.strptime(contribution_month, '%Y%m%d')
                                month_str = month_date.strftime('%Y-%m')
                        except:
                            row_errors.append({
                                'sheet': sheet_name,
                                'row': row_num,
                                'field': 'contribution_month',
                                'message': f'Invalid month format: {contribution_month}'
                            })
                    
                    if row_errors:
                        errors.extend(row_errors)
                    else:
                        # Initialize employee data if not exists
                        if employee_code not in employee_data:
                            employee_data[employee_code] = {
                                'employee_code': employee_code,
                                'employee_name': employee_name,
                                'email': email,
                                'department': department,
                                'pod': pod,
                                'products': []
                            }
                        
                        # Convert effort_hours to Decimal
                        try:
                            hours = Decimal(str(effort_hours)) if pd.notna(effort_hours) else Decimal('0')
                        except:
                            hours = Decimal('0')
                        
                        employee_data[employee_code]['products'].append({
                            'product': product,
                            'description': description,
                            'contribution_month': month_str,
                            'effort_hours': hours
                        })
        else:
            # Handle CSV file
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
            required_columns = ['employee_code', 'product', 'description', 'contribution_month']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                errors.append({
                    'sheet': 'CSV',
                    'row': 0,
                    'field': 'headers',
                    'message': f"Missing required columns: {', '.join(missing_columns)}"
                })
            else:
                # Process each row (similar to Excel processing)
                for idx, row in df.iterrows():
                    row_num = idx + 2
                    employee_code = str(row.get('employee_code', '')).strip()
                    employee_name = str(row.get('employee_name', '')).strip() if pd.notna(row.get('employee_name')) else ''
                    email = str(row.get('email', '')).strip() if pd.notna(row.get('email')) else ''
                    department = str(row.get('department', '')).strip() if pd.notna(row.get('department')) else ''
                    pod = str(row.get('pod', '')).strip() if pd.notna(row.get('pod')) else ''
                    product = str(row.get('product', '')).strip()
                    description = str(row.get('description', '')).strip() if pd.notna(row.get('description')) else ''
                    contribution_month = str(row.get('contribution_month', '')).strip()
                    effort_hours = row.get('effort_hours', 0)
                    
                    if employee_code and product and contribution_month:
                        if employee_code not in employee_data:
                            employee_data[employee_code] = {
                                'employee_code': employee_code,
                                'employee_name': employee_name,
                                'email': email,
                                'department': department,
                                'pod': pod,
                                'products': []
                            }
                        
                        # Normalize month
                        try:
                            if len(contribution_month) == 7 and '-' in contribution_month:
                                month_str = contribution_month
                            else:
                                month_date = datetime.strptime(contribution_month, '%Y-%m-%d')
                                month_str = month_date.strftime('%Y-%m')
                        except:
                            month_str = contribution_month
                        
                        try:
                            hours = Decimal(str(effort_hours)) if pd.notna(effort_hours) else Decimal('0')
                        except:
                            hours = Decimal('0')
                        
                        employee_data[employee_code]['products'].append({
                            'product': product,
                            'description': description,
                            'contribution_month': month_str,
                            'effort_hours': hours
                        })
    
    except Exception as e:
        errors.append({
            'sheet': 'File',
            'row': 0,
            'field': 'file',
            'message': f"Error parsing file: {str(e)}"
        })
    
    return employee_data, errors

