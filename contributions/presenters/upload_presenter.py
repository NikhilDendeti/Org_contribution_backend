"""Presenter for upload responses."""
from contributions.common.response import success_response, error_response
from contributions.exceptions import DomainException, ValidationException


def present_upload_result(result: dict) -> dict:
    """Present upload result as response data."""
    return {
        'raw_file_id': result['raw_file_id'],
        'summary': result['summary'],
        'errors': result.get('errors', []),
        'has_errors': len(result.get('errors', [])) > 0,
    }


def present_upload_error(exception: DomainException) -> dict:
    """Present upload error."""
    if isinstance(exception, ValidationException):
        return {
            'success': False,
            'message': str(exception),
            'error_code': 'VALIDATION_ERROR',
            'errors': exception.errors if hasattr(exception, 'errors') else {},
        }
    return {
        'success': False,
        'message': str(exception),
        'error_code': 'UPLOAD_ERROR',
    }

