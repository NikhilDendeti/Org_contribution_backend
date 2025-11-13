"""Presenter for error responses."""
from contributions.exceptions import (
    DomainException, InvalidFileFormatException, ValidationException,
    PermissionDeniedException, EntityNotFoundException, DuplicateUploadException
)
from contributions.common.response import (
    error_response, not_found_response, permission_denied_response, validation_error_response
)
from rest_framework.response import Response


def present_error(exception: DomainException) -> Response:
    """Present domain exception as HTTP response."""
    if isinstance(exception, EntityNotFoundException):
        return not_found_response(str(exception))
    elif isinstance(exception, PermissionDeniedException):
        return permission_denied_response(str(exception))
    elif isinstance(exception, ValidationException):
        errors = exception.errors if hasattr(exception, 'errors') else {}
        return validation_error_response(errors)
    elif isinstance(exception, InvalidFileFormatException):
        return error_response(str(exception), error_code='INVALID_FILE_FORMAT')
    elif isinstance(exception, DuplicateUploadException):
        return error_response(str(exception), error_code='DUPLICATE_UPLOAD')
    else:
        return error_response(str(exception), error_code='DOMAIN_ERROR')

