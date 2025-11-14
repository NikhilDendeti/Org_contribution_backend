"""Service for generating Pod Lead allocation sheets."""
import pandas as pd
from pathlib import Path
from datetime import date
from typing import List, Dict, Optional
from django.conf import settings
from contributions.storages import employee_storage, pod_storage


def generate_pod_lead_allocation_sheets(
    pod_id: int,
    month: date,
    employee_product_data: Dict[str, List[Dict]]
) -> Path:
    """
    Generate Excel sheet for Pod Lead allocation with NEW format.
    
    Sheet format:
    employee_code, employee_name, email, department, pod, product_description, 
    product, contribution_month, Academy_product_contribution (%), 
    Intensive_product_contribution (%), NIAT_product_contribution (%), 
    is_verified_description
    
    One row per employee-product combination
    
    Returns:
        Path to generated sheet file
    """
    # Get pod details
    pod = pod_storage.get_pod_by_id(pod_id)
    
    # Get all employees in the pod
    employees = employee_storage.list_employees_by_pod(pod_id)
    
    # Prepare sheet data
    sheet_data = []
    for emp in employees:
        products = employee_product_data.get(emp.employee_code, [])
        
        if not products:
            # If no products, create one empty row
            sheet_data.append({
                'employee_code': emp.employee_code,
                'employee_name': emp.name,
                'email': emp.email,
                'department': emp.department_name or '',
                'pod': emp.pod_name or '',
                'product_description': '',
                'product': '',
                'contribution_month': month.strftime('%Y-%m'),
                'Academy_product_contribution': '',
                'Intensive_product_contribution': '',
                'NIAT_product_contribution': '',
                'is_verified_description': False
            })
        else:
            # One row per product
            for product_data in products:
                sheet_data.append({
                    'employee_code': emp.employee_code,
                    'employee_name': emp.name,
                    'email': emp.email,
                    'department': emp.department_name or '',
                    'pod': emp.pod_name or '',
                    'product_description': product_data.get('description', ''),
                    'product': product_data.get('product', ''),
                    'contribution_month': product_data.get('contribution_month', month.strftime('%Y-%m')),
                    'Academy_product_contribution': '',
                    'Intensive_product_contribution': '',
                    'NIAT_product_contribution': '',
                    'is_verified_description': False
                })
    
    # Create DataFrame
    df = pd.DataFrame(sheet_data)
    
    # Create directory if it doesn't exist
    sheet_dir = Path(settings.MEDIA_ROOT) / 'pod_lead_sheets'
    sheet_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    month_str = month.strftime('%Y-%m')
    filename = f"pod_{pod_id}_allocation_{month_str}.xlsx"
    file_path = sheet_dir / filename
    
    # Check if file already exists - reuse it to prevent duplicates
    if file_path.exists():
        # File exists, return existing path (no overwrite)
        return file_path
    
    # Save to Excel
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=f'{pod.name}', index=False)
    
    return file_path


def get_sheet_download_url(file_path: Path) -> str:
    """Generate download URL for sheet."""
    relative_path = file_path.relative_to(Path(settings.MEDIA_ROOT))
    return f"{settings.MEDIA_URL}{relative_path}"


def save_sheet_to_storage(file_path: Path) -> str:
    """Save sheet and return storage path."""
    relative_path = file_path.relative_to(Path(settings.MEDIA_ROOT))
    return str(relative_path)

