"""Custom authentication views."""
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from contributions.services import jwt_service
from contributions.storages import employee_storage
from contributions.presenters.error_presenter import present_error
from contributions.common.response import success_response
from contributions.exceptions import DomainException, EntityNotFoundException


class EmployeeTokenObtainView(APIView):
    """Custom token obtain view for Employee authentication."""
    permission_classes = []  # Public endpoint
    
    def post(self, request: Request):
        """Generate tokens for employee using employee_code."""
        try:
            employee_code = request.data.get('employee_code')
            
            if not employee_code:
                return success_response(
                    data={'error': 'employee_code is required'},
                    message='Missing required field',
                    status_code=400
                )
            
            # Get employee by code
            employee = employee_storage.get_employee_by_code(employee_code)
            
            # Generate tokens
            tokens = jwt_service.generate_tokens(employee.id)
            
            return success_response(data=tokens, message='Tokens generated successfully')
        
        except EntityNotFoundException as e:
            return present_error(e)
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Authentication failed: {str(e)}"))


class EmployeeTokenRefreshView(APIView):
    """Custom token refresh view for Employee authentication."""
    permission_classes = []  # Public endpoint
    
    def post(self, request: Request):
        """Refresh access token using refresh token."""
        try:
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return success_response(
                    data={'error': 'refresh token is required'},
                    message='Missing required field',
                    status_code=400
                )
            
            try:
                # Validate refresh token
                refresh = RefreshToken(refresh_token)
                
                # Get employee_id from token
                employee_id = refresh.get('employee_id')
                if not employee_id:
                    raise InvalidToken('Token missing employee_id')
                
                # Verify employee exists
                employee = employee_storage.get_employee_by_id(employee_id)
                
                # Generate new access token
                access_token = jwt_service.generate_tokens(employee.id)['access']
                
                return success_response(
                    data={'access': access_token},
                    message='Token refreshed successfully'
                )
            
            except TokenError as e:
                return success_response(
                    data={'error': str(e)},
                    message='Invalid refresh token',
                    status_code=401
                )
        
        except EntityNotFoundException as e:
            return present_error(e)
        except DomainException as e:
            return present_error(e)
        except Exception as e:
            return present_error(DomainException(f"Token refresh failed: {str(e)}"))

