"""
Chart Data Processor module.
Converts domain models into format configurations suitable for plotting.
"""

import pandas as pd
from typing import List
from models import HistoricalPrice

class ChartDataProcessor:
    """
    Transforms historical price datasets into structure formats for visual rendering.
    """

    @staticmethod
    def to_dataframe(prices: List[HistoricalPrice]) -> pd.DataFrame:
        """
        Converts a list of HistoricalPrice objects to a pandas DataFrame.
        """
        if not prices:
            return pd.DataFrame()

        data = {
            "Date": [p.date for p in prices],
            "Open": [p.open_val for p in prices],
            "High": [p.high_val for p in prices],
            "Low": [p.low_val for p in prices],
            "Close": [p.close_val for p in prices],
            "Volume": [p.volume for p in prices]
        }
        
        df = pd.DataFrame(data)
        df.set_index("Date", inplace=False)
        return df
