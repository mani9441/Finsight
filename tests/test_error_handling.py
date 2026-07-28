import unittest
import requests
import socket
from unittest.mock import patch, MagicMock
from core.exceptions import InvalidInputError, DataRetrievalError
from utils.error_handler import (
    redact_sensitive_info,
    is_connection_error,
    is_rate_limit,
    get_friendly_message,
    log_and_map_exception
)

class TestErrorHandling(unittest.TestCase):

    def test_redact_sensitive_info(self):
        # Gemini key pattern in URL
        url_with_key = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=AIzaSyA1B2C3D4E5"
        self.assertIn("key=REDACTED", redact_sensitive_info(url_with_key))
        self.assertNotIn("AIzaSyA1B2C3D4E5", redact_sensitive_info(url_with_key))

        # JSON key patterns
        json_key = '{"api_key": "AIzaSyXyZ123"}'
        self.assertIn('"api_key: REDACTED"', redact_sensitive_info(json_key))

        # Random query param with key
        query_key = "http://localhost:8000/?apiKey=AIzaSyTest"
        self.assertIn("apiKey=REDACTED", redact_sensitive_info(query_key))

    def test_is_connection_error(self):
        # Built-in exception types
        self.assertTrue(is_connection_error(requests.exceptions.ConnectionError("Failed to connect")))
        self.assertTrue(is_connection_error(requests.exceptions.Timeout("Timeout occurred")))
        self.assertTrue(is_connection_error(socket.timeout("Socket timeout")))

        # Causal exception
        base_err = Exception("Base connection timed out")
        wrapper_err = DataRetrievalError("Failed overview")
        wrapper_err.__cause__ = base_err
        self.assertTrue(is_connection_error(wrapper_err))

        # Standard exceptions that are not connection errors
        self.assertFalse(is_connection_error(ValueError("Invalid value")))

    def test_is_rate_limit(self):
        self.assertTrue(is_rate_limit(Exception("Gemini API Error 429: Too Many Requests")))
        self.assertTrue(is_rate_limit(Exception("AI request limit has been reached")))
        self.assertFalse(is_rate_limit(Exception("General 500 error")))

    def test_get_friendly_message(self):
        conn_err = requests.exceptions.ConnectionError("offline")
        rate_err = Exception("Error 429 limit reached")
        
        # 1. Test offline error mapping across any module
        self.assertEqual(
            get_friendly_message(conn_err, "overview"),
            "Unable to connect to the internet. Please check your connection and try again."
        )
        self.assertEqual(
            get_friendly_message(conn_err, "summary"),
            "Unable to connect to the internet. Please check your connection and try again."
        )

        # 2. Test rate limit mapping across any module
        self.assertEqual(
            get_friendly_message(rate_err, "overview"),
            "Service request limit has been reached. Please try again later."
        )
        self.assertEqual(
            get_friendly_message(rate_err, "summary"),
            "Service request limit has been reached. Please try again later."
        )

        # 3. Test context-specific mappings
        # Search / Resolution
        self.assertEqual(
            get_friendly_message(InvalidInputError("Please search for a company before continuing."), "search"),
            "Please search for a company before continuing."
        )
        self.assertEqual(
            get_friendly_message(Exception("company could not be found"), "search"),
            "Company not found. Please enter a valid company name or stock ticker."
        )
        # Overview
        self.assertEqual(
            get_friendly_message(Exception("incomplete yfinance payload"), "overview"),
            "Financial data is currently unavailable for this company."
        )
        # Historical
        self.assertEqual(
            get_friendly_message(Exception("any chart failure"), "historical"),
            "Unable to display the historical stock chart."
        )
        # Ratios
        self.assertEqual(
            get_friendly_message(Exception("ratios validation warning"), "ratios"),
            "Financial data is currently unavailable for this company."
        )
        # News
        self.assertEqual(
            get_friendly_message(Exception("news failed"), "news"),
            "Unable to retrieve recent news articles."
        )
        # Risk
        self.assertEqual(
            get_friendly_message(Exception("risk rules failed"), "risk"),
            "Unable to generate the risk indicator."
        )
        # Summary
        self.assertEqual(
            get_friendly_message(Exception("Gemini failed"), "summary"),
            "AI summary is temporarily unavailable."
        )

    @patch("utils.error_handler.logger")
    def test_log_and_map_exception(self, mock_logger):
        # Verify it logs the redacted content and returns friendly message
        e = Exception("General failure querying Gemini URL key=AIzaSySecretCode")
        msg = log_and_map_exception(e, "summary")
        
        self.assertEqual(msg, "AI summary is temporarily unavailable.")
        
        # Check logger.error was called
        mock_logger.error.assert_called_once()
        log_arg = mock_logger.error.call_args[0][0]
        self.assertIn("key=REDACTED", log_arg)
        self.assertNotIn("AIzaSySecretCode", log_arg)
