"""Interactor for uploading feature CSV and generating Pod Lead allocation sheets."""
from datetime import datetime, date
from pathlib import Path
from django.conf import settings
from contributions.services import feature_csv_parser_service, sheet_generation_service
from contributions.storages import (
    pod_lead_allocation_storage, employee_storage, pod_storage
)
from contributions.exceptions import ValidationException, DomainException


class UploadFeatureCSVInteractor:
    """Interactor for uploading feature CSV and generating allocation sheets."""
    
    def __init__(self, file_path: str, month: str):
        self.file_path = file_path
        self.month = month
    
    def execute(self) -> dict:
        """Execute the upload and sheet generation process."""
        # Validate month format
        try:
            month_date = datetime.strptime(self.month, '%Y-%m').date()
            month_date = date(month_date.year, month_date.month, 1)
        except ValueError:
            raise ValidationException(f"Invalid month format: {self.month}. Expected YYYY-MM")
        
        # Resolve file path
        if not Path(self.file_path).is_absolute():
            file_path = Path(settings.BASE_DIR) / self.file_path
        else:
            file_path = Path(self.file_path)
        
        if not file_path.exists():
            raise DomainException(f"File not found: {file_path}")
        
        # Parse feature CSV
        employee_features, errors = feature_csv_parser_service.parse_feature_csv(str(file_path))
        
        if errors:
            if not employee_features:
                raise ValidationException("Failed to parse feature CSV", errors={'rows': errors})
        
        # Get all pods
        from contributions.storages import pod_storage, department_storage
        departments = department_storage.list_departments()
        
        generated_sheets = []
        created_allocations = 0
        
        # Generate sheets for each pod
        for dept in departments:
            pods = pod_storage.list_pods_by_department(dept.id)
            
            for pod in pods:
                # Get Pod Lead for this pod
                employees = employee_storage.list_employees_by_pod(pod.id)
                pod_lead = None
                for emp in employees:
                    if emp.role == 'POD_LEAD':
                        pod_lead = emp
                        break
                
                if not pod_lead:
                    # Skip pods without Pod Lead
                    continue
                
                # Convert employee_features dict to employee_product_data format
                # For feature CSV upload, we create empty product data structure
                # This is a legacy flow - new flow uses initial XLSX upload
                employee_product_data = {}
                for emp_code, features_text in employee_features.items():
                    # Create empty product entry (will be filled by Pod Lead)
                    employee_product_data[emp_code] = [{
                        'product': '',
                        'description': features_text,
                        'contribution_month': month_date.strftime('%Y-%m'),
                        'effort_hours': 0
                    }]
                
                # Generate sheet
                sheet_path = sheet_generation_service.generate_pod_lead_allocation_sheets(
                    pod.id,
                    month_date,
                    employee_product_data
                )
                
                # Create allocation records for employees in this pod
                for emp in employees:
                    if emp.role == 'EMPLOYEE':  # Only create for regular employees
                        features = employee_features.get(emp.employee_code, '')
                        
                        # Get or create allocation
                        existing = pod_lead_allocation_storage.get_allocations_by_employee_and_month(
                            emp.id, month_date
                        )
                        
                        if not existing:
                            # Get employee baseline hours from model
                            from core.models import Employee
                            from decimal import Decimal
                            emp_model = Employee.objects.get(id=emp.id)
                            baseline_hours = emp_model.monthly_baseline_hours or Decimal('160.00')
                            
                            pod_lead_allocation_storage.create_allocation(
                                employee_id=emp.id,
                                pod_lead_id=pod_lead.id,
                                contribution_month=month_date,
                                features_text=features,
                                baseline_hours=baseline_hours,
                                status='PENDING'
                            )
                            created_allocations += 1
                
                generated_sheets.append({
                    'pod_id': pod.id,
                    'pod_name': pod.name,
                    'pod_lead_code': pod_lead.employee_code,
                    'sheet_path': str(sheet_path.relative_to(Path(settings.MEDIA_ROOT))),
                    'download_url': sheet_generation_service.get_sheet_download_url(sheet_path)
                })
        
        return {
            'summary': {
                'generated_sheets': len(generated_sheets),
                'created_allocations': created_allocations,
                'month': self.month
            },
            'sheets': generated_sheets,
            'errors': errors if errors else [],
            'has_errors': len(errors) > 0
        }

