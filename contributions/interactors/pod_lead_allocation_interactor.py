"""Interactor for Pod Lead allocation submission."""
from datetime import datetime, date
from decimal import Decimal
from contributions.services import allocation_processing_service
from contributions.storages import pod_lead_allocation_storage, employee_storage
from contributions.exceptions import ValidationException, PermissionDeniedException


class SubmitPodLeadAllocationInteractor:
    """Interactor for submitting Pod Lead allocations."""
    
    def __init__(self, pod_id: int, month: str, allocations: list, pod_lead_id: int):
        self.pod_id = pod_id
        self.month = month
        # allocations format:
        # [
        #   {
        #     'employee_id': 1,
        #     'product': 'Academy',
        #     'product_description': 'Feature X',
        #     'academy_percent': 40,
        #     'intensive_percent': 30,
        #     'niat_percent': 30,
        #     'is_verified_description': True
        #   }
        # ]
        self.allocations = allocations
        self.pod_lead_id = pod_lead_id
    
    def execute(self) -> dict:
        """Execute the allocation submission."""
        # Validate month format
        try:
            month_date = datetime.strptime(self.month, '%Y-%m').date()
            month_date = date(month_date.year, month_date.month, 1)
        except ValueError:
            raise ValidationException(f"Invalid month format: {self.month}. Expected YYYY-MM")
        
        # Verify Pod Lead has access to this pod
        pod_lead = employee_storage.get_employee_by_id(self.pod_lead_id)
        if pod_lead.role != 'POD_LEAD' or pod_lead.pod_id != self.pod_id:
            raise PermissionDeniedException(
                f"Pod Lead {pod_lead.employee_code} does not have access to pod {self.pod_id}"
            )
        
        updated_allocations = []
        errors = []
        
        # Process each allocation
        for alloc_data in self.allocations:
            employee_id = alloc_data.get('employee_id')
            product = alloc_data.get('product')
            academy_percent = Decimal(str(alloc_data.get('academy_percent', 0)))
            intensive_percent = Decimal(str(alloc_data.get('intensive_percent', 0)))
            niat_percent = Decimal(str(alloc_data.get('niat_percent', 0)))
            is_verified_description = alloc_data.get('is_verified_description', False)
            
            if not product:
                errors.append({
                    'employee_id': employee_id,
                    'message': 'product is required'
                })
                continue
            
            # Validate percentages
            try:
                allocation_processing_service.validate_allocation_percentages(
                    academy_percent, intensive_percent, niat_percent
                )
            except ValidationException as e:
                errors.append({
                    'employee_id': employee_id,
                    'product': product,
                    'message': str(e)
                })
                continue
            
            # Get existing allocation by employee-product-month
            allocation = pod_lead_allocation_storage.get_allocation_by_employee_product_month(
                employee_id,
                product,
                month_date
            )
            
            if not allocation:
                errors.append({
                    'employee_id': employee_id,
                    'product': product,
                    'message': f'Allocation not found for employee {employee_id} and product {product}'
                })
                continue
            
            # Verify this allocation belongs to this Pod Lead
            if allocation.pod_lead_id != self.pod_lead_id:
                errors.append({
                    'employee_id': employee_id,
                    'product': product,
                    'message': 'Allocation does not belong to this Pod Lead'
                })
                continue
            
            # Determine status based on verification
            # Status is SUBMITTED only if description is verified, otherwise PENDING
            allocation_status = 'SUBMITTED' if is_verified_description else 'PENDING'
            
            # Update allocation
            updated = pod_lead_allocation_storage.update_allocation(
                allocation.id,
                academy_percent=academy_percent,
                intensive_percent=intensive_percent,
                niat_percent=niat_percent,
                is_verified_description=is_verified_description,
                status=allocation_status
            )
            
            updated_allocations.append(updated)
        
        return {
            'summary': {
                'updated_allocations': len(updated_allocations),
                'error_count': len(errors)
            },
            'allocations': updated_allocations,
            'errors': errors,
            'has_errors': len(errors) > 0
        }

