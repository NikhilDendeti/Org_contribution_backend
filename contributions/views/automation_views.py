"""Views for automation user operations."""
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.conf import settings
from pathlib import Path
from contributions.utils.auth_middleware import get_employee_from_request
from contributions.services.permission_service import check_automation_permission
from contributions.interactors.initial_xlsx_upload_interactor import InitialXLSXUploadInteractor
from contributions.common.response import success_response
from contributions.exceptions import ValidationException, DomainException


class UploadInitialXLSXView(APIView):
    """View for automation user to upload initial XLSX."""
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request: Request):
        """Upload initial XLSX and generate Pod Lead sheets."""
        try:
            # Get employee from token
            employee = get_employee_from_request(request)
            
            # Check automation permission
            check_automation_permission(employee.id)
            
            # Get file and month
            file_obj = request.FILES.get('file')
            month = request.data.get('month')
            
            if not file_obj:
                return success_response(
                    data={'error': 'No file provided'},
                    message='File is required',
                    status_code=400
                )
            
            if not month:
                return success_response(
                    data={'error': 'Month parameter is required'},
                    message='Month is required (format: YYYY-MM)',
                    status_code=400
                )
            
            # Save uploaded file temporarily
            upload_dir = Path(settings.MEDIA_ROOT) / 'temp_uploads'
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = upload_dir / file_obj.name
            with open(file_path, 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
            
            # Execute interactor
            interactor = InitialXLSXUploadInteractor(
                file_path=str(file_path),
                month=month
            )
            result = interactor.execute()
            
            # Clean up temp file
            try:
                file_path.unlink()
            except:
                pass
            
            return success_response(
                data=result,
                message='Initial XLSX uploaded and sheets generated successfully'
            )
        
        except ValidationException as e:
            return success_response(
                data={'error': str(e), 'details': getattr(e, 'errors', {})},
                message='Validation error',
                status_code=400
            )
        except DomainException as e:
            return success_response(
                data={'error': str(e)},
                message='Domain error',
                status_code=400
            )
        except Exception as e:
            return success_response(
                data={'error': str(e)},
                message='Unexpected error occurred',
                status_code=500
            )

