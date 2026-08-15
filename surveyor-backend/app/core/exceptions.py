"""Custom exceptions for the application."""

from fastapi import HTTPException, status

class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(AppException):
    """Authentication failed."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)

class AuthorizationError(AppException):
    """User not authorized for this action."""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)

class NotFoundError(AppException):
    """Resource not found."""
    def __init__(self, resource: str = "Resource"):
        message = f"{resource} not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class ConflictError(AppException):
    """Resource conflict (e.g., duplicate)."""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status.HTTP_409_CONFLICT)

class ValidationError(AppException):
    """Validation error."""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)

class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials provided."""
    def __init__(self):
        super().__init__("Invalid email or password")

class UserNotFoundError(NotFoundError):
    """User not found."""
    def __init__(self):
        super().__init__("User")

class OrganizationNotFoundError(NotFoundError):
    """Organization not found."""
    def __init__(self):
        super().__init__("Organization")

class ProjectNotFoundError(NotFoundError):
    """Project not found."""
    def __init__(self):
        super().__init__("Project")

class ClientNotFoundError(NotFoundError):
    """Client not found."""
    def __init__(self):
        super().__init__("Client")

class QuoteNotFoundError(NotFoundError):
    """Quote not found."""
    def __init__(self):
        super().__init__("Quote")

class EmailAlreadyExistsError(ConflictError):
    """Email already registered."""
    def __init__(self):
        super().__init__("Email already registered")

class InvalidTokenError(AuthenticationError):
    """Invalid or expired token."""
    def __init__(self):
        super().__init__("Invalid or expired token")

class TokenExpiredError(AuthenticationError):
    """Token has expired."""
    def __init__(self):
        super().__init__("Token has expired")

class InsufficientPermissionsError(AuthorizationError):
    """User lacks required permissions."""
    def __init__(self):
        super().__init__("Insufficient permissions")

def http_exception(exc: AppException) -> HTTPException:
    """Convert AppException to HTTPException."""
    return HTTPException(
        status_code=exc.status_code,
        detail=exc.message,
    )
