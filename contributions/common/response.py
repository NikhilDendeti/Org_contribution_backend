"""Common response helpers for consistent API responses."""
from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message=None, status_code=status.HTTP_200_OK) -> Response:
    """Standard success response format."""
    response_data = {
        'success': True,
        'data': data,
    }
    if message:
        response_data['message'] = message
    return Response(response_data, status=status_code)


def error_response(message: str, error_code: str = None, errors: dict = None, status_code=status.HTTP_400_BAD_REQUEST) -> Response:
    """Standard error response format."""
    response_data = {
        'success': False,
        'message': message,
    }
    if error_code:
        response_data['error_code'] = error_code
    if errors:
        response_data['errors'] = errors
    return Response(response_data, status=status_code)


def not_found_response(entity_name: str = "Entity") -> Response:
    """404 Not Found response."""
    return error_response(
        message=f"{entity_name} not found",
        error_code="NOT_FOUND",
        status_code=status.HTTP_404_NOT_FOUND
    )


def permission_denied_response(message: str = "Permission denied") -> Response:
    """403 Forbidden response."""
    return error_response(
        message=message,
        error_code="PERMISSION_DENIED",
        status_code=status.HTTP_403_FORBIDDEN
    )


def validation_error_response(errors: dict) -> Response:
    """400 Bad Request response for validation errors."""
    return error_response(
        message="Validation failed",
        error_code="VALIDATION_ERROR",
        errors=errors,
        status_code=status.HTTP_400_BAD_REQUEST
    )

