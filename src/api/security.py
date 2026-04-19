import hmac
import os
import threading
import time

from typing import Dict
from fastapi import HTTPException


# Security utilities for API key verification and rate limiting based on user ID
API_KEY_HEADER_NAME = "X-API-Key"
API_KEY_ENV_NAME = "COIN_COUNTER_API_KEY"
RATE_LIMIT_WINDOW_SECONDS = float(os.getenv("COIN_COUNTER_RATE_LIMIT_SECONDS", "5"))

# Load API key from environment variable
_api_key = os.getenv(API_KEY_ENV_NAME)
if not _api_key:
    raise RuntimeError(f"Missing required environment variable: {API_KEY_ENV_NAME}")

# In-memory store for tracking last request timestamps per user for rate limiting
_rate_limit_lock = threading.Lock()
_user_last_request_ts: Dict[str, float] = {}


def normalize_user_id(raw_user_id: str | None) -> str:
    """Normalize and validate user ID for rate limiting"""
    user_id = (raw_user_id or "").strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing user_id")
    if len(user_id) > 128:
        raise HTTPException(status_code=400, detail="user_id is too long")
    return user_id


def verify_api_key(x_api_key: str | None) -> None:
    """Verify the provided API key against the expected value"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    if not hmac.compare_digest(x_api_key, _api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")


def enforce_rate_limit(user_id: str) -> None:
    """Enforce rate limit based on user ID and configured time window"""
    now = time.monotonic()

    # Use a lock to ensure thread-safe access to the rate limit tracking dictionary
    with _rate_limit_lock:
        last_ts = _user_last_request_ts.get(user_id)
        if last_ts is not None:
            elapsed = now - last_ts
            # If the last request was within the rate limit window, reject with 429 Too Many Requests
            if elapsed < RATE_LIMIT_WINDOW_SECONDS:
                retry_after = max(1, int(RATE_LIMIT_WINDOW_SECONDS - elapsed))
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please wait before retrying.",
                    headers={"Retry-After": str(retry_after)},
                )

        _user_last_request_ts[user_id] = now

        # Clean up old entries to prevent unbounded growth of the tracking dictionary
        if len(_user_last_request_ts) > 10000:
            cutoff = now - (RATE_LIMIT_WINDOW_SECONDS * 10)
            stale_users = [key for key, ts in _user_last_request_ts.items() if ts < cutoff]
            for key in stale_users:
                _user_last_request_ts.pop(key, None)
