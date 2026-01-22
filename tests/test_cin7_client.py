"""
Unit tests for Cin7 API client
"""

import pytest
import responses
from cin7.cin7_client import Cin7Client, Cin7APIError
import config


class TestCin7Client:
    """Test Cin7 API client"""

    def test_initialization_without_credentials(self):
        """Test that client raises error without credentials"""
        # Save original values
        original_key = config.CIN7_API_KEY
        original_secret = config.CIN7_API_SECRET

        try:
            config.CIN7_API_KEY = ""
            config.CIN7_API_SECRET = ""

            with pytest.raises(ValueError, match="credentials not configured"):
                Cin7Client()

        finally:
            # Restore original values
            config.CIN7_API_KEY = original_key
            config.CIN7_API_SECRET = original_secret

    def test_initialization_with_credentials(self):
        """Test successful initialization with credentials"""
        client = Cin7Client(api_key="test_key", api_secret="test_secret")
        assert client.api_key == "test_key"
        assert client.api_secret == "test_secret"

    @responses.activate
    def test_find_purchase_orders_success(self):
        """Test successful PO search"""
        # Mock API response
        responses.add(
            responses.GET,
            f"{config.CIN7_API_BASE_URL}/v1/PurchaseOrders",
            json=[
                {
                    "Id": "12345",
                    "Reference": "PO-12345",
                    "Supplier": {"Name": "Test Supplier"},
                    "Status": "Open"
                }
            ],
            status=200
        )

        client = Cin7Client(api_key="test", api_secret="test")
        results = client.find_purchase_orders("PO-12345")

        assert len(results) == 1
        assert results[0]['Reference'] == "PO-12345"

    @responses.activate
    def test_rate_limit_429_retry(self):
        """Test that 429 responses trigger retry"""
        # First response is 429, second is success
        responses.add(
            responses.GET,
            f"{config.CIN7_API_BASE_URL}/v1/PurchaseOrders",
            status=429,
            headers={"Retry-After": "1"}
        )
        responses.add(
            responses.GET,
            f"{config.CIN7_API_BASE_URL}/v1/PurchaseOrders",
            json=[{"Id": "12345"}],
            status=200
        )

        client = Cin7Client(api_key="test", api_secret="test")
        results = client.find_purchase_orders("PO-12345")

        # Should succeed after retry
        assert len(results) == 1

    @responses.activate
    def test_503_exponential_backoff(self):
        """Test 503 service unavailable with exponential backoff"""
        # Multiple 503 responses then success
        for _ in range(2):
            responses.add(
                responses.GET,
                f"{config.CIN7_API_BASE_URL}/v1/PurchaseOrders",
                status=503
            )
        responses.add(
            responses.GET,
            f"{config.CIN7_API_BASE_URL}/v1/PurchaseOrders",
            json=[{"Id": "12345"}],
            status=200
        )

        client = Cin7Client(api_key="test", api_secret="test")
        results = client.find_purchase_orders("PO-12345")

        assert len(results) == 1

    @responses.activate
    def test_max_retries_exceeded(self):
        """Test that max retries eventually fails"""
        # Always return 503
        for _ in range(10):
            responses.add(
                responses.GET,
                f"{config.CIN7_API_BASE_URL}/v1/PurchaseOrders",
                status=503
            )

        client = Cin7Client(api_key="test", api_secret="test")

        with pytest.raises(Cin7APIError, match="Max retries exceeded"):
            client.find_purchase_orders("PO-12345")

    @responses.activate
    def test_pagination(self):
        """Test pagination handling"""
        # Page 1 - full page
        responses.add(
            responses.GET,
            f"{config.CIN7_API_BASE_URL}/v1/PurchaseOrders",
            json=[{"Id": str(i)} for i in range(250)],
            status=200
        )
        # Page 2 - partial page (indicates end)
        responses.add(
            responses.GET,
            f"{config.CIN7_API_BASE_URL}/v1/PurchaseOrders",
            json=[{"Id": "250"}],
            status=200
        )

        client = Cin7Client(api_key="test", api_secret="test")
        results = client._paginate("v1/PurchaseOrders")

        assert len(results) == 251  # 250 + 1

    def test_get_rate_limit_status(self):
        """Test rate limit status reporting"""
        client = Cin7Client(api_key="test", api_secret="test")
        status = client.get_rate_limit_status()

        assert 'per_second' in status
        assert 'per_minute' in status
        assert 'per_day' in status
        assert status['per_second']['remaining'] == 3  # Default limit
