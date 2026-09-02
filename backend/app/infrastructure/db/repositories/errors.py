class RepositoryError(Exception):
    """Base repository error for persistence layer."""


class NotFoundError(RepositoryError):
    """Raised when an entity is not found."""


class IntegrityViolationError(RepositoryError):
    """Raised when a DB integrity error occurs (unique constraint, FK, etc.)."""
