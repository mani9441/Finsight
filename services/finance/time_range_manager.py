"""
Time Range Manager module.
Validates and translates human-readable chart ranges to yfinance periods.
"""

from typing import List, Dict
from core.exceptions import InvalidInputError

class TimeRangeManager:
    """
    Manages selection and mapping of historical time ranges.
    """

    RANGE_MAP: Dict[str, str] = {
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y",
        "5 Years": "5y",
        "Maximum Available History": "max"
    }

    DEFAULT_RANGE: str = "1 Year"

    @classmethod
    def get_supported_ranges(cls) -> List[str]:
        """
        Returns a list of human-readable supported ranges.
        """
        return list(cls.RANGE_MAP.keys())

    @classmethod
    def get_yfinance_period(cls, time_range: str) -> str:
        """
        Translates a human-readable selection into yfinance period codes (e.g. '1mo', '1y').
        Raises InvalidInputError if selection is unsupported.
        """
        if time_range not in cls.RANGE_MAP:
            raise InvalidInputError(
                f"Unsupported historical time range: '{time_range}'. "
                f"Supported values are: {', '.join(cls.get_supported_ranges())}"
            )
        return cls.RANGE_MAP[time_range]
