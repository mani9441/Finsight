"""
Mapper utility for translating raw pandas DataFrames from yfinance into standardized HistoricalPrice models.
"""

import pandas as pd
from typing import List
from models import HistoricalPrice
from core import get_logger

logger = get_logger("historical_mapper")

class HistoricalDataMapper:
    """
    Translates raw structures from Yahoo Finance into standardized HistoricalPrice dataclasses.
    """

    @staticmethod
    def to_historical_prices(history_df: pd.DataFrame) -> List[HistoricalPrice]:
        """
        Maps a pandas DataFrame returned by yfinance history() to a list of HistoricalPrice models.
        """
        prices = []
        if history_df is None or history_df.empty:
            return prices

        for index, row in history_df.iterrows():
            # Extract date value (handling pandas Timestamp convert to python datetime)
            date_val = index.to_pydatetime() if hasattr(index, "to_pydatetime") else index
            
            # yfinance returns columns with first letter capitalized (Open, High, Low, Close, Volume)
            # We map them to our internal model fields
            try:
                open_val = row.get("Open")
                high_val = row.get("High")
                low_val = row.get("Low")
                close_val = row.get("Close")
                volume_val = row.get("Volume")

                # Convert to clean numeric formats
                parsed_open = float(open_val) if open_val is not None else 0.0
                parsed_high = float(high_val) if high_val is not None else 0.0
                parsed_low = float(low_val) if low_val is not None else 0.0
                parsed_close = float(close_val) if close_val is not None else 0.0
                parsed_volume = int(volume_val) if volume_val is not None else 0

                prices.append(
                    HistoricalPrice(
                        date=date_val,
                        open_val=parsed_open,
                        high_val=parsed_high,
                        low_val=parsed_low,
                        close_val=parsed_close,
                        volume=parsed_volume
                    )
                )
            except Exception as e:
                logger.warning(f"Error mapping historical record at index '{index}': {e}")
                
        return prices
