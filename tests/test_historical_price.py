import unittest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from core.exceptions import InvalidInputError, DataRetrievalError
from models import HistoricalPrice
from services.finance.time_range_manager import TimeRangeManager
from services.common.historical_validator import HistoricalDataValidator
from services.finance.historical_mapper import HistoricalDataMapper
from services.finance.chart_data_processor import ChartDataProcessor
from services.finance.historical_price_service import HistoricalPriceService
from services.finance.historical_price_controller import HistoricalPriceController

class TestHistoricalStockPricesModule(unittest.TestCase):

    def setUp(self):
        self.d1 = datetime(2026, 7, 1)
        self.d2 = datetime(2026, 7, 2)
        self.d3 = datetime(2026, 7, 3)

        self.sample_prices_list = [
            HistoricalPrice(date=self.d2, open_val=151.0, high_val=153.0, low_val=150.0, close_val=152.0, volume=1000),
            # Duplicate date (should be filtered)
            HistoricalPrice(date=self.d2, open_val=151.5, high_val=153.5, low_val=150.5, close_val=152.5, volume=1200),
            # Invalid negative price (should be filtered)
            HistoricalPrice(date=self.d3, open_val=153.0, high_val=155.0, low_val=152.0, close_val=-10.0, volume=1100),
            # Out of order date (should be sorted)
            HistoricalPrice(date=self.d1, open_val=150.0, high_val=152.0, low_val=149.0, close_val=151.0, volume=900),
        ]

        self.mock_df = pd.DataFrame(
            data={
                "Open": [150.0, 151.0],
                "High": [152.0, 153.0],
                "Low": [149.0, 150.0],
                "Close": [151.0, 152.0],
                "Volume": [900, 1000]
            },
            index=[self.d1, self.d2]
        )

    def test_time_range_manager(self):
        # Valid mappings
        self.assertEqual(TimeRangeManager.get_yfinance_period("1 Month"), "1mo")
        self.assertEqual(TimeRangeManager.get_yfinance_period("1 Year"), "1y")
        self.assertEqual(TimeRangeManager.get_yfinance_period("Maximum Available History"), "max")

        # Unsupported range
        with self.assertRaises(InvalidInputError):
            TimeRangeManager.get_yfinance_period("10 Years")

    def test_historical_data_validator(self):
        validated = HistoricalDataValidator.validate_historical_prices(self.sample_prices_list, "AAPL")
        
        # Valid records remaining: d1 (Apple Corp $151), d2 (Apple Corp $152).
        # Duplicate d2, negative price d3 filtered.
        self.assertEqual(len(validated), 2)
        
        # Chronological ordering check (d1 must precede d2)
        self.assertEqual(validated[0].date, self.d1)
        self.assertEqual(validated[1].date, self.d2)

        # Negative price verification
        self.assertEqual(validated[0].close_val, 151.0)
        self.assertEqual(validated[1].close_val, 152.0)

        # Empty list check
        with self.assertRaises(DataRetrievalError):
            HistoricalDataValidator.validate_historical_prices([], "AAPL")

    def test_historical_data_mapper(self):
        prices = HistoricalDataMapper.to_historical_prices(self.mock_df)
        
        self.assertEqual(len(prices), 2)
        self.assertEqual(prices[0].date, self.d1)
        self.assertEqual(prices[0].open_val, 150.0)
        self.assertEqual(prices[0].close_val, 151.0)
        self.assertEqual(prices[0].volume, 900)

        # Empty df
        empty_prices = HistoricalDataMapper.to_historical_prices(pd.DataFrame())
        self.assertEqual(len(empty_prices), 0)

    def test_chart_data_processor(self):
        validated_prices = [
            HistoricalPrice(date=self.d1, open_val=150.0, high_val=152.0, low_val=149.0, close_val=151.0, volume=900),
            HistoricalPrice(date=self.d2, open_val=151.0, high_val=153.0, low_val=150.0, close_val=152.0, volume=1000)
        ]
        df = ChartDataProcessor.to_dataframe(validated_prices)
        
        self.assertEqual(len(df), 2)
        self.assertListEqual(list(df["Close"]), [151.0, 152.0])
        self.assertListEqual(list(df["Volume"]), [900, 1000])

    @patch("yfinance.Ticker")
    def test_historical_price_service_success(self, mock_ticker):
        mock_instance = MagicMock()
        mock_instance.history.return_value = self.mock_df
        mock_ticker.return_value = mock_instance

        service = HistoricalPriceService()
        prices = service.get_historical_prices_by_range("AAPL", "1 Year")
        
        self.assertEqual(len(prices), 2)
        self.assertEqual(prices[0].date, self.d1)
        mock_instance.history.assert_called_once_with(period="1y")

    @patch("yfinance.Ticker")
    def test_historical_price_service_api_failure(self, mock_ticker):
        mock_ticker.side_effect = Exception("Conda connection timeout error")
        
        service = HistoricalPriceService()
        with self.assertRaises(DataRetrievalError):
            service.get_historical_prices_by_range("AAPL", "6 Months")

    @patch("services.finance.historical_price_service.HistoricalPriceService")
    def test_historical_price_controller(self, mock_service_class):
        mock_service = MagicMock()
        expected_prices = [
            HistoricalPrice(date=self.d1, open_val=150.0, high_val=152.0, low_val=149.0, close_val=151.0, volume=900)
        ]
        mock_service.get_historical_prices_by_range.return_value = expected_prices
        
        controller = HistoricalPriceController(mock_service)
        prices = controller.get_historical_prices("AAPL", "1 Month")
        
        self.assertEqual(prices, expected_prices)
        mock_service.get_historical_prices_by_range.assert_called_once_with("AAPL", "1 Month")
