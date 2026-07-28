import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from models import FinancialRatios, SentimentResult, RiskAssessment
from services.common.risk_validator import RiskValidator
from services.finance.risk_rules_engine import RiskRulesEngine
from services.finance.risk_service import RiskEvaluationService
from services.finance.risk_controller import RiskController
from core.exceptions import DataRetrievalError

class TestRiskIndicatorModule(unittest.TestCase):

    def setUp(self):
        # 1. Clean positive ratios & sentiment -> Low Risk
        self.clean_ratios = FinancialRatios(
            ticker="AAPL",
            currency="USD",
            pe_ratio=20.0,
            pb_ratio=3.0,
            roe=0.18,
            profit_margin=0.12,
            dividend_yield=0.015,
            eps=4.5
        )
        self.positive_sentiment = SentimentResult(
            ticker="AAPL",
            average_score=0.25,
            sentiment_label="Positive",
            article_count=10,
            positive_count=6,
            negative_count=1,
            neutral_count=3
        )

        # 2. Moderate risk ratios & sentiment -> Moderate Risk
        self.moderate_ratios = FinancialRatios(
            ticker="AAPL",
            currency="USD",
            pe_ratio=40.0,         # Valuation factor flagged
            pb_ratio=3.0,
            roe=-0.05,             # Profitability factor flagged
            profit_margin=0.12,
            dividend_yield=0.0,
            eps=1.5
        )
        self.neutral_sentiment = SentimentResult(
            ticker="AAPL",
            average_score=0.0,
            sentiment_label="Neutral",
            article_count=10,
            positive_count=3,
            negative_count=3,
            neutral_count=4
        )

        # 3. High risk ratios & sentiment -> High Risk
        self.high_risk_ratios = FinancialRatios(
            ticker="AAPL",
            currency="USD",
            pe_ratio=50.0,         # Valuation factor flagged
            pb_ratio=8.0,          # Valuation factor flagged
            roe=-0.10,             # Profitability factor flagged
            profit_margin=-0.04,   # Profitability factor flagged
            dividend_yield=0.0,
            eps=-2.0               # Profitability factor flagged
        )
        self.negative_sentiment = SentimentResult(
            ticker="AAPL",
            average_score=-0.20,
            sentiment_label="Negative", # Sentiment factor flagged
            article_count=10,
            positive_count=1,
            negative_count=7,
            neutral_count=2
        )

    def test_risk_validator_missing_objects(self):
        # Missing ratios
        with self.assertRaises(DataRetrievalError) as context:
            RiskValidator.validate_inputs(None, self.positive_sentiment)
        self.assertIn("financial information is unavailable", str(context.exception))

        # Missing sentiment
        with self.assertRaises(DataRetrievalError) as context:
            RiskValidator.validate_inputs(self.clean_ratios, None)
        self.assertIn("sentiment analysis is unavailable", str(context.exception))

    def test_risk_validator_incomplete_fields(self):
        # Empty ratios model
        empty_ratios = FinancialRatios(ticker="AAPL", currency="USD")
        with self.assertRaises(DataRetrievalError) as context:
            RiskValidator.validate_inputs(empty_ratios, self.positive_sentiment)
        self.assertIn("Additional information is required", str(context.exception))

    def test_risk_rules_engine_low_risk(self):
        factors, level, score = RiskRulesEngine.evaluate_factors(self.clean_ratios, self.positive_sentiment)
        self.assertEqual(len(factors), 0)
        self.assertEqual(level, "Low Risk")
        self.assertEqual(score, 15.0)

    def test_risk_rules_engine_moderate_risk(self):
        factors, level, score = RiskRulesEngine.evaluate_factors(self.moderate_ratios, self.neutral_sentiment)
        # PE > 35, ROE < 0 -> 2 factors flagged
        self.assertEqual(len(factors), 2)
        self.assertEqual(level, "Moderate Risk")
        self.assertEqual(score, 50.0)
        self.assertIn("High P/E valuation", factors[0])
        self.assertIn("Negative Return on Equity", factors[1])

    def test_risk_rules_engine_high_risk(self):
        factors, level, score = RiskRulesEngine.evaluate_factors(self.high_risk_ratios, self.negative_sentiment)
        # PE > 35, PB > 6, ROE < 0, margin < 0, EPS < 0, sentiment Negative -> 6 factors flagged
        self.assertEqual(len(factors), 6)
        self.assertEqual(level, "High Risk")
        self.assertEqual(score, 85.0)

    def test_risk_evaluation_service(self):
        service = RiskEvaluationService()
        
        # Test low risk explanation
        assessment_low = service.evaluate_risk("AAPL", self.clean_ratios, self.positive_sentiment)
        self.assertEqual(assessment_low.risk_level, "Low Risk")
        self.assertIn("low risk signals", assessment_low.risk_explanation)

        # Test moderate risk explanation
        assessment_mod = service.evaluate_risk("AAPL", self.moderate_ratios, self.neutral_sentiment)
        self.assertEqual(assessment_mod.risk_level, "Moderate Risk")
        self.assertIn("Moderate investment risk indicators detected", assessment_mod.risk_explanation)

        # Test high risk explanation
        assessment_high = service.evaluate_risk("AAPL", self.high_risk_ratios, self.negative_sentiment)
        self.assertEqual(assessment_high.risk_level, "High Risk")
        self.assertIn("High risk signals detected", assessment_high.risk_explanation)

    @patch("services.finance.risk_service.RiskEvaluationService")
    def test_risk_controller(self, mock_service_class):
        mock_service = MagicMock()
        expected_assessment = RiskAssessment(
            ticker="AAPL",
            risk_score=15.0,
            risk_level="Low Risk",
            risk_explanation="Clean low risk metrics"
        )
        mock_service.evaluate_risk.return_value = expected_assessment
        
        controller = RiskController(mock_service)
        assessment = controller.get_risk_assessment("AAPL", self.clean_ratios, self.positive_sentiment)
        
        self.assertEqual(assessment, expected_assessment)
        mock_service.evaluate_risk.assert_called_once_with("AAPL", self.clean_ratios, self.positive_sentiment)
