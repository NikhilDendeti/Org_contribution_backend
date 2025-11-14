"""Views for Pod Lead allocation operations."""
from rest_framework.views import APIView
from rest_framework.request import Request
from django.http import FileResponse
from contributions.interactors.pod_lead_allocation_interactor import SubmitPodLeadAllocationInteractor
from contributions.presenters.allocation_presenter import (
    present_allocation_sheet, present_allocation_submission, present_allocation_list
)
from contributions.presenters.error_presenter import present_error
from contributions.common.response import success_response
from contributions.utils.auth_middleware import get_employee_from_request
from contributions.storages import pod_lead_allocation_storage, pod_storage
from contributions.services import sheet_generation_service
from contributions.exceptions import DomainException, PermissionDeniedException
from django.conf import settings
from pathlib import Path


class GetPodAllocationSheetView(APIView):
    """View for getting Pod Lead allocation sheet."""
    
    def get(self, request: Request, pod_id: int):
        """Get allocation sheet for Pod Lead's pod."""
        try:
            # Get employee from token
            employee = get_employee_from_request(request)
            
            # AUTOMATION users can access any pod's sheet
            if employee.role == 'AUTOMATION':
                pass  # Allow access
            # Verify Pod Lead has access to this pod
            elif employee.role != 'POD_LEAD' or employee.pod_id != pod_id:
                raise PermissionDeniedException(
                    f"Pod Lead {employee.employee_code} does not have access to pod {pod_id}"
                )
            
            # Get month parameter
            month = request.query_params.get('month')
            if not month:
                return success_response(
                    data={'error': 'month parameter is required'},
                    message='Missing required parameter',
                    status_code=400
                )
            
            # Get pod details
            pod = pod_storage.get_pod_by_id(pod_id)
            
            # Check if sheet exists
            from datetime import datetime, date
            month_date = datetime.strptime(month, '%Y-%m').date()
            month_date = date(month_date.year, month_date.month, 1)
            
            month_str = month_date.strftime('%Y-%m')
            sheet_filename = f"pod_{pod_id}_allocation_{month_str}.xlsx"
            sheet_path = Path(settings.MEDIA_ROOT) / 'pod_lead_sheets' / sheet_filename
            
            if not sheet_path.exists():
                return success_response(
                    data={'error': 'Sheet not found. Please generate sheets first.'},
                    message='Sheet not found',
                    status_code=404
                )
            
            download_url = sheet_generation_service.get_sheet_download_url(sheet_path)
            
            response_data = present_allocation_sheet(
                str(sheet_path.relative_to(Path(settings.MEDIA_ROOT))),
                download_url,
                pod_id,
                pod.name
            )
            
            return success_response(data=response_data, message='Sheet retrieved successfully')
        
        except PermissionDeniedException as e:
            return present_error(e)
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to get sheet: {str(e)}"))


class DownloadPodAllocationSheetView(APIView):
    """View for downloading Pod Lead allocation sheet file."""
    
    def get(self, request: Request, pod_id: int):
        """Download allocation sheet file."""
        try:
            # Get employee from token
            employee = get_employee_from_request(request)
            
            # AUTOMATION users can download any pod's sheet
            if employee.role == 'AUTOMATION':
                pass  # Allow access
            # Verify Pod Lead has access to this pod
            elif employee.role != 'POD_LEAD' or employee.pod_id != pod_id:
                raise PermissionDeniedException(
                    f"Pod Lead {employee.employee_code} does not have access to pod {pod_id}"
                )
            
            # Get month parameter
            month = request.query_params.get('month')
            if not month:
                return success_response(
                    data={'error': 'month parameter is required'},
                    message='Missing required parameter',
                    status_code=400
                )
            
            # Get pod details
            pod = pod_storage.get_pod_by_id(pod_id)
            
            # Check if sheet exists
            from datetime import datetime, date
            month_date = datetime.strptime(month, '%Y-%m').date()
            month_date = date(month_date.year, month_date.month, 1)
            
            month_str = month_date.strftime('%Y-%m')
            sheet_filename = f"pod_{pod_id}_allocation_{month_str}.xlsx"
            sheet_path = Path(settings.MEDIA_ROOT) / 'pod_lead_sheets' / sheet_filename
            
            if not sheet_path.exists():
                return success_response(
                    data={'error': 'Sheet not found. Please generate sheets first.'},
                    message='Sheet not found',
                    status_code=404
                )
            
            # Return file response
            return FileResponse(
                open(sheet_path, 'rb'),
                as_attachment=True,
                filename=sheet_filename,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        
        except PermissionDeniedException as e:
            return present_error(e)
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to download sheet: {str(e)}"))


class GetPodAllocationsView(APIView):
    """View for getting Pod Lead allocations."""
    
    def get(self, request: Request, pod_id: int):
        """Get all allocations for Pod Lead's pod."""
        try:
            # Get employee from token
            employee = get_employee_from_request(request)
            
            # Verify Pod Lead has access to this pod
            if employee.role != 'POD_LEAD' or employee.pod_id != pod_id:
                raise PermissionDeniedException(
                    f"Pod Lead {employee.employee_code} does not have access to pod {pod_id}"
                )
            
            # Get month parameter
            month = request.query_params.get('month')
            if not month:
                return success_response(
                    data={'error': 'month parameter is required'},
                    message='Missing required parameter',
                    status_code=400
                )
            
            # Parse month
            from datetime import datetime, date
            month_date = datetime.strptime(month, '%Y-%m').date()
            month_date = date(month_date.year, month_date.month, 1)
            
            # Get allocations
            allocations = pod_lead_allocation_storage.get_allocations_by_pod_lead(employee.id, month_date)
            
            response_data = present_allocation_list(allocations)
            
            return success_response(data=response_data, message='Allocations retrieved successfully')
        
        except PermissionDeniedException as e:
            return present_error(e)
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to get allocations: {str(e)}"))


class SubmitPodAllocationView(APIView):
    """View for submitting Pod Lead allocations."""
    
    def post(self, request: Request, pod_id: int):
        """Submit allocations for Pod Lead's pod."""
        try:
            # Get employee from token
            employee = get_employee_from_request(request)
            
            # Get month parameter
            month = request.data.get('month')
            if not month:
                return success_response(
                    data={'error': 'month parameter is required'},
                    message='Missing required parameter',
                    status_code=400
                )
            
            # Get allocations data
            allocations = request.data.get('allocations', [])
            if not allocations:
                return success_response(
                    data={'error': 'allocations array is required'},
                    message='Missing required parameter',
                    status_code=400
                )
            
            # Execute interactor
            interactor = SubmitPodLeadAllocationInteractor(
                pod_id=pod_id,
                month=month,
                allocations=allocations,
                pod_lead_id=employee.id
            )
            result = interactor.execute()
            
            # Present result
            response_data = present_allocation_submission(result)
            return success_response(data=response_data, message='Allocations submitted successfully')
        
        except PermissionDeniedException as e:
            return present_error(e)
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to submit allocations: {str(e)}"))

