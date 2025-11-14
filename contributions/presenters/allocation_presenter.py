"""Presenter for allocation responses."""
from contributions.storages.storage_dto import PodLeadAllocationDTO
from typing import List


def present_allocation_sheet(sheet_path: str, download_url: str, pod_id: int, pod_name: str) -> dict:
    """Present allocation sheet data."""
    return {
        'pod_id': pod_id,
        'pod_name': pod_name,
        'sheet_path': sheet_path,
        'download_url': download_url
    }


def present_allocation_submission(result: dict) -> dict:
    """Present allocation submission result."""
    return {
        'summary': result['summary'],
        'allocations': [
            {
                'id': alloc.id,
                'employee_id': alloc.employee_id,
                'employee_code': alloc.employee_code,
                'employee_name': alloc.employee_name,
                'product': alloc.product,
                'product_description': alloc.product_description,
                'academy_percent': float(alloc.academy_percent),
                'intensive_percent': float(alloc.intensive_percent),
                'niat_percent': float(alloc.niat_percent),
                'is_verified_description': alloc.is_verified_description,
                'status': alloc.status
            }
            for alloc in result['allocations']
        ],
        'errors': result.get('errors', []),
        'has_errors': result.get('has_errors', False)
    }


def present_allocation_list(allocations: List[PodLeadAllocationDTO]) -> List[dict]:
    """Present allocation list."""
    return [
        {
            'id': alloc.id,
            'employee_id': alloc.employee_id,
            'employee_code': alloc.employee_code,
            'employee_name': alloc.employee_name,
            'email': '',  # Will be filled from employee if needed
            'academy_percent': float(alloc.academy_percent),
            'intensive_percent': float(alloc.intensive_percent),
            'niat_percent': float(alloc.niat_percent),
            'product': alloc.product,
            'product_description': alloc.product_description,
            'features_text': alloc.features_text,
            'is_verified_description': alloc.is_verified_description,
            'baseline_hours': float(alloc.baseline_hours),
            'status': alloc.status,
            'total_percent': float(alloc.academy_percent + alloc.intensive_percent + alloc.niat_percent)
        }
        for alloc in allocations
    ]


def present_processing_result(result: dict) -> dict:
    """Present processing result."""
    return {
        'processed_count': result.get('processed_count', 0),
        'output_format': result.get('output_format', 'records'),
        'created_records': result.get('created_records', 0),
        'csv_path': result.get('csv_path'),
        'message': result.get('message', 'Processing completed')
    }

