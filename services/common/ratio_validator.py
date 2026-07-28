"""
Validation utilities for financial ratio payloads and numeric variables.
"""

from typing import Any, Optional
from core import get_logger
from core.exceptions import DataRetrievalError

logger = get_logger("ratio_validator")

class RatioResponseValidator:
    """
    Validates yfinance API payload info dictionaries and individual financial ratio bounds.
    """

    @staticmethod
    def validate_raw_response(raw_info: Any, ticker: str):
        """
        Validates that the raw response dictionary is not empty and has minimum metadata keys.
        """
        if not raw_info or not isinstance(raw_info, dict):
            raise DataRetrievalError(f"No financial ratio information found for ticker '{ticker}'")
            
        if len(raw_info) <= 5:
            raise DataRetrievalError(f"Financial ratio payload is incomplete or invalid for ticker '{ticker}'")

    @staticmethod
    def clean_ratio_value(value: Any, field_name: str, can_be_negative: bool = True) -> Optional[float]:
        """
        Validates the type and value of an individual ratio.
        Converts to float, checks negative constraints, and returns None if invalid.
        """
        if value is None:
            return None

        try:
            val_float = float(value)
            
            # Check negative constraints where inappropriate (e.g. PE, PB, Dividend Yield)
            if not can_be_negative and val_float < 0:
                logger.warning(
                    f"Ratio validation warning: field '{field_name}' got negative value '{val_float}' "
                    "which is inappropriate. Excluded."
                )
                return None
                
            return val_float
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Ratio validation warning: field '{field_name}' value '{value}' could not be parsed as float: {e}")
            return None
