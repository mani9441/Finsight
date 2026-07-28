import unittest
from unittest.mock import patch, MagicMock
from core.exceptions import InvalidInputError, DataRetrievalError
from models import CompanyOverview
from services.common.response_validator import ResponseValidator
from services.finance.overview_mapper import CompanyOverviewMapper
from services.finance.overview_service import FinancialOverviewService
from services.finance.overview_controller import OverviewController

class TestFinancialOverviewModule(unittest.TestCase):
    
    def setUp(self):
        self.raw_info_sample = {
            "longName": "Apple Inc.",
            "symbol": "AAPL",
            "exchange": "NMS",
            "currency": "USD",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "country": "United States",
            "website": "https://www.apple.com",
            "longBusinessSummary": "Apple Inc. designs, manufactures, and markets smartphones...",
            "marketCap": 3000000000000.0
        }

    def test_ticker_validation(self):
        # Valid ticker
        ResponseValidator.validate_ticker_input("AAPL")
        ResponseValidator.validate_ticker_input("msft")
        
        # Invalid inputs
        with self.assertRaises(InvalidInputError):
            ResponseValidator.validate_ticker_input("")
        with self.assertRaises(InvalidInputError):
            ResponseValidator.validate_ticker_input("LONGTICKERSYMBOL")
        with self.assertRaises(InvalidInputError):
            ResponseValidator.validate_ticker_input("AAP$L")

    def test_overview_response_validation(self):
        # Valid payload
        ResponseValidator.validate_overview_response(self.raw_info_sample, "AAPL")
        
        # Empty or non-dict inputs
        with self.assertRaises(DataRetrievalError):
            ResponseValidator.validate_overview_response(None, "AAPL")
        with self.assertRaises(DataRetrievalError):
            ResponseValidator.validate_overview_response([], "AAPL")
            
        # Missing keys or small length
        incomplete_payload = {"regularMarketPrice": None}
        with self.assertRaises(DataRetrievalError):
            ResponseValidator.validate_overview_response(incomplete_payload, "AAPL")
            
        # Lacking ticker symbol
        no_symbol_payload = {
            "longName": "Apple Inc.",
            "exchange": "NMS",
            "currency": "USD",
            "sector": "Tech",
            "industry": "Electronics",
            "country": "US"
        }
        with self.assertRaises(DataRetrievalError):
            ResponseValidator.validate_overview_response(no_symbol_payload, "AAPL")

    def test_company_overview_mapping(self):
        overview = CompanyOverviewMapper.to_company_overview("AAPL", self.raw_info_sample)
        
        self.assertEqual(overview.name, "Apple Inc.")
        self.assertEqual(overview.ticker, "AAPL")
        self.assertEqual(overview.exchange, "NMS")
        self.assertEqual(overview.currency, "USD")
        self.assertEqual(overview.sector, "Technology")
        self.assertEqual(overview.industry, "Consumer Electronics")
        self.assertEqual(overview.country, "United States")
        self.assertEqual(overview.website, "https://www.apple.com")
        self.assertEqual(overview.business_summary, "Apple Inc. designs, manufactures, and markets smartphones...")
        self.assertEqual(overview.market_capitalization, 3000000000000.0)

    def test_company_overview_mapping_partial(self):
        # Test default/fallback mechanisms for missing optional fields
        partial_info = {
            "symbol": "XYZ",
            "longName": "XYZ Corp",
            "sector": "Energy",
            # industry, website, summary, marketCap missing
        }
        overview = CompanyOverviewMapper.to_company_overview("XYZ", partial_info)
        
        self.assertEqual(overview.name, "XYZ Corp")
        self.assertEqual(overview.ticker, "XYZ")
        self.assertEqual(overview.exchange, "Not Available")
        self.assertEqual(overview.currency, "Not Available")
        self.assertEqual(overview.sector, "Energy")
        self.assertEqual(overview.industry, "Not Available")
        self.assertEqual(overview.country, "Not Available")
        self.assertEqual(overview.website, "")
        self.assertEqual(overview.business_summary, "Business description unavailable.")
        self.assertIsNone(overview.market_capitalization)

    @patch("yfinance.Ticker")
    def test_financial_overview_service_success(self, mock_ticker):
        # Mock yfinance return value
        mock_instance = MagicMock()
        mock_instance.info = self.raw_info_sample
        mock_ticker.return_value = mock_instance
        
        service = FinancialOverviewService()
        overview = service.get_company_overview("AAPL")
        
        self.assertIsInstance(overview, CompanyOverview)
        self.assertEqual(overview.name, "Apple Inc.")
        self.assertEqual(overview.ticker, "AAPL")
        mock_ticker.assert_called_once_with("AAPL")

    @patch("yfinance.Ticker")
    def test_financial_overview_service_failure(self, mock_ticker):
        # Mock yfinance throwing an exception
        mock_ticker.side_effect = Exception("API connection timed out")
        
        service = FinancialOverviewService()
        with self.assertRaises(DataRetrievalError):
            service.get_company_overview("AAPL")

    @patch("services.finance.overview_service.FinancialOverviewService")
    def test_overview_controller(self, mock_service_class):
        mock_service = MagicMock()
        expected_overview = CompanyOverviewMapper.to_company_overview("AAPL", self.raw_info_sample)
        mock_service.get_company_overview.return_value = expected_overview
        
        controller = OverviewController(mock_service)
        overview = controller.get_overview("AAPL")
        
        self.assertEqual(overview, expected_overview)
        mock_service.get_company_overview.assert_called_once_with("AAPL")
