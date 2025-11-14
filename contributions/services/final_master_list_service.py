"""Service for generating final master list from processed allocations."""
import pandas as pd
from pathlib import Path
from datetime import date
from decimal import Decimal
from typing import Dict
from django.conf import settings
from contributions.storages import pod_lead_allocation_storage, employee_storage, department_storage


def generate_final_master_list(month: date) -> Path:
    """
    Generate final master list combining all teams/pods/employees.
    
    Format:
    employee_code, employee_name, email, department, pod, product, 
    description, contribution_month, effort_hours
    
    Steps:
    1. Get all PROCESSED allocations for month
    2. For each allocation:
       - Calculate effort_hours = (percent / 100) * baseline_hours
       - Create row with product-specific data
    3. Combine all rows
    4. Generate XLSX with multiple sheets (one per department)
    5. Save to media/final_master_lists/
    
    Returns:
        Path to generated master list file
    """
    # Get all processed allocations
    allocations = pod_lead_allocation_storage.get_processed_allocations_by_month(month)
    
    if not allocations:
        raise ValueError(f"No processed allocations found for month {month.strftime('%Y-%m')}")
    
    # Group by department
    department_data = {}
    
    for alloc in allocations:
        employee = employee_storage.get_employee_by_id(alloc.employee_id)
        dept_name = employee.department_name or 'Unknown'
        
        if dept_name not in department_data:
            department_data[dept_name] = []
        
        # Calculate hours for each product with non-zero percentage
        products = [
            ('Academy', alloc.academy_percent),
            ('Intensive', alloc.intensive_percent),
            ('NIAT', alloc.niat_percent),
        ]
        
        for product_name, percent in products:
            if percent > Decimal('0'):
                hours = (percent / Decimal('100')) * alloc.baseline_hours
                department_data[dept_name].append({
                    'employee_code': alloc.employee_code,
                    'employee_name': alloc.employee_name,
                    'email': employee.email,
                    'department': dept_name,
                    'pod': employee.pod_name or '',
                    'product': product_name,
                    'description': alloc.product_description or '',
                    'contribution_month': month.strftime('%Y-%m'),
                    'effort_hours': float(hours)
                })
    
    # Create directory if it doesn't exist
    master_list_dir = Path(settings.MEDIA_ROOT) / 'final_master_lists'
    master_list_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    month_str = month.strftime('%Y-%m')
    filename = f"final_master_list_{month_str}.xlsx"
    file_path = master_list_dir / filename
    
    # Check if file already exists - reuse it to prevent duplicates
    if file_path.exists():
        # File exists, return existing path (no overwrite)
        return file_path
    
    # Generate XLSX with multiple sheets (one per department)
    headers = [
        'employee_code', 'employee_name', 'email', 'department', 'pod',
        'product', 'description', 'contribution_month', 'effort_hours'
    ]
    
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        # Create Master sheet with all data
        all_data = []
        for dept_name, rows in department_data.items():
            all_data.extend(rows)
        
        if all_data:
            master_df = pd.DataFrame(all_data, columns=headers)
            master_df.to_excel(writer, sheet_name='Master', index=False)
        
        # Create sheet for each department
        for dept_name, rows in department_data.items():
            if rows:
                dept_df = pd.DataFrame(rows, columns=headers)
                # Clean sheet name (Excel has 31 char limit)
                sheet_name = dept_name[:31] if len(dept_name) <= 31 else dept_name[:28] + '...'
                dept_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return file_path

