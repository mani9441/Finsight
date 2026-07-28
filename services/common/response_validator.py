"""
Validation utilities for API payloads and configuration parameters.
Ensures external data is formatted correctly before processing.
"""

from typing import Dict, List, Any, Type
from core.exceptions import DataRetrievalError, InvalidInputError

class ResponseValidator:
    """
    Utility class to assert and type-check external service response structures.
    """

    @staticmethod
    def validate_keys(data: Dict[str, Any], required_keys: List[str], context_name: str = "Payload"):
        """
        Validates that all required keys exist in the data dictionary.
        Raises DataRetrievalError if key is missing.
        """
        missing_keys = [k for k in required_keys if k not in data]
        if missing_keys:
            raise DataRetrievalError(
                f"Validation failed for {context_name}. Missing required keys: {', '.join(missing_keys)}"
            )

    @staticmethod
    def validate_type(
        value: Any, 
        expected_type: Type, 
        field_name: str, 
        allow_none: bool = True
    ):
        """
        Validates the type of a specific field.
        Raises DataRetrievalError if types do not match.
        """
        if value is None:
            if not allow_none:
                raise DataRetrievalError(f"Field '{field_name}' cannot be Null/None.")
            return

        if not isinstance(value, expected_type):
            raise DataRetrievalError(
                f"Field '{field_name}' must be of type {expected_type.__name__}, got {type(value).__name__}."
            )

    @staticmethod
    def assert_not_empty(data: Any, context_name: str = "Payload"):
        """
        Checks that the data object is not empty or None.
        """
        if not data:
            raise DataRetrievalError(f"Validation failed: {context_name} cannot be empty or None.")

    @staticmethod
    def validate_ticker_input(ticker: str):
        """
        Validates that the provided ticker matches basic syntax rules.
        """
        if not ticker or not isinstance(ticker, str):
            raise InvalidInputError("Ticker must be a non-empty string.")
        
        clean_ticker = ticker.strip()
        if not clean_ticker.isalnum() or len(clean_ticker) > 10:
            raise InvalidInputError(
                f"Invalid ticker format: '{ticker}'. Ticker must be alphanumeric and between 1-10 characters."
            )

    @staticmethod
    def validate_overview_response(raw_info: Any, ticker: str):
        """
        Validates the raw yfinance info dictionary for company overview.
        Raises DataRetrievalError if response is invalid or lacks necessary keys.
        """
        if not raw_info or not isinstance(raw_info, dict):
            raise DataRetrievalError(f"No company information found for ticker '{ticker}'")
        
        if len(raw_info) <= 5:
            raise DataRetrievalError(f"Company information payload is incomplete or invalid for ticker '{ticker}'")

        if "symbol" not in raw_info and "ticker" not in raw_info:
            raise DataRetrievalError(f"Company overview payload for '{ticker}' lacks identifying ticker symbol.")
