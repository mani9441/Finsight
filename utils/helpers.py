"""
General helper utilities for formatting, conversions, and datetime operations.
"""

from datetime import datetime, timedelta
from typing import Union, Optional
import math

def is_invalid_number(val: Union[int, float, None]) -> bool:
    """Helper to check if a value is None or NaN (Not a Number)."""
    if val is None:
        return True
    if isinstance(val, float) and math.isnan(val):
        return True
    return False

def format_currency(val: Union[int, float, None], currency_symbol: str = "$") -> str:
    """
    Formats a numeric value as currency (e.g., $1,234.56).
    """
    if is_invalid_number(val):
        return "N/A"
    return f"{currency_symbol}{val:,.2f}"


def format_large_number(val: Union[int, float, None]) -> str:
    """
    Formats large numbers into human-readable compact strings with suffixes.
    e.g.,
      1,200,000 -> 1.20M
      3,450,000,000 -> 3.45B
      15,000 -> 15.00K
    """
    if is_invalid_number(val):
        return "N/A"

    if val < 0:
        sign = "-"
    else:
        sign = ""
        
    number = abs(val)

    if number >= 1e12:
        return f"{sign}{number / 1e12:.2f}T"
    elif number >= 1e9:
        return f"{sign}{number / 1e9:.2f}B"
    elif number >= 1e6:
        return f"{sign}{number / 1e6:.2f}M"
    elif number >= 1e3:
        return f"{sign}{number / 1e3:.2f}K"
    else:
        return f"{sign}{number:.2f}"


def format_percent(val: Union[int, float, None], is_multiplier: bool = False) -> str:
    """
    Formats a decimal or multiplier value as a percentage.
    If is_multiplier is True, multiplies by 100 first (e.g. 0.057 -> 5.70%).
    """
    if is_invalid_number(val):
        return "N/A"
    
    if is_multiplier:
        scaled_val = val * 100.0
    else:
        scaled_val = val
        
    if scaled_val != 0:
        return f"{scaled_val:+.2f}%"
    else:
        return f"{scaled_val:.2f}%"


def get_date_range_days_ago(days: int) -> tuple[datetime, datetime]:
    """
    Returns a start date and end date tuple representing the range from
    `days` ago to today.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def parse_date_string(date_str: str, format_str: str = "%Y-%m-%d") -> Optional[datetime]:
    """
    Attempts to parse a date string into a datetime object. Returns None if parsing fails.
    """
    try:
        return datetime.strptime(date_str.strip(), format_str)
    except (ValueError, TypeError):
        return None
