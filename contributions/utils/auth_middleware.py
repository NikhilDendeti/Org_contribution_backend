"""Authentication middleware for extracting employee from JWT token."""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from contributions.services import jwt_service
from contributions.storages import employee_storage
from contributions.exceptions import EntityNotFoundException


def get_employee_from_request(request):
    """Extract employee from request JWT token."""
    try:
        # Use our custom authentication
        from contributions.utils.custom_auth import EmployeeJWTAuthentication
        jwt_auth = EmployeeJWTAuthentication()
        header = jwt_auth.get_header(request)
        if header is None:
            raise AuthenticationFailed('No authorization header')
        raw_token = jwt_auth.get_raw_token(header)
        validated_token = jwt_auth.get_validated_token(raw_token)
        
        # Get employee_id from token
        employee_id = validated_token.get('employee_id')
        if not employee_id:
            raise AuthenticationFailed('Token missing employee_id')
        
        # Get employee DTO
        return employee_storage.get_employee_by_id(employee_id)
    except Exception as e:
        # Fallback: try manual extraction
        try:
            from rest_framework_simplejwt.tokens import UntypedToken
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header.startswith('Bearer '):
                raise AuthenticationFailed('Invalid authorization header')
            
            token = auth_header.split(' ')[1]
            decoded_token = UntypedToken(token)
            employee_id = decoded_token.get('employee_id')
            if not employee_id:
                raise AuthenticationFailed('Token missing employee_id')
            return employee_storage.get_employee_by_id(employee_id)
        except Exception as ex:
            raise AuthenticationFailed(f"Authentication failed: {str(ex)}")

