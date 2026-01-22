"""
Rate limiter for Cin7 API compliance
Supports: 3/sec, 60/min, 5000/day
"""

import time
from collections import deque
from threading import Lock
from datetime import datetime, timedelta


class RateLimiter:
    """
    Multi-tier rate limiter for Cin7 API
    Enforces limits: 3/sec, 60/min, 5000/day
    """

    def __init__(self, per_second=3, per_minute=60, per_day=5000):
        self.per_second = per_second
        self.per_minute = per_minute
        self.per_day = per_day

        # Sliding window tracking
        self.second_window = deque()
        self.minute_window = deque()
        self.day_window = deque()

        self.lock = Lock()

    def _clean_windows(self, now: float):
        """Remove old timestamps outside the time windows"""
        second_ago = now - 1.0
        minute_ago = now - 60.0
        day_ago = now - 86400.0

        # Clean second window
        while self.second_window and self.second_window[0] < second_ago:
            self.second_window.popleft()

        # Clean minute window
        while self.minute_window and self.minute_window[0] < minute_ago:
            self.minute_window.popleft()

        # Clean day window
        while self.day_window and self.day_window[0] < day_ago:
            self.day_window.popleft()

    def _calculate_wait_time(self, now: float) -> float:
        """Calculate how long to wait before next request"""
        wait_times = []

        # Check second limit
        if len(self.second_window) >= self.per_second:
            oldest = self.second_window[0]
            wait_times.append(oldest + 1.0 - now)

        # Check minute limit
        if len(self.minute_window) >= self.per_minute:
            oldest = self.minute_window[0]
            wait_times.append(oldest + 60.0 - now)

        # Check day limit
        if len(self.day_window) >= self.per_day:
            oldest = self.day_window[0]
            wait_times.append(oldest + 86400.0 - now)

        return max(wait_times) if wait_times else 0

    def acquire(self):
        """
        Wait until a request can be made within rate limits
        Blocks until permission is granted
        """
        with self.lock:
            while True:
                now = time.time()
                self._clean_windows(now)

                wait_time = self._calculate_wait_time(now)

                if wait_time <= 0:
                    # Permission granted - record the request
                    self.second_window.append(now)
                    self.minute_window.append(now)
                    self.day_window.append(now)
                    return

                # Need to wait
                time.sleep(min(wait_time + 0.01, 1.0))  # Sleep in small increments

    def get_status(self) -> dict:
        """Get current rate limit status"""
        with self.lock:
            now = time.time()
            self._clean_windows(now)

            return {
                "per_second": {
                    "used": len(self.second_window),
                    "limit": self.per_second,
                    "remaining": self.per_second - len(self.second_window)
                },
                "per_minute": {
                    "used": len(self.minute_window),
                    "limit": self.per_minute,
                    "remaining": self.per_minute - len(self.minute_window)
                },
                "per_day": {
                    "used": len(self.day_window),
                    "limit": self.per_day,
                    "remaining": self.per_day - len(self.day_window)
                }
            }
