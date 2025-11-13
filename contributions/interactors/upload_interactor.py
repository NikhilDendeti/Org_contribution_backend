"""Upload interactor for handling file uploads."""
from datetime import date
from decimal import Decimal
from django.db import transaction
from contributions.services import file_parser_service
from contributions.services import file_storage_service
from contributions.services.file_parser_service import normalize_month
from contributions.storages import (
    department_storage, pod_storage, product_storage, feature_storage,
    employee_storage, raw_file_storage, contribution_storage
)
from contributions.storages.storage_dto import ContributionRecordDTO
from contributions.exceptions import ValidationException, PermissionDeniedException


class UploadContributionFileInteractor:
    """Interactor for uploading and parsing contribution files."""
    
    def __init__(self, file, uploaded_by_id: int):
        self.file = file
        self.uploaded_by_id = uploaded_by_id
    
    def execute(self) -> dict:
        """Execute the upload and parsing process."""
        # Save file
        storage_path, file_size, checksum = file_storage_service.save_uploaded_file(self.file)
        from django.conf import settings
        from pathlib import Path
        full_path = Path(settings.MEDIA_ROOT) / storage_path
        
        # Get file name for raw_file record
        file_name = getattr(self.file, 'name', 'uploaded_file.xlsx')
        if not file_name:
            file_name = 'uploaded_file.xlsx'
        
        # Parse file
        parsed_rows, errors = file_parser_service.parse_excel_file(str(full_path))
        
        if not parsed_rows and errors:
            # All rows had errors
            raise ValidationException("All rows failed validation", errors={'rows': errors})
        
        # Create raw file record
        raw_file = raw_file_storage.create_raw_file(
            file_name=file_name,
            storage_path=storage_path,
            uploaded_by_id=self.uploaded_by_id,
            file_size=file_size,
            checksum=checksum,
        )
        
        # Process rows and create contribution records
        created_records = []
        created_employees = set()
        created_departments = set()
        created_pods = set()
        created_products = set()
        created_features = set()
        
        with transaction.atomic():
            for row in parsed_rows:
                # Upsert entities
                dept = department_storage.get_or_create_department(row['department'])
                if dept.id not in created_departments:
                    created_departments.add(dept.id)
                
                pod = pod_storage.get_or_create_pod(row['pod'], dept.id)
                if pod.id not in created_pods:
                    created_pods.add(pod.id)
                
                product = product_storage.get_or_create_product(row['product'])
                if product.id not in created_products:
                    created_products.add(product.id)
                
                feature = None
                if row.get('feature_name') and row['feature_name'].strip():
                    feature = feature_storage.get_or_create_feature(
                        row['feature_name'],
                        product.id,
                        row.get('description', '')
                    )
                    if feature.id not in created_features:
                        created_features.add(feature.id)
                
                employee = employee_storage.get_or_create_employee(
                    employee_code=row['employee_code'],
                    name=row['employee_name'],
                    email=row['email'],
                    department_id=dept.id,
                    pod_id=pod.id,
                )
                if employee.id not in created_employees:
                    created_employees.add(employee.id)
                
                # Create contribution record DTO
                contribution_month = normalize_month(row['contribution_month'])
                effort_hours = Decimal(str(row['effort_hours']))
                
                record = ContributionRecordDTO(
                    employee_id=employee.id,
                    department_id=dept.id,
                    pod_id=pod.id,
                    product_id=product.id,
                    feature_id=feature.id if feature else None,
                    contribution_month=contribution_month,
                    effort_hours=effort_hours,
                    description=row.get('description', ''),
                    source_file_id=raw_file.id,
                )
                created_records.append(record)
            
            # Bulk create contribution records
            records_created = contribution_storage.bulk_create_contributions(created_records, raw_file.id)
        
        # Update parse summary
        parse_summary = {
            'total_rows': len(parsed_rows),
            'created_records': records_created,
            'created_employees': len(created_employees),
            'created_departments': len(created_departments),
            'created_pods': len(created_pods),
            'created_products': len(created_products),
            'created_features': len(created_features),
            'error_count': len(errors),
            'errors': errors,  # Store errors for download
        }
        
        raw_file_storage.update_raw_file_summary(raw_file.id, parse_summary)
        
        return {
            'raw_file_id': raw_file.id,
            'summary': parse_summary,
            'errors': errors,
        }

