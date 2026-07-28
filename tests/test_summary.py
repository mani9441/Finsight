import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
import requests
from models import CompanyOverview, FinancialRatios, SentimentResult, RiskAssessment, AISummary
from services.ai.prompt_builder import PromptBuilder
from services.ai.llm_service import LlmService
from services.ai.summary_controller import SummaryController
from core.exceptions import ServiceError, DataRetrievalError

class TestAISummaryModule(unittest.TestCase):

    def setUp(self):
        self.overview = CompanyOverview(
            ticker="AAPL",
            name="Apple Inc.",
            exchange="NASDAQ",
            currency="USD",
            sector="Technology",
            industry="Consumer Electronics",
            country="US",
            website="https://apple.com",
            business_summary="Designs consumer electronics."
        )
        self.ratios = FinancialRatios(
            ticker="AAPL",
            currency="USD",
            pe_ratio=25.0,
            pb_ratio=5.0,
            roe=0.20,
            profit_margin=0.15,
            dividend_yield=0.015,
            eps=5.0
        )
        self.sentiment = SentimentResult(
            ticker="AAPL",
            average_score=0.15,
            sentiment_label="Positive",
            article_count=10,
            positive_count=5,
            neutral_count=3,
            negative_count=2
        )
        self.risk = RiskAssessment(
            ticker="AAPL",
            risk_score=15.0,
            risk_level="Low Risk",
            risk_explanation="Low overall warning signs."
        )

    def test_prompt_builder_structure(self):
        prompt = PromptBuilder.build_advisory_prompt(
            self.overview, self.ratios, self.sentiment, self.risk
        )
        self.assertIn("Apple Inc.", prompt)
        self.assertIn("AAPL", prompt)
        self.assertIn("Technology", prompt)
        self.assertIn("Consumer Electronics", prompt)
        self.assertIn("25.0", prompt)
        self.assertIn("5.0", prompt)
        self.assertIn("Low Risk", prompt)
        self.assertIn("JSON", prompt)

    @patch("services.ai.llm_service.settings")
    def test_llm_service_mock_mode(self, mock_settings):
        # Configure mock mode (no key)
        mock_settings.GEMINI_API_KEY = ""
        
        service = LlmService()
        summary = service.generate_advisory_summary(
            self.overview, self.ratios, self.sentiment, self.risk
        )
        
        self.assertEqual(summary.ticker, "AAPL")
        self.assertEqual(summary.status, "Mocked")
        self.assertIn("Apple Inc. (AAPL) indicates a profile", summary.executive_summary)

    @patch("services.ai.llm_service.requests.post")
    @patch("services.ai.llm_service.settings")
    def test_llm_service_success_api(self, mock_settings, mock_post):
        mock_settings.GEMINI_API_KEY = "valid_api_key"
        mock_settings.GEMINI_MODEL = "Gemini 2.5 Flash"
        
        # Setup mock response content representing strict JSON matching models with >30 words executive summary
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": """{
                                    "executive_summary": "Apple demonstrates very robust operational stability with growing profitability metrics across consumer electronics, services, and software segments. The company has stable operating margins and is well-positioned for future long-term compound growth.",
                                    "strengths": ["Strong cash reserves", "Global brand leadership"],
                                    "weaknesses": ["Supply chain constraints", "High valuation premiums"],
                                    "investment_thesis": "Hold for long-term compounding growth."
                                }"""
                            }
                        ]
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        service = LlmService()
        summary = service.generate_advisory_summary(
            self.overview, self.ratios, self.sentiment, self.risk
        )
        
        self.assertEqual(summary.ticker, "AAPL")
        self.assertEqual(summary.status, "Success")
        self.assertEqual(summary.model_name, "Gemini 2.5 Flash")
        self.assertEqual(len(summary.strengths), 2)
        self.assertEqual(len(summary.weaknesses), 2)

    @patch("services.ai.llm_service.requests.post")
    @patch("services.ai.llm_service.settings")
    def test_llm_service_rate_limit(self, mock_settings, mock_post):
        mock_settings.GEMINI_API_KEY = "valid_api_key"
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response

        service = LlmService()
        with self.assertRaises(ServiceError) as context:
            service.generate_advisory_summary(
                self.overview, self.ratios, self.sentiment, self.risk
            )
        self.assertIn("AI request limit has been reached", str(context.exception))

    @patch("services.ai.llm_service.requests.post")
    @patch("services.ai.llm_service.settings")
    def test_llm_service_unauthorized(self, mock_settings, mock_post):
        mock_settings.GEMINI_API_KEY = "invalid_api_key"
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_post.return_value = mock_response

        service = LlmService()
        with self.assertRaises(ServiceError) as context:
            service.generate_advisory_summary(
                self.overview, self.ratios, self.sentiment, self.risk
            )
        self.assertIn("AI service configuration error", str(context.exception))

    def test_summary_controller_incomplete_context(self):
        service = MagicMock()
        controller = SummaryController(service)
        
        # Test missing overview context
        with self.assertRaises(DataRetrievalError) as context:
            controller.get_summary("AAPL", None, self.ratios, self.sentiment, self.risk)
        self.assertIn("required financial information is incomplete", str(context.exception))

        # Test empty ratios model validation
        empty_ratios = FinancialRatios(ticker="AAPL", currency="USD")
        with self.assertRaises(DataRetrievalError) as context:
            controller.get_summary("AAPL", self.overview, empty_ratios, self.sentiment, self.risk)
        self.assertIn("required financial information is incomplete", str(context.exception))
