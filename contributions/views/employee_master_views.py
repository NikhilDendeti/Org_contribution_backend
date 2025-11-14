"""Views for employee master import."""
from rest_framework.views import APIView
from rest_framework.request import Request
from django.conf import settings
from pathlib import Path
from contributions.interactors.employee_master_import_interactor import ImportEmployeeMasterInteractor
from contributions.presenters.upload_presenter import present_upload_result, present_upload_error
from contributions.presenters.error_presenter import present_error
from contributions.common.response import success_response
from contributions.utils.auth_middleware import get_employee_from_request
from contributions.services import permission_service
from contributions.exceptions import DomainException, PermissionDeniedException


class ImportEmployeeMasterView(APIView):
    """View for importing employee master CSV."""
    
    def post(self, request: Request):
        """Handle employee master CSV import."""
        try:
            # Get employee from token
            employee = get_employee_from_request(request)
            
            # Check admin/CEO permission
            if not (employee.role == 'ADMIN' or employee.role == 'CEO'):
                raise PermissionDeniedException("Only ADMIN or CEO can import employee master data")
            
            # Check if file is present
            if 'file' not in request.FILES:
                return success_response(
                    data={'error': 'No file provided'},
                    message='File upload failed',
                    status_code=400
                )
            
            file = request.FILES['file']
            
            # Save file temporarily
            upload_dir = Path(settings.MEDIA_ROOT) / 'temp'
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            temp_file_path = upload_dir / f"{timestamp}_{file.name}"
            
            with open(temp_file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            
            # Execute import interactor
            interactor = ImportEmployeeMasterInteractor(str(temp_file_path))
            result = interactor.execute()
            
            # Clean up temp file
            temp_file_path.unlink()
            
            # Present result
            response_data = {
                'summary': result['summary'],
                'errors': result.get('errors', []),
                'has_errors': result.get('has_errors', False)
            }
            return success_response(data=response_data, message='Employee master imported successfully')
        
        except PermissionDeniedException as e:
            return present_error(e)
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Import failed: {str(e)}"))

