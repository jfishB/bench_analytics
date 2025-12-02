"""
- This file defines domain-level exceptions for the accounts module.
- Imported by:
  - backend/accounts/services.py
"""


class DomainError(Exception):
    """Base class for predictable business/domain errors."""

    status_code = 400  # Default HTTP code


class MissingFieldsError(DomainError):
    """Raised when required fields are missing."""

    pass


class UserAlreadyExistsError(DomainError):
    """Raised when a username is already taken."""

    pass


class UsernameConflictError(DomainError):
    """Raised when a username conflict occurs due to a race condition."""

    pass


class EmailAlreadyExistsError(DomainError):
    """Raised when an email is already taken."""

    pass


class InvalidCredentialsError(DomainError):
    """Raised when login credentials are invalid."""

    status_code = 401
