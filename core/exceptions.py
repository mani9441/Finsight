"""
Custom exception classes for FinSight.
Provides unified error handling across services, core subsystems, and UI.
"""

class FinSightException(Exception):
    """Base exception class for all FinSight application errors."""
    def __init__(self, message: str = "An unexpected error occurred in FinSight", *args):
        super().__init__(message, *args)
        self.message = message


class ConfigurationError(FinSightException):
    """Exception raised for errors in the application configuration or environment variables."""
    def __init__(self, message: str = "Configuration error occurred", *args):
        super().__init__(message, *args)


class ServiceError(FinSightException):
    """Base class for exceptions raised by external API services or integrations."""
    def __init__(self, message: str = "External service error occurred", *args):
        super().__init__(message, *args)


class InvalidInputError(FinSightException):
    """Exception raised when validation of user or component inputs fails."""
    def __init__(self, message: str = "Invalid input details provided", *args):
        super().__init__(message, *args)


class DataRetrievalError(FinSightException):
    """Exception raised when financial data fetching or scraping fails."""
    def __init__(self, message: str = "Failed to retrieve financial dataset", *args):
        super().__init__(message, *args)
