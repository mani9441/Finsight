"""
Common HTTP Client for external service integrations.
Handles sessions, request retries, timeout parameters, and raises core exceptions on failure.
"""

import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from typing import Dict, Any, Optional

from core import get_logger
from core.exceptions import ServiceError

logger = get_logger("api_client")

class ApiClient:
    """
    Standardized HTTP client using requests session, retries, and clean error handling.
    """

    def __init__(self, base_url: str = "", default_headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Configure standard headers to bypass generic scraping blocks
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*"
        }
        if default_headers:
            self.headers.update(default_headers)
        
        self.session.headers.update(self.headers)
        
        # Setup retry adapter (retry on 5xx errors after exponential backoff)
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None, 
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout_seconds: float = 10.0
    ) -> requests.Response:
        """
        Executes an HTTP request. Maps standard connection errors to ServiceError.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}" if self.base_url else endpoint
        method = method.upper()
        
        logger.info(f"API Request: {method} {url} | Params: {params}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=headers,
                timeout=timeout_seconds
            )
            
            # Check for bad status code responses
            response.raise_for_status()
            logger.debug(f"API Response: {response.status_code} | Time: {response.elapsed.total_seconds()}s")
            return response
            
        except requests.exceptions.Timeout as e:
            logger.error(f"API Timeout to {url}: {e}")
            raise ServiceError(f"Connection timeout during request to: {url}") from e
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"API Connection failure to {url}: {e}")
            raise ServiceError(f"Failed to connect to external service at: {url}") from e
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "Unknown"
            logger.error(f"API HTTP Error {status_code} from {url}: {e}")
            raise ServiceError(f"HTTP Error {status_code} returned by service at: {url}") from e
            
        except Exception as e:
            logger.error(f"Unexpected request error: {e}")
            raise ServiceError(f"Unexpected connection error querying service at {url}: {str(e)}") from e
