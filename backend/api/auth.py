"""
Authentication Middleware for HealthGuard API

Provides API key-based authentication for securing endpoints.
"""

from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from api.config import get_settings

# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Verify API key from request header.

    This dependency can be added to any endpoint that requires authentication.

    Args:
        api_key: API key from X-API-Key header

    Returns:
        Valid API key

    Raises:
        HTTPException: If API key is missing or invalid

    Example:
        @app.get("/protected", dependencies=[Depends(verify_api_key)])
        async def protected_endpoint():
            return {"message": "Authenticated"}
    """
    settings = get_settings()

    # If API key authentication is disabled, allow all requests
    if not settings.api_key_enabled:
        return "authentication_disabled"

    # Check if API key is provided
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include X-API-Key header in your request.",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    # Validate API key
    valid_keys = settings.api_keys_list
    if not valid_keys:
        # No keys configured - this is a configuration error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key authentication is enabled but no keys are configured"
        )

    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    return api_key


def get_optional_api_key(api_key: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """
    Optional API key verification for endpoints that support both authenticated and public access.

    Args:
        api_key: API key from X-API-Key header

    Returns:
        Valid API key or None if not provided/invalid
    """
    settings = get_settings()

    if not settings.api_key_enabled:
        return None

    if not api_key:
        return None

    if api_key in settings.api_keys_list:
        return api_key

    return None
