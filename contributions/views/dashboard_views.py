"""Dashboard views."""
from rest_framework.views import APIView
from rest_framework.request import Request
from contributions.interactors.metrics_interactors import (
    GetOrgMetricsInteractor, GetDepartmentMetricsInteractor,
    GetPodMetricsInteractor, GetEmployeeMetricsInteractor
)
from contributions.presenters.metrics_presenter import (
    present_org_metrics, present_department_metrics,
    present_pod_metrics, present_employee_metrics
)
from contributions.presenters.error_presenter import present_error
from contributions.common.response import success_response
from contributions.utils.auth_middleware import get_employee_from_request
from contributions.exceptions import DomainException


class OrgDashboardView(APIView):
    """Organization dashboard view."""
    
    def get(self, request: Request):
        """Get organization metrics."""
        try:
            employee = get_employee_from_request(request)
            month = request.query_params.get('month')
            
            if not month:
                return success_response(
                    data={'error': 'month parameter is required'},
                    message='Missing required parameter',
                    status_code=400
                )
            
            interactor = GetOrgMetricsInteractor(month, employee.id)
            metrics = interactor.execute()
            
            response_data = present_org_metrics(metrics)
            return success_response(data=response_data)
        
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to get org metrics: {str(e)}"))


class DepartmentDashboardView(APIView):
    """Department dashboard view."""
    
    def get(self, request: Request, dept_id: int):
        """Get department metrics."""
        try:
            employee = get_employee_from_request(request)
            month = request.query_params.get('month')
            
            if not month:
                return success_response(
                    data={'error': 'month parameter is required'},
                    message='Missing required parameter',
                    status_code=400
                )
            
            interactor = GetDepartmentMetricsInteractor(dept_id, month, employee.id)
            metrics = interactor.execute()
            
            response_data = present_department_metrics(metrics)
            return success_response(data=response_data)
        
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to get department metrics: {str(e)}"))


class PodContributionsView(APIView):
    """Pod contributions view."""
    
    def get(self, request: Request, pod_id: int):
        """Get pod metrics."""
        try:
            employee = get_employee_from_request(request)
            month = request.query_params.get('month')
            
            if not month:
                return success_response(
                    data={'error': 'month parameter is required'},
                    message='Missing required parameter',
                    status_code=400
                )
            
            interactor = GetPodMetricsInteractor(pod_id, month, employee.id)
            metrics = interactor.execute()
            
            response_data = present_pod_metrics(metrics)
            return success_response(data=response_data)
        
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to get pod metrics: {str(e)}"))


class EmployeeContributionsView(APIView):
    """Employee contributions view."""
    
    def get(self, request: Request, employee_id: int):
        """Get employee metrics."""
        try:
            employee = get_employee_from_request(request)
            month = request.query_params.get('month')
            
            if not month:
                return success_response(
                    data={'error': 'month parameter is required'},
                    message='Missing required parameter',
                    status_code=400
                )
            
            interactor = GetEmployeeMetricsInteractor(employee_id, month, employee.id)
            metrics = interactor.execute()
            
            response_data = present_employee_metrics(metrics)
            return success_response(data=response_data)
        
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to get employee metrics: {str(e)}"))

