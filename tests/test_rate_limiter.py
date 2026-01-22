"""
Unit tests for Cin7 API rate limiter
"""

import pytest
import time
from cin7.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test rate limiter functionality"""

    def test_initialization(self):
        """Test rate limiter initialization"""
        limiter = RateLimiter(per_second=3, per_minute=60, per_day=5000)
        assert limiter.per_second == 3
        assert limiter.per_minute == 60
        assert limiter.per_day == 5000

    def test_single_request(self):
        """Test single request is allowed immediately"""
        limiter = RateLimiter(per_second=3)
        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start
        assert elapsed < 0.1  # Should be nearly instant

    def test_per_second_limit(self):
        """Test per-second rate limiting"""
        limiter = RateLimiter(per_second=2, per_minute=100, per_day=10000)

        # First 2 requests should be fast
        start = time.time()
        limiter.acquire()
        limiter.acquire()
        elapsed = time.time() - start
        assert elapsed < 0.2

        # Third request should wait ~1 second
        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start
        assert elapsed >= 0.9  # Should wait about 1 second

    def test_get_status(self):
        """Test status reporting"""
        limiter = RateLimiter(per_second=3, per_minute=60, per_day=5000)

        # Initial status
        status = limiter.get_status()
        assert status['per_second']['used'] == 0
        assert status['per_second']['remaining'] == 3

        # After one request
        limiter.acquire()
        status = limiter.get_status()
        assert status['per_second']['used'] == 1
        assert status['per_second']['remaining'] == 2

    def test_window_cleanup(self):
        """Test that old requests are removed from windows"""
        limiter = RateLimiter(per_second=2)

        # Make 2 requests
        limiter.acquire()
        limiter.acquire()

        # Status should show 2 used
        status = limiter.get_status()
        assert status['per_second']['used'] == 2

        # Wait for window to clear
        time.sleep(1.1)

        # Status should show 0 used
        status = limiter.get_status()
        assert status['per_second']['used'] == 0

    def test_multiple_tiers(self):
        """Test that all rate limit tiers are enforced"""
        limiter = RateLimiter(per_second=10, per_minute=20, per_day=1000)

        # Make 10 requests quickly (should hit per_second limit)
        for _ in range(10):
            limiter.acquire()

        # 11th request should wait
        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start
        assert elapsed >= 0.9

    @pytest.mark.slow
    def test_concurrent_safety(self):
        """Test thread safety (optional)"""
        import threading

        limiter = RateLimiter(per_second=5)
        counter = [0]

        def worker():
            limiter.acquire()
            counter[0] += 1

        threads = [threading.Thread(target=worker) for _ in range(10)]
        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        elapsed = time.time() - start

        # Should take at least 1 second to process 10 requests with limit of 5/sec
        assert elapsed >= 1.0
        assert counter[0] == 10
