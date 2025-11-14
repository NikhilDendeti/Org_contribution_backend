"""Views for feature CSV upload."""
from rest_framework.views import APIView
from rest_framework.request import Request
from django.conf import settings
from pathlib import Path
from contributions.interactors.feature_csv_upload_interactor import UploadFeatureCSVInteractor
from contributions.presenters.error_presenter import present_error
from contributions.common.response import success_response
from contributions.utils.auth_middleware import get_employee_from_request
from contributions.exceptions import DomainException, PermissionDeniedException


class UploadFeatureCSVView(APIView):
    """View for uploading feature CSV."""
    
    def post(self, request: Request):
        """Handle feature CSV upload."""
        try:
            # Get employee from token
            employee = get_employee_from_request(request)
            
            # Check admin/CEO permission
            if not (employee.role == 'ADMIN' or employee.role == 'CEO'):
                raise PermissionDeniedException("Only ADMIN or CEO can upload feature CSV")
            
            # Get month parameter
            month = request.data.get('month')
            if not month:
                return success_response(
                    data={'error': 'month parameter is required'},
                    message='Missing required parameter',
                    status_code=400
                )
            
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
            
            # Execute upload interactor
            interactor = UploadFeatureCSVInteractor(str(temp_file_path), month)
            result = interactor.execute()
            
            # Clean up temp file
            temp_file_path.unlink()
            
            # Present result
            return success_response(data=result, message='Feature CSV uploaded and sheets generated successfully')
        
        except PermissionDeniedException as e:
            return present_error(e)
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Upload failed: {str(e)}"))

