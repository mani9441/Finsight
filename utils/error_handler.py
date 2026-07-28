"""
Centralized exception mapping and log formatting for FinSight.
Maps runtime exceptions to user-friendly messages and redacts sensitive credentials.
"""

import logging
import re
import socket
import traceback
from datetime import datetime
import requests
from core.exceptions import InvalidInputError, DataRetrievalError, ServiceError

logger = logging.getLogger("error_handler")

def redact_sensitive_info(text: str) -> str:
    """Scrubs sensitive API keys or configuration strings from logs."""
    if not text:
        return text
    # Scrub Gemini API keys (usually start with AIzaSy)
    text = re.sub(r'key=AIzaSy[A-Za-z0-9_-]+', 'key=REDACTED', text)
    # Scrub general api_key or APIKey parameters in URLs or JSON
    text = re.sub(r'api_key[":\s]+[A-Za-z0-9_-]+', 'api_key: REDACTED', text)
    text = re.sub(r'([a-zA-Z0-9_]*api_?key[a-zA-Z0-9_]*[=:])([a-zA-Z0-9_-]{10,})', r'\1REDACTED', text, flags=re.IGNORECASE)
    return text

def get_redacted_traceback(e: Exception) -> str:
    """Generates the exception traceback with any sensitive keys redacted."""
    tb_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    return redact_sensitive_info(tb_str)

def is_connection_error(e: Exception) -> bool:
    """Identifies if the exception is due to connection issues or DNS resolution failure."""
    # Check current exception type
    if isinstance(e, (requests.exceptions.ConnectionError, requests.exceptions.Timeout, socket.timeout)):
        return True
    
    # Check causal exception chain
    cause = getattr(e, "__cause__", None)
    if cause and isinstance(cause, Exception):
        if is_connection_error(cause):
            return True
            
    # Check text details
    err_str = str(e).lower()
    indicators = [
        "connection timed out",
        "failed to connect",
        "connection failure",
        "dns resolution",
        "max retries exceeded",
        "newconnectionerror",
        "connection refused",
        "timeout",
        "socket.timeout"
    ]
    return any(ind in err_str for ind in indicators)

def is_rate_limit(e: Exception) -> bool:
    """Identifies if the exception is due to rate limits or API quotas being exceeded."""
    err_str = str(e).lower()
    indicators = [
        "429",
        "rate limit",
        "too many requests",
        "limit has been reached",
        "quota exceeded"
    ]
    return any(ind in err_str for ind in indicators)

def get_friendly_message(e: Exception, module_name: str) -> str:
    """
    Maps exceptions to standardized, non-technical, user-friendly strings.
    """
    # 1. Connection / Offline
    if is_connection_error(e):
        return "Unable to connect to the internet. Please check your connection and try again."

    # 2. Rate Limit Reached
    if is_rate_limit(e):
        return "Service request limit has been reached. Please try again later."

    err_str = str(e).lower()

    # 3. Contextual mapping based on module_name
    if module_name == "search":
        if isinstance(e, InvalidInputError):
            if "empty" in err_str or "please enter" in err_str or "please search" in err_str:
                return "Please search for a company before continuing."
            return str(e)
        if "not found" in err_str or "could not be found" in err_str:
            return "Company not found. Please enter a valid company name or stock ticker."
        return "Financial information is temporarily unavailable."

    elif module_name == "overview":
        if "not found" in err_str or "invalid ticker" in err_str:
            return "Company not found. Please enter a valid company name or stock ticker."
        if "incomplete" in err_str or "empty" in err_str or "missing" in err_str or "lacks identifying" in err_str:
            return "Financial data is currently unavailable for this company."
        return "Financial information is temporarily unavailable."

    elif module_name == "historical":
        return "Unable to display the historical stock chart."

    elif module_name == "ratios":
        if "incomplete" in err_str or "empty" in err_str or "missing" in err_str or "validation warning" in err_str:
            return "Financial data is currently unavailable for this company."
        return "Financial information is temporarily unavailable."

    elif module_name == "news":
        return "Unable to retrieve recent news articles."

    elif module_name == "risk":
        return "Unable to generate the risk indicator."

    elif module_name == "summary":
        return "AI summary is temporarily unavailable."

    # Fallback
    return "Financial information is temporarily unavailable."

def log_and_map_exception(e: Exception, module_name: str) -> str:
    """
    Logs technical exception details with timestamp and module scope,
    redacting API keys, and returns a friendly display message.
    """
    error_type = type(e).__name__
    timestamp = datetime.now().isoformat()
    error_desc_redacted = redact_sensitive_info(str(e))
    tb_redacted = get_redacted_traceback(e)
    
    # Log the sanitized diagnostic information
    logger.error(
        f"[{timestamp}] Module: {module_name} | ErrorType: {error_type} | Details: {error_desc_redacted}\nTraceback:\n{tb_redacted}"
    )
    
    return get_friendly_message(e, module_name)
