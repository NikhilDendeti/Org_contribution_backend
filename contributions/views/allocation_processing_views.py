"""Views for processing Pod Lead allocations."""
from rest_framework.views import APIView
from rest_framework.request import Request
from contributions.interactors.allocation_processing_interactor import ProcessPodAllocationsInteractor
from contributions.presenters.allocation_presenter import present_processing_result
from contributions.presenters.error_presenter import present_error
from contributions.common.response import success_response
from contributions.utils.auth_middleware import get_employee_from_request
from contributions.exceptions import DomainException, PermissionDeniedException


class ProcessPodAllocationsView(APIView):
    """View for processing Pod Lead allocations."""
    
    def post(self, request: Request, pod_id: int):
        """Process all SUBMITTED allocations for a pod."""
        try:
            # Get employee from token
            employee = get_employee_from_request(request)
            
            # Check admin/CEO permission
            if not (employee.role == 'ADMIN' or employee.role == 'CEO'):
                raise PermissionDeniedException("Only ADMIN or CEO can process allocations")
            
            # Get month parameter
            month = request.query_params.get('month')
            if not month:
                return success_response(
                    data={'error': 'month parameter is required'},
                    message='Missing required parameter',
                    status_code=400
                )
            
            # Get output format (default: records)
            output_format = request.query_params.get('output', 'records')
            if output_format not in ['records', 'csv']:
                return success_response(
                    data={'error': "output parameter must be 'records' or 'csv'"},
                    message='Invalid parameter',
                    status_code=400
                )
            
            # Execute interactor
            interactor = ProcessPodAllocationsInteractor(
                pod_id=pod_id,
                month=month,
                output_format=output_format
            )
            result = interactor.execute()
            
            # Present result
            response_data = present_processing_result(result)
            return success_response(data=response_data, message='Allocations processed successfully')
        
        except PermissionDeniedException as e:
            return present_error(e)
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to process allocations: {str(e)}"))

