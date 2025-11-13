"""Custom JWT authentication for Employee model."""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from contributions.storages import employee_storage
from contributions.exceptions import EntityNotFoundException


class EmployeeJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication that uses employee_id instead of user."""
    
    def get_user(self, validated_token):
        """Get employee from validated token."""
        try:
            employee_id = validated_token.get('employee_id')
            if not employee_id:
                raise InvalidToken('Token missing employee_id')
            
            employee = employee_storage.get_employee_by_id(employee_id)
            
            # Create a simple user-like object for compatibility
            class EmployeeUser:
                def __init__(self, employee):
                    self.employee = employee
                    self.id = employee.id
                    self.is_authenticated = True
                    self.is_active = True
            
            return EmployeeUser(employee)
        except EntityNotFoundException:
            raise InvalidToken('Employee not found')
        except Exception as e:
            raise InvalidToken(f'Invalid token: {str(e)}')

