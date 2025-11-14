"""Interactor for importing employee master CSV."""
from pathlib import Path
from django.conf import settings
from contributions.services import employee_master_import_service
from contributions.exceptions import ValidationException, DomainException


class ImportEmployeeMasterInteractor:
    """Interactor for importing employee master CSV."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def execute(self) -> dict:
        """Execute the import process."""
        # Resolve file path
        if not Path(self.file_path).is_absolute():
            file_path = Path(settings.BASE_DIR) / self.file_path
        else:
            file_path = Path(self.file_path)
        
        if not file_path.exists():
            raise DomainException(f"File not found: {file_path}")
        
        # Parse CSV
        parsed_rows, errors = employee_master_import_service.parse_employee_master_csv(str(file_path))
        
        if errors:
            # Check if all rows had errors
            if not parsed_rows:
                raise ValidationException("All rows failed validation", errors={'rows': errors})
        
        # Import employees
        summary = employee_master_import_service.import_employees(parsed_rows)
        
        return {
            'summary': summary,
            'errors': errors if errors else [],
            'has_errors': len(errors) > 0
        }

