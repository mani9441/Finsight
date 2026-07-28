"""
Financial Overview Service implementation using yfinance.
"""

import time
import yfinance as yf
from models import CompanyOverview
from services.interfaces import IFinancialOverviewService
from services.finance.overview_mapper import CompanyOverviewMapper
from services.common.response_validator import ResponseValidator
from core import get_logger
from core.exceptions import DataRetrievalError

logger = get_logger("overview_service")

class FinancialOverviewService(IFinancialOverviewService):
    """
    Service responsible for retrieving corporate metadata and profile overview.
    Implements IFinancialOverviewService interface.
    """

    def get_company_overview(self, ticker: str) -> CompanyOverview:
        """
        Retrieves company overview details for a specific ticker from Yahoo Finance.
        Validates the output and maps it to a standardized internal dataclass.
        """
        ticker_str = ticker.strip().upper()
        logger.info(f"Overview request started for ticker: '{ticker_str}'")
        
        # Validate ticker syntax
        ResponseValidator.validate_ticker_input(ticker_str)
        
        start_time = time.time()
        try:
            ticker_obj = yf.Ticker(ticker_str)
            raw_info = ticker_obj.info
            
            response_time = (time.time() - start_time) * 1000
            logger.info(f"Provider response received for '{ticker_str}' in {response_time:.2f}ms")
            
            # Validate response payload structure
            ResponseValidator.validate_overview_response(raw_info, ticker_str)
            
            # Identify missing fields in raw_info compared to what we map
            expected_keys = ["longName", "exchange", "currency", "financialCurrency", "sector", "industry", "country", "website", "longBusinessSummary", "marketCap"]
            missing_fields = [key for key in expected_keys if key not in raw_info or raw_info[key] is None]
            if missing_fields:
                logger.warning(f"Missing fields in yfinance response for '{ticker_str}': {', '.join(missing_fields)}")
            
            # Map raw response to model
            overview = CompanyOverviewMapper.to_company_overview(ticker_str, raw_info)
            logger.info(f"Successful overview retrieval for ticker '{ticker_str}'")
            return overview
            
        except DataRetrievalError as e:
            logger.error(f"Validation failure or empty response for '{ticker_str}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during overview retrieval for '{ticker_str}': {e}")
            raise DataRetrievalError(
                f"Failed to retrieve company overview from Yahoo Finance for symbol '{ticker_str}' due to: {str(e)}"
            ) from e
