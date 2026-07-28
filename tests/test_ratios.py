import unittest
from unittest.mock import patch, MagicMock
from core.exceptions import DataRetrievalError
from models import FinancialRatios
from services.common.ratio_validator import RatioResponseValidator
from services.finance.ratio_mapper import FinancialRatioMapper
from services.finance.ratio_service import FinancialRatioService
from services.finance.ratio_controller import RatioController

class TestFinancialRatiosModule(unittest.TestCase):

    def setUp(self):
        self.raw_info_sample = {
            "financialCurrency": "USD",
            "trailingPE": 28.5,
            "priceToBook": 4.2,
            "returnOnEquity": 0.25,
            "profitMargins": 0.18,
            "dividendYield": 0.015,
            "trailingEps": 5.8
        }

    def test_ratio_value_cleaning(self):
        # Valid float parsing
        self.assertEqual(RatioResponseValidator.clean_ratio_value(25.5, "pe_ratio"), 25.5)
        self.assertEqual(RatioResponseValidator.clean_ratio_value("12.3", "pb_ratio"), 12.3)
        
        # Null values
        self.assertIsNone(RatioResponseValidator.clean_ratio_value(None, "pe_ratio"))
        
        # Invalid string
        self.assertIsNone(RatioResponseValidator.clean_ratio_value("invalid", "eps"))
        
        # Negative bounds assertions
        # 1. Negative is fine for ROE, profit margin, EPS
        self.assertEqual(RatioResponseValidator.clean_ratio_value(-0.05, "roe", can_be_negative=True), -0.05)
        self.assertEqual(RatioResponseValidator.clean_ratio_value(-1.2, "eps", can_be_negative=True), -1.2)
        # 2. Negative must be filtered (return None) for PE, PB, Dividend Yield
        self.assertIsNone(RatioResponseValidator.clean_ratio_value(-15.0, "pe_ratio", can_be_negative=False))
        self.assertIsNone(RatioResponseValidator.clean_ratio_value(-0.01, "dividend_yield", can_be_negative=False))

    def test_ratio_response_validation(self):
        # Valid payload
        RatioResponseValidator.validate_raw_response(self.raw_info_sample, "AAPL")
        
        # Non-dictionary payload
        with self.assertRaises(DataRetrievalError):
            RatioResponseValidator.validate_raw_response(None, "AAPL")
        with self.assertRaises(DataRetrievalError):
            RatioResponseValidator.validate_raw_response("string", "AAPL")
            
        # Incomplete payload
        with self.assertRaises(DataRetrievalError):
            RatioResponseValidator.validate_raw_response({"regularMarketPrice": None}, "AAPL")

    def test_financial_ratio_mapping(self):
        ratios = FinancialRatioMapper.to_financial_ratios("AAPL", self.raw_info_sample)
        
        self.assertEqual(ratios.ticker, "AAPL")
        self.assertEqual(ratios.currency, "USD")
        self.assertEqual(ratios.pe_ratio, 28.5)
        self.assertEqual(ratios.pb_ratio, 4.2)
        self.assertEqual(ratios.roe, 0.25)
        self.assertEqual(ratios.profit_margin, 0.18)
        self.assertEqual(ratios.dividend_yield, 0.015)
        self.assertEqual(ratios.eps, 5.8)

    def test_financial_ratio_mapping_partial(self):
        # Exclude PE, PB, and Yield by setting them to negative/invalid, others missing
        dirty_info = {
            "financialCurrency": "EUR",
            "trailingPE": -5.0,        # negative (invalid)
            "priceToBook": "invalid",   # invalid string (invalid)
            "returnOnEquity": -0.15,    # negative ROE (allowed)
            "trailingEps": 2.5          # positive EPS (allowed)
        }
        ratios = FinancialRatioMapper.to_financial_ratios("AAPL", dirty_info)
        
        self.assertEqual(ratios.ticker, "AAPL")
        self.assertEqual(ratios.currency, "EUR")
        self.assertIsNone(ratios.pe_ratio)
        self.assertIsNone(ratios.pb_ratio)
        self.assertEqual(ratios.roe, -0.15)
        self.assertIsNone(ratios.profit_margin)
        self.assertIsNone(ratios.dividend_yield)
        self.assertEqual(ratios.eps, 2.5)

    @patch("yfinance.Ticker")
    def test_financial_ratio_service_success(self, mock_ticker):
        mock_instance = MagicMock()
        mock_instance.info = self.raw_info_sample
        mock_ticker.return_value = mock_instance
        
        service = FinancialRatioService()
        ratios = service.get_financial_ratios("AAPL")
        
        self.assertIsInstance(ratios, FinancialRatios)
        self.assertEqual(ratios.pe_ratio, 28.5)
        mock_ticker.assert_called_once_with("AAPL")

    @patch("yfinance.Ticker")
    def test_financial_ratio_service_failure(self, mock_ticker):
        mock_ticker.side_effect = Exception("API connection timeout error")
        
        service = FinancialRatioService()
        with self.assertRaises(DataRetrievalError):
            service.get_financial_ratios("AAPL")

    @patch("services.finance.ratio_service.FinancialRatioService")
    def test_ratio_controller(self, mock_service_class):
        mock_service = MagicMock()
        expected_ratios = FinancialRatioMapper.to_financial_ratios("AAPL", self.raw_info_sample)
        mock_service.get_financial_ratios.return_value = expected_ratios
        
        controller = RatioController(mock_service)
        ratios = controller.get_ratios("AAPL")
        
        self.assertEqual(ratios, expected_ratios)
        mock_service.get_financial_ratios.assert_called_once_with("AAPL")
