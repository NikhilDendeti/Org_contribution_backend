"""Upload views."""
from rest_framework.views import APIView
from rest_framework.request import Request
from contributions.interactors.upload_interactor import UploadContributionFileInteractor
from contributions.presenters.upload_presenter import present_upload_result, present_upload_error
from contributions.presenters.error_presenter import present_error
from contributions.common.response import success_response
from contributions.utils.auth_middleware import get_employee_from_request
from contributions.exceptions import DomainException


class UploadContributionFileView(APIView):
    """View for uploading contribution files."""
    
    def post(self, request: Request):
        """Handle file upload."""
        try:
            # Get employee from token
            employee = get_employee_from_request(request)
            
            # Check if file is present
            if 'file' not in request.FILES:
                return success_response(
                    data={'error': 'No file provided'},
                    message='File upload failed',
                    status_code=400
                )
            
            file = request.FILES['file']
            
            # Execute upload interactor
            interactor = UploadContributionFileInteractor(file, employee.id)
            result = interactor.execute()
            
            # Present result
            response_data = present_upload_result(result)
            return success_response(data=response_data, message='File uploaded successfully')
        
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Upload failed: {str(e)}"))

