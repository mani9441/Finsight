"""
Validation utilities for historical stock price records.
Ensures data integrity before rendering charts.
"""

import math
from typing import List
from models import HistoricalPrice
from core import get_logger
from core.exceptions import DataRetrievalError

logger = get_logger("historical_validator")

class HistoricalDataValidator:
    """
    Validates a list of HistoricalPrice records for missing fields, duplicates, ordering, and invalid values.
    """

    @staticmethod
    def validate_historical_prices(prices: List[HistoricalPrice], ticker: str) -> List[HistoricalPrice]:
        """
        Validates historical pricing records.
        Removes invalid, null, negative, or duplicate dates.
        Ensures ascending chronological order.
        Raises DataRetrievalError if final dataset is empty.
        """
        if not prices:
            raise DataRetrievalError(f"No historical price data available for the selected period for ticker '{ticker}'.")

        validated_prices = []
        seen_dates = set()

        for idx, price in enumerate(prices):
            # 1. Validate Date exists
            if price.date is None:
                logger.warning(f"Excluding record at index {idx} for '{ticker}': missing date.")
                continue

            # 2. Check for duplicate dates (keep the first one)
            date_key = price.date.date() if hasattr(price.date, "date") else price.date
            if date_key in seen_dates:
                logger.warning(f"Excluding duplicate record for '{ticker}' on date {date_key}.")
                continue

            # 3. Validate price values are not negative, NaN, or None
            invalid_value = False
            for field, val in [
                ("open", price.open_val),
                ("high", price.high_val),
                ("low", price.low_val),
                ("close", price.close_val)
            ]:
                if val is None or math.isnan(val) or val < 0:
                    logger.warning(f"Excluding record for '{ticker}' on date {date_key}: invalid {field} value '{val}'.")
                    invalid_value = True
                    break
            
            if invalid_value:
                continue

            # If all checks pass, record is valid
            seen_dates.add(date_key)
            validated_prices.append(price)

        # 4. Check if final dataset is empty
        if not validated_prices:
            raise DataRetrievalError(f"No valid historical price records remain after validation for ticker '{ticker}'.")

        # 5. Ensure ascending chronological ordering
        validated_prices.sort(key=lambda p: p.date)

        logger.info(
            f"Successfully validated {len(validated_prices)} records for '{ticker}' "
            f"(excluded {len(prices) - len(validated_prices)} invalid/duplicate records)."
        )
        return validated_prices
