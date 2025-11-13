"""Domain exceptions for the contributions app."""


class DomainException(Exception):
    """Base exception for all domain exceptions."""
    pass


class InvalidFileFormatException(DomainException):
    """Raised when file format is invalid."""
    pass


class ValidationException(DomainException):
    """Raised when validation fails."""
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors or {}


class PermissionDeniedException(DomainException):
    """Raised when permission is denied."""
    pass


class EntityNotFoundException(DomainException):
    """Raised when an entity is not found."""
    pass


class DuplicateUploadException(DomainException):
    """Raised when attempting to upload a duplicate file."""
    pass

