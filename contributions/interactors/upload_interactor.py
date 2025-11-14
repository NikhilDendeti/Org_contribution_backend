"""Upload interactor for handling file uploads."""
from datetime import date
from decimal import Decimal
from django.db import transaction
from django.conf import settings
from pathlib import Path
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
        # Check if file is a path string (for management commands)
        if isinstance(self.file, str):
            full_path = Path(self.file)
            if not full_path.is_absolute():
                full_path = Path(settings.BASE_DIR) / full_path
            
            # Calculate storage path relative to MEDIA_ROOT
            try:
                storage_path = str(full_path.relative_to(Path(settings.MEDIA_ROOT)))
            except ValueError:
                # File is outside MEDIA_ROOT, use filename in uploads directory
                storage_path = f"uploads/{full_path.name}"
            
            file_size = full_path.stat().st_size
            import hashlib
            with open(full_path, 'rb') as f:
                checksum = hashlib.md5(f.read()).hexdigest()
            file_name = full_path.name
            
            # Check for duplicate file before processing
            existing_file = raw_file_storage.get_raw_file_by_checksum(checksum)
            if existing_file:
                from contributions.exceptions import DuplicateUploadException
                raise DuplicateUploadException(
                    f"File with same content already exists: {existing_file.file_name} "
                    f"(uploaded at {existing_file.uploaded_at}). Use existing file ID: {existing_file.id}"
                )
        else:
            # Read file content first to calculate checksum before saving
            file_content = b''
            if hasattr(self.file, 'read'):
                self.file.seek(0)
                file_content = self.file.read()
                self.file.seek(0)
            elif hasattr(self.file, 'chunks'):
                for chunk in self.file.chunks():
                    file_content += chunk
            
            # Calculate checksum from content
            import hashlib
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(file_content)
                tmp_path = Path(tmp_file.name)
                checksum = hashlib.md5(file_content).hexdigest()
                tmp_path.unlink()
            
            # Check for duplicate BEFORE saving
            existing_file = raw_file_storage.get_raw_file_by_checksum(checksum)
            if existing_file:
                from contributions.exceptions import DuplicateUploadException
                raise DuplicateUploadException(
                    f"File with same content already exists: {existing_file.file_name} "
                    f"(uploaded at {existing_file.uploaded_at}). Use existing file ID: {existing_file.id}"
                )
            
            # Save uploaded file (duplicate check already done)
            storage_path, file_size, checksum = file_storage_service.save_uploaded_file(
                self.file, 
                check_duplicate=False  # Already checked above
            )
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
        
        # Create raw file record (duplicate check already done above)
        raw_file = raw_file_storage.create_raw_file(
            file_name=file_name,
            storage_path=storage_path,
            uploaded_by_id=self.uploaded_by_id,
            file_size=file_size,
            checksum=checksum,
            check_duplicate=False,  # Already checked above
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

