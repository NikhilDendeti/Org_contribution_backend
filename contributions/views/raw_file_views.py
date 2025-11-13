"""Raw file views."""
from rest_framework.views import APIView
from rest_framework.request import Request
from django.http import FileResponse, HttpResponse
from contributions.interactors.entity_interactors import GetRawFileInteractor
from contributions.presenters.entity_presenter import present_raw_file
from contributions.presenters.error_presenter import present_error
from contributions.services.file_parser_service import generate_errors_csv
from contributions.services.file_storage_service import get_file_path_by_id
from contributions.common.response import success_response
from contributions.utils.auth_middleware import get_employee_from_request
from contributions.exceptions import DomainException
from pathlib import Path


class GetRawFileView(APIView):
    """Get raw file details view."""
    
    def get(self, request: Request, raw_file_id: int):
        """Get raw file details."""
        try:
            get_employee_from_request(request)  # Just check auth
            
            interactor = GetRawFileInteractor(raw_file_id)
            raw_file = interactor.execute()
            
            response_data = present_raw_file(raw_file)
            return success_response(data=response_data)
        
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to get raw file: {str(e)}"))


class DownloadRawFileView(APIView):
    """Download raw file view."""
    
    def get(self, request: Request, raw_file_id: int):
        """Download original file."""
        try:
            get_employee_from_request(request)  # Just check auth
            
            interactor = GetRawFileInteractor(raw_file_id)
            raw_file = interactor.execute()
            
            file_path = get_file_path_by_id(raw_file_id)
            
            if not file_path.exists():
                return present_error(DomainException("File not found"))
            
            return FileResponse(
                open(file_path, 'rb'),
                as_attachment=True,
                filename=raw_file.file_name
            )
        
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to download file: {str(e)}"))


class DownloadErrorsCSVView(APIView):
    """Download errors CSV view."""
    
    def get(self, request: Request, raw_file_id: int):
        """Download errors CSV."""
        try:
            get_employee_from_request(request)  # Just check auth
            
            interactor = GetRawFileInteractor(raw_file_id)
            raw_file = interactor.execute()
            
            # Get errors from parse_summary
            parse_summary = raw_file.parse_summary or {}
            errors = parse_summary.get('errors', [])
            
            if not errors:
                return success_response(
                    data={'message': 'No errors found'},
                    message='No errors to download'
                )
            
            csv_content = generate_errors_csv(errors)
            
            response = HttpResponse(csv_content, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="errors_{raw_file_id}.csv"'
            return response
        
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to download errors CSV: {str(e)}"))

