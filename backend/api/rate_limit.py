"""
Rate Limiting Middleware for HealthGuard API

Provides simple in-memory rate limiting to protect against DoS attacks.
For production with multiple instances, consider using Redis-backed rate limiting.
"""

import time
from typing import Dict, Tuple
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from api.config import get_settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    In-memory rate limiting middleware.

    Tracks requests per IP address and enforces configurable rate limits.
    Note: This is a simple in-memory implementation. For production with
    multiple instances, use Redis-backed rate limiting (e.g., slowapi).
    """

    def __init__(self, app):
        super().__init__(app)
        # Store: {ip_address: [(timestamp, count), ...]}
        self.request_counts: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = 60  # Clean up old entries every 60 seconds
        self.last_cleanup = time.time()

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.

        Handles proxy headers (X-Forwarded-For) for accurate IP detection.

        Args:
            request: FastAPI request object

        Returns:
            Client IP address
        """
        # Check for proxy headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(",")[0].strip()

        # Check for other common proxy headers
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fall back to direct client IP
        if request.client:
            return request.client.host

        return "unknown"

    def _cleanup_old_entries(self):
        """Remove rate limit entries older than 1 minute."""
        current_time = time.time()

        if current_time - self.last_cleanup > self.cleanup_interval:
            cutoff_time = current_time - 60  # 60 seconds ago

            # Clean up old entries
            for ip in list(self.request_counts.keys()):
                self.request_counts[ip] = [(ts, count) for ts, count in self.request_counts[ip] if ts > cutoff_time]
                # Remove IP if no recent requests
                if not self.request_counts[ip]:
                    del self.request_counts[ip]

            self.last_cleanup = current_time

    def _check_rate_limit(self, ip: str, limit: int) -> Tuple[bool, int]:
        """
        Check if IP has exceeded rate limit.

        Args:
            ip: Client IP address
            limit: Maximum requests per minute

        Returns:
            Tuple of (is_allowed, current_count)
        """
        current_time = time.time()
        cutoff_time = current_time - 60  # 60 seconds ago

        # Filter requests within the last minute
        recent_requests = [(ts, count) for ts, count in self.request_counts[ip] if ts > cutoff_time]

        # Calculate total requests in the last minute
        total_requests = sum(count for _, count in recent_requests)

        # Update with filtered requests
        self.request_counts[ip] = recent_requests

        # Check if limit exceeded
        is_allowed = total_requests < limit

        if is_allowed:
            # Add current request
            self.request_counts[ip].append((current_time, 1))

        return is_allowed, total_requests

    async def dispatch(self, request: Request, call_next):
        """
        Process request and enforce rate limits.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint in chain

        Returns:
            Response from endpoint or rate limit error

        Raises:
            HTTPException: If rate limit is exceeded
        """
        settings = get_settings()

        # Skip rate limiting if disabled
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Skip rate limiting for health check endpoint
        if request.url.path == "/" or request.url.path == "/health":
            return await call_next(request)

        # Periodic cleanup
        self._cleanup_old_entries()

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Check rate limit
        is_allowed, current_count = self._check_rate_limit(client_ip, settings.rate_limit_requests)

        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for IP {client_ip}: " f"{current_count + 1}/{settings.rate_limit_requests} requests/min"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {settings.rate_limit_requests} requests per minute.",
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(settings.rate_limit_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_requests)
        response.headers["X-RateLimit-Remaining"] = str(settings.rate_limit_requests - current_count - 1)

        return response
