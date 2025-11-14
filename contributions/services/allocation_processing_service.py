"""Service for processing Pod Lead allocations."""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import List, Dict
from pathlib import Path
import pandas as pd
from django.conf import settings
from contributions.exceptions import ValidationException
from contributions.storages.storage_dto import PodLeadAllocationDTO


def validate_allocation_percentages(
    academy_percent: Decimal,
    intensive_percent: Decimal,
    niat_percent: Decimal
) -> bool:
    """
    Validate that allocation percentages sum to <= 100%.
    
    Raises:
        ValidationException if sum > 100%
    """
    total = academy_percent + intensive_percent + niat_percent
    if total > Decimal('100.00'):
        raise ValidationException(
            f"Total percentage exceeds 100%. Got: {total}%"
        )
    return True


def calculate_hours_from_percentage(percent: Decimal, baseline_hours: Decimal) -> Decimal:
    """Calculate hours from percentage and baseline hours."""
    if percent == Decimal('0'):
        return Decimal('0')
    hours = (percent / Decimal('100')) * baseline_hours
    return hours.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def process_allocation_to_records(
    allocation: PodLeadAllocationDTO,
    source_file_id: int
) -> List[Dict]:
    """
    Convert allocation percentages to ContributionRecord entries.
    
    Returns:
        List of ContributionRecordDTO dicts ready for creation
    """
    from contributions.storages import (
        product_storage, contribution_storage
    )
    
    records = []
    
    # Get product IDs
    academy = product_storage.get_product_by_name('Academy')
    intensive = product_storage.get_product_by_name('Intensive')
    niat = product_storage.get_product_by_name('NIAT')
    
    # Process each product with non-zero percentage
    products = [
        (academy.id, allocation.academy_percent),
        (intensive.id, allocation.intensive_percent),
        (niat.id, allocation.niat_percent),
    ]
    
    for product_id, percent in products:
        if percent > Decimal('0'):
            hours = calculate_hours_from_percentage(percent, allocation.baseline_hours)
            records.append({
                'employee_id': allocation.employee_id,
                'department_id': None,  # Will be filled from employee
                'pod_id': None,  # Will be filled from employee
                'product_id': product_id,
                'feature_id': None,
                'contribution_month': allocation.contribution_month,
                'effort_hours': hours,
                'description': f"Allocated {percent}% via Pod Lead allocation",
                'source_file_id': source_file_id,
            })
    
    return records


def process_allocation_to_csv(
    allocations: List[PodLeadAllocationDTO],
    month: date
) -> Path:
    """
    Generate CSV in canonical template format from allocations.
    
    Returns:
        Path to generated CSV file
    """
    from contributions.storages import employee_storage, product_storage
    
    # Get product IDs
    academy = product_storage.get_product_by_name('Academy')
    intensive = product_storage.get_product_by_name('Intensive')
    niat = product_storage.get_product_by_name('NIAT')
    
    # Prepare CSV rows
    csv_rows = []
    
    for allocation in allocations:
        # Get employee details
        employee = employee_storage.get_employee_by_id(allocation.employee_id)
        
        # Create rows for each product with non-zero percentage
        products = [
            (academy.id, 'Academy', allocation.academy_percent),
            (intensive.id, 'Intensive', allocation.intensive_percent),
            (niat.id, 'NIAT', allocation.niat_percent),
        ]
        
        for product_id, product_name, percent in products:
            if percent > Decimal('0'):
                hours = calculate_hours_from_percentage(percent, allocation.baseline_hours)
                csv_rows.append({
                    'employee_code': employee.employee_code,
                    'employee_name': employee.name,
                    'email': employee.email,
                    'department': employee.department_name or '',
                    'pod': employee.pod_name or '',
                    'product': product_name,
                    'feature_name': '',
                    'contribution_month': month.strftime('%Y-%m'),
                    'effort_hours': float(hours),
                    'description': f"Allocated {percent}% via Pod Lead allocation",
                    'reported_by': allocation.pod_lead_code or '',
                    'source': f"pod_lead_allocation_{month.strftime('%Y-%m')}"
                })
    
    # Create DataFrame
    headers = [
        'employee_code', 'employee_name', 'email', 'department', 'pod',
        'product', 'feature_name', 'contribution_month', 'effort_hours',
        'description', 'reported_by', 'source'
    ]
    df = pd.DataFrame(csv_rows, columns=headers)
    
    # Save to CSV
    uploads_dir = Path(settings.MEDIA_ROOT) / 'uploads'
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    month_str = month.strftime('%Y-%m')
    filename = f"pod_allocations_{month_str}.csv"
    file_path = uploads_dir / filename
    
    df.to_csv(file_path, index=False)
    
    return file_path


def process_all_pod_allocations(
    pod_id: int,
    month: date,
    output_format: str = 'records'
) -> Dict:
    """
    Process all SUBMITTED allocations for a pod.
    
    Args:
        pod_id: Pod ID
        month: Contribution month
        output_format: 'records' or 'csv'
    
    Returns:
        Dict with processing summary
    """
    from contributions.storages import (
        pod_lead_allocation_storage, contribution_storage, raw_file_storage, employee_storage
    )
    
    # Get submitted allocations
    allocations = pod_lead_allocation_storage.get_submitted_allocations_by_pod(pod_id, month)
    
    if not allocations:
        return {
            'processed_count': 0,
            'message': 'No submitted allocations found'
        }
    
    if output_format == 'records':
        # Create a dummy RawFile for source tracking
        from contributions.storages import employee_storage, raw_file_storage
        pod_lead = employee_storage.get_employee_by_id(allocations[0].pod_lead_id)
        
        raw_file = raw_file_storage.create_raw_file(
            file_name=f"pod_allocations_{month.strftime('%Y-%m')}.csv",
            storage_path=f"allocations/pod_{pod_id}_{month.strftime('%Y-%m')}.csv",
            uploaded_by_id=pod_lead.id,
            file_size=0,
            checksum='',
            parse_summary={'source': 'pod_lead_allocation', 'pod_id': pod_id, 'month': month.strftime('%Y-%m')}
        )
        
        # Process each allocation to records
        created_records = 0
        for allocation in allocations:
            records = process_allocation_to_records(allocation, raw_file.id)
            
            for record_data in records:
                # Get employee to fill department/pod
                employee = employee_storage.get_employee_by_id(allocation.employee_id)
                record_data['department_id'] = employee.department_id
                record_data['pod_id'] = employee.pod_id
                
                # Create contribution record
                contribution_storage.create_contribution_record(
                    **record_data
                )
                created_records += 1
            
            # Mark allocation as processed
            pod_lead_allocation_storage.mark_allocation_processed(allocation.id)
        
        return {
            'processed_count': len(allocations),
            'created_records': created_records,
            'output_format': 'records'
        }
    
    else:  # CSV format
        # Generate CSV
        csv_path = process_allocation_to_csv(allocations, month)
        
        # Mark allocations as processed
        for allocation in allocations:
            pod_lead_allocation_storage.mark_allocation_processed(allocation.id)
        
        return {
            'processed_count': len(allocations),
            'csv_path': str(csv_path.relative_to(Path(settings.MEDIA_ROOT))),
            'output_format': 'csv'
        }

