"""
Cin7 Omni API Client
Handles authentication, rate limiting, retries, and pagination
"""

import requests
import time
import logging
from typing import Optional, Dict, List, Any
from urllib.parse import urlencode, quote
import config
from cin7.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class Cin7APIError(Exception):
    """Custom exception for Cin7 API errors"""
    pass


class Cin7Client:
    """
    Cin7 Omni API client with rate limiting and retry logic
    """

    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key or config.CIN7_API_KEY
        self.api_secret = api_secret or config.CIN7_API_SECRET
        self.base_url = config.CIN7_API_BASE_URL

        if not self.api_key or not self.api_secret:
            raise ValueError("Cin7 API credentials not configured")

        # Rate limiter
        self.rate_limiter = RateLimiter(
            per_second=config.CIN7_RATE_LIMIT_PER_SECOND,
            per_minute=config.CIN7_RATE_LIMIT_PER_MINUTE,
            per_day=config.CIN7_RATE_LIMIT_PER_DAY
        )

        # Session for connection pooling
        self.session = requests.Session()
        self.session.auth = (self.api_key, self.api_secret)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        max_retries: int = 3
    ) -> Dict:
        """
        Make HTTP request with rate limiting and exponential backoff retry
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        for attempt in range(max_retries):
            try:
                # Wait for rate limiter permission
                self.rate_limiter.acquire()

                # Make request
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    timeout=30
                )

                # Handle rate limiting (429)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited (429). Waiting {retry_after}s")
                    time.sleep(retry_after)
                    continue

                # Handle service unavailable (503)
                if response.status_code == 503:
                    wait_time = (2 ** attempt) * 2  # Exponential backoff
                    logger.warning(f"Service unavailable (503). Retry {attempt + 1}/{max_retries} in {wait_time}s")
                    time.sleep(wait_time)
                    continue

                # Raise for other HTTP errors
                response.raise_for_status()

                # Success
                return response.json() if response.content else {}

            except requests.exceptions.RequestException as e:
                logger.error(f"Request error on attempt {attempt + 1}/{max_retries}: {e}")

                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 2
                    time.sleep(wait_time)
                else:
                    raise Cin7APIError(f"Max retries exceeded: {str(e)}")

        raise Cin7APIError("Request failed after all retries")

    def _paginate(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        page_size: int = 250
    ) -> List[Dict]:
        """
        Handle paginated responses
        Returns all results across all pages
        """
        all_results = []
        page = 1
        params = params or {}

        while True:
            params.update({"page": page, "rows": page_size})

            logger.info(f"Fetching page {page} from {endpoint}")
            response = self._make_request("GET", endpoint, params=params)

            # Handle different response formats
            if isinstance(response, list):
                results = response
            elif isinstance(response, dict) and "data" in response:
                results = response["data"]
            else:
                results = [response] if response else []

            if not results:
                break

            all_results.extend(results)

            # Check if more pages exist
            if len(results) < page_size:
                break

            page += 1

        logger.info(f"Retrieved {len(all_results)} total results from {endpoint}")
        return all_results

    def find_purchase_orders(self, reference: str) -> List[Dict]:
        """
        Find purchase orders by reference
        Supports exact match and wildcard search
        """
        # URL encode the reference for the where clause
        where_clause = f"Reference='{reference}'"
        encoded_where = quote(where_clause)

        params = {"where": where_clause}

        logger.info(f"Searching for PO: {reference}")
        results = self._paginate("v1/PurchaseOrders", params=params)

        return results

    def find_purchase_orders_by_base_ref(self, base_ref: str) -> List[Dict]:
        """
        Find purchase orders with LIKE query on base reference
        Used for finding backorder POs (e.g., PO-12345%)
        """
        # Use LIKE for wildcard matching
        where_clause = f"Reference LIKE '{base_ref}%'"
        params = {"where": where_clause}

        logger.info(f"Searching for POs starting with: {base_ref}")
        results = self._paginate("v1/PurchaseOrders", params=params)

        return results

    def get_purchase_order(self, po_id: str) -> Dict:
        """
        Get detailed purchase order by ID
        """
        logger.info(f"Fetching PO details: {po_id}")
        return self._make_request("GET", f"v1/PurchaseOrders/{po_id}")

    def update_purchase_order(self, po_id: str, po_data: Dict) -> Dict:
        """
        Update a purchase order (used for receipting)
        """
        logger.info(f"Updating PO: {po_id}")
        return self._make_request("PUT", f"v1/PurchaseOrders/{po_id}", data=po_data)

    def get_suppliers(self, name_filter: Optional[str] = None) -> List[Dict]:
        """
        Get suppliers, optionally filtered by name
        """
        params = {}
        if name_filter:
            params["where"] = f"Name LIKE '%{name_filter}%'"

        logger.info("Fetching suppliers")
        return self._paginate("v1/Suppliers", params=params)

    def get_rate_limit_status(self) -> Dict:
        """Get current rate limit status"""
        return self.rate_limiter.get_status()

    def close(self):
        """Close the HTTP session"""
        self.session.close()
