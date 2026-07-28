import unittest
from unittest.mock import patch
import streamlit as st
from models import CompanyOverview, FinancialRatios, SentimentResult, RiskAssessment, AISummary
from utils.session_cache import (
    initialize_overview_session,
    get_cached_overview,
    set_cached_overview,
    clear_overview_cache,
    
    initialize_historical_session,
    get_cached_historical_prices,
    set_cached_historical_prices,
    get_selected_time_range,
    set_selected_time_range,
    clear_historical_cache,
    
    initialize_ratios_session,
    get_cached_ratios,
    set_cached_ratios,
    clear_ratios_cache,
    
    initialize_news_session,
    get_cached_news,
    set_cached_news,
    get_cached_sentiment,
    set_cached_sentiment,
    clear_news_cache,
    
    initialize_risk_session,
    get_cached_risk,
    set_cached_risk,
    clear_risk_cache,
    
    initialize_summary_session,
    get_cached_summary,
    set_cached_summary,
    clear_summary_cache,
    
    initialize_dashboard_visibility_session,
    get_dashboard_visibility,
    set_dashboard_visibility,
    clear_all_caches
)

class TestSessionManagement(unittest.TestCase):

    def setUp(self):
        # Mock st.session_state as a standard dictionary
        self.session_dict = {}
        # Apply patch to streamlit session state
        self.patcher = patch.object(st, "session_state", self.session_dict)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_overview_caching(self):
        initialize_overview_session()
        self.assertIn("overview_data", self.session_dict)
        self.assertIsNone(get_cached_overview())
        
        overview = CompanyOverview(
            ticker="AAPL",
            name="Apple Inc.",
            exchange="NASDAQ",
            currency="USD",
            sector="Technology",
            industry="Consumer Electronics",
            country="US",
            website="https://apple.com",
            business_summary="Summary"
        )
        set_cached_overview(overview)
        self.assertEqual(get_cached_overview(), overview)
        
        clear_overview_cache()
        self.assertIsNone(get_cached_overview())

    def test_historical_caching(self):
        initialize_historical_session()
        self.assertEqual(get_selected_time_range(), "1 Year")
        
        set_selected_time_range("5 Years")
        self.assertEqual(get_selected_time_range(), "5 Years")
        
        set_cached_historical_prices([])
        self.assertEqual(get_cached_historical_prices(), [])
        
        clear_historical_cache()
        self.assertIsNone(get_cached_historical_prices())
        # Ticker selection range should persist across normal clears
        self.assertEqual(get_selected_time_range(), "5 Years")

    def test_ratios_caching(self):
        initialize_ratios_session()
        self.assertIsNone(get_cached_ratios())
        
        ratios = FinancialRatios(ticker="AAPL", currency="USD")
        set_cached_ratios(ratios)
        self.assertEqual(get_cached_ratios(), ratios)
        
        clear_ratios_cache()
        self.assertIsNone(get_cached_ratios())

    def test_news_and_sentiment_caching(self):
        initialize_news_session()
        self.assertIsNone(get_cached_news())
        self.assertIsNone(get_cached_sentiment())
        
        set_cached_news([])
        set_cached_sentiment(SentimentResult(ticker="AAPL", average_score=0.1, sentiment_label="Neutral", article_count=0, positive_count=0, neutral_count=0, negative_count=0))
        self.assertEqual(get_cached_news(), [])
        self.assertIsNotNone(get_cached_sentiment())
        
        clear_news_cache()
        self.assertIsNone(get_cached_news())
        self.assertIsNone(get_cached_sentiment())

    def test_risk_caching(self):
        initialize_risk_session()
        self.assertIsNone(get_cached_risk())
        
        risk = RiskAssessment(ticker="AAPL", risk_score=10, risk_level="Low Risk", risk_explanation="Explain")
        set_cached_risk(risk)
        self.assertEqual(get_cached_risk(), risk)
        
        clear_risk_cache()
        self.assertIsNone(get_cached_risk())

    def test_summary_caching(self):
        initialize_summary_session()
        self.assertIsNone(get_cached_summary())
        
        summary = AISummary(ticker="AAPL", executive_summary="Summary", investment_thesis="Thesis", strengths=[], weaknesses=[], model_name="Gemini 2.5 Flash", status="Success")
        set_cached_summary(summary)
        self.assertEqual(get_cached_summary(), summary)
        
        clear_summary_cache()
        self.assertIsNone(get_cached_summary())

    def test_dashboard_visibility_session(self):
        initialize_dashboard_visibility_session()
        self.assertFalse(get_dashboard_visibility())
        
        set_dashboard_visibility(True)
        self.assertTrue(get_dashboard_visibility())

    def test_clear_all_caches(self):
        initialize_overview_session()
        initialize_historical_session()
        initialize_ratios_session()
        initialize_news_session()
        initialize_risk_session()
        initialize_summary_session()
        
        # Populate
        set_cached_overview(CompanyOverview(ticker="AAPL", name="Apple Inc.", exchange="NASDAQ", currency="USD", sector="Tech", industry="CE", country="US", website="a.com", business_summary="b"))
        set_cached_historical_prices([])
        set_cached_ratios(FinancialRatios(ticker="AAPL", currency="USD"))
        set_cached_news([])
        set_cached_sentiment(SentimentResult(ticker="AAPL", average_score=0.1, sentiment_label="Neutral", article_count=0, positive_count=0, neutral_count=0, negative_count=0))
        set_cached_risk(RiskAssessment(ticker="AAPL", risk_score=10, risk_level="Low Risk", risk_explanation="Explain"))
        set_cached_summary(AISummary(ticker="AAPL", executive_summary="Summary", investment_thesis="Thesis", strengths=[], weaknesses=[], model_name="Gemini 2.5 Flash", status="Success"))
        
        # Verify populated
        self.assertIsNotNone(get_cached_overview())
        self.assertIsNotNone(get_cached_historical_prices())
        self.assertIsNotNone(get_cached_ratios())
        self.assertIsNotNone(get_cached_news())
        self.assertIsNotNone(get_cached_sentiment())
        self.assertIsNotNone(get_cached_risk())
        self.assertIsNotNone(get_cached_summary())
        
        # Clear all
        clear_all_caches()
        
        # Verify cleared
        self.assertIsNone(get_cached_overview())
        self.assertIsNone(get_cached_historical_prices())
        self.assertIsNone(get_cached_ratios())
        self.assertIsNone(get_cached_news())
        self.assertIsNone(get_cached_sentiment())
        self.assertIsNone(get_cached_risk())
        self.assertIsNone(get_cached_summary())
