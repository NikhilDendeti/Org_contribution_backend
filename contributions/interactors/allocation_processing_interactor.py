"""Interactor for processing Pod Lead allocations."""
from datetime import datetime, date
from contributions.services import allocation_processing_service
from contributions.storages import pod_lead_allocation_storage
from contributions.exceptions import ValidationException


class ProcessPodAllocationsInteractor:
    """Interactor for processing Pod Lead allocations."""
    
    def __init__(self, pod_id: int, month: str, output_format: str = 'records'):
        self.pod_id = pod_id
        self.month = month
        self.output_format = output_format
    
    def execute(self) -> dict:
        """Execute the processing."""
        # Validate month format
        try:
            month_date = datetime.strptime(self.month, '%Y-%m').date()
            month_date = date(month_date.year, month_date.month, 1)
        except ValueError:
            raise ValidationException(f"Invalid month format: {self.month}. Expected YYYY-MM")
        
        # Validate output format
        if self.output_format not in ['records', 'csv']:
            raise ValidationException(f"Invalid output_format: {self.output_format}. Must be 'records' or 'csv'")
        
        # Process allocations
        result = allocation_processing_service.process_all_pod_allocations(
            self.pod_id,
            month_date,
            self.output_format
        )
        
        return result

