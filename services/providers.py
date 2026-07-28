from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

class IFinancialDataProvider(ABC):
    """
    Interface for third-party financial API adapters (e.g. Yahoo Finance).
    """
    @abstractmethod
    def fetch_company_info(self, ticker: str) -> Dict[str, Any]:
        """
        Retrieves raw metadata dictionary for a ticker.
        """
        pass

    @abstractmethod
    def fetch_historical_data(
        self, ticker: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Retrieves a list of daily pricing dictionaries for a ticker.
        """
        pass

    @abstractmethod
    def fetch_financial_statements(self, ticker: str) -> Dict[str, Any]:
        """
        Retrieves balance sheets, cash flows, and income statement raw figures.
        """
        pass


class INewsDataProvider(ABC):
    """
    Interface for external news search providers (e.g. news APIs or web crawlers).
    """
    @abstractmethod
    def fetch_news(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves raw articles metadata matching the query string.
        """
        pass


class ILLMProvider(ABC):
    """
    Interface for third-party LLM providers (e.g. OpenAI or Google Gemini).
    """
    @abstractmethod
    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Queries an LLM text generation model with a prompt.
        """
        pass

    @abstractmethod
    def generate_json(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Queries an LLM model demanding response in a validated JSON schema format.
        """
        pass
