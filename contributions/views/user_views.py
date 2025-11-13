"""User profile views."""
from rest_framework.views import APIView
from rest_framework.request import Request
from contributions.utils.auth_middleware import get_employee_from_request
from contributions.presenters.error_presenter import present_error
from contributions.common.response import success_response
from contributions.exceptions import DomainException


class CurrentUserView(APIView):
    """Get current authenticated user's profile."""
    
    def get(self, request: Request):
        """Get current user information."""
        try:
            employee = get_employee_from_request(request)
            
            # Return user profile
            return success_response(data={
                'id': employee.id,
                'employee_code': employee.employee_code,
                'name': employee.name,
                'email': employee.email,
                'role': employee.role,
                'department_id': employee.department_id,
                'department_name': employee.department_name,
                'pod_id': employee.pod_id,
                'pod_name': employee.pod_name,
            })
        
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Failed to get user profile: {str(e)}"))

