"""JWT service for token generation and validation."""
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from contributions.storages import employee_storage
from contributions.exceptions import EntityNotFoundException


def generate_tokens(employee_id: int) -> dict:
    """Generate access and refresh tokens for an employee."""
    try:
        employee = employee_storage.get_employee_by_id(employee_id)
        refresh = RefreshToken()
        # Add custom claims
        refresh['employee_id'] = employee.id
        refresh['employee_code'] = employee.employee_code
        refresh['role'] = employee.role
        refresh['department_id'] = employee.department_id
        refresh['pod_id'] = employee.pod_id
        
        access_token = refresh.access_token
        access_token['employee_id'] = employee.id
        access_token['employee_code'] = employee.employee_code
        access_token['role'] = employee.role
        access_token['department_id'] = employee.department_id
        access_token['pod_id'] = employee.pod_id
        
        return {
            'refresh': str(refresh),
            'access': str(access_token),
        }
    except EntityNotFoundException:
        raise EntityNotFoundException(f"Employee with id {employee_id} not found")


def validate_token(token: str) -> dict:
    """Validate and decode a JWT token."""
    try:
        from rest_framework_simplejwt.tokens import UntypedToken
        from rest_framework_simplejwt.exceptions import InvalidToken
        
        UntypedToken(token)
        return {'valid': True}
    except (InvalidToken, TokenError):
        return {'valid': False}


def get_employee_from_token(token: str) -> int:
    """Extract employee ID from token."""
    try:
        from rest_framework_simplejwt.tokens import UntypedToken
        decoded_token = UntypedToken(token)
        return decoded_token.get('employee_id')
    except (InvalidToken, TokenError):
        raise InvalidToken("Invalid token")

