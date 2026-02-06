"""
Retry utility for API calls with exponential backoff and error classification

提供带指数退避的重试装饰器，用于处理外部 API 调用的临时故障。
"""
import time
import logging
import random
from functools import wraps
from typing import Callable, Any, Optional
import requests
from requests.exceptions import Timeout, ConnectionError, RequestException

logger = logging.getLogger(__name__)


class APICallError(Exception):
    """Base class for API call errors with context"""

    def __init__(
        self,
        message: str,
        error_type: str,
        original_error: Optional[Exception] = None
    ):
        self.message = message
        self.error_type = error_type  # 'timeout', 'connection', 'http_error', 'other'
        self.original_error = original_error
        super().__init__(self.message)


def is_timeout_error(error: Exception) -> bool:
    """
    Check if error is a timeout error

    Args:
        error: Exception to check

    Returns:
        True if error is a timeout error
    """
    error_str = str(error).lower()
    return (
        isinstance(error, Timeout) or
        'timeout' in error_str or
        'timed out' in error_str or
        'read timed out' in error_str
    )


def is_connection_error(error: Exception) -> bool:
    """
    Check if error is a connection error

    Args:
        error: Exception to check

    Returns:
        True if error is a connection error
    """
    return isinstance(error, ConnectionError) or 'connection' in str(error).lower()


def classify_error(error: Exception) -> str:
    """
    Classify error type for appropriate handling

    Args:
        error: Exception to classify

    Returns:
        Error type string: 'timeout', 'connection', 'http_error', 'other'
    """
    if is_timeout_error(error):
        return 'timeout'
    elif is_connection_error(error):
        return 'connection'
    elif isinstance(error, RequestException):
        return 'http_error'
    else:
        return 'other'


def retry_with_backoff(
    max_retries: int = 3,
    backoff_base: float = 1.0,
    retry_on_timeout: bool = True,
    retry_on_connection_error: bool = True,
    jitter: bool = True
):
    """
    Decorator for retrying API calls with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        backoff_base: Base backoff time in seconds (default: 1.0)
        retry_on_timeout: Whether to retry on timeout errors (default: True)
        retry_on_connection_error: Whether to retry on connection errors (default: True)
        jitter: Add random jitter to backoff to avoid thundering herd (default: True)

    Returns:
        Decorated function with retry logic

    Example:
        @retry_with_backoff(max_retries=3, backoff_base=1.0)
        def fetch_data(url):
            return requests.get(url)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    error_type = classify_error(e)

                    # Determine if we should retry
                    should_retry = False
                    if attempt < max_retries:
                        if error_type == 'timeout' and retry_on_timeout:
                            should_retry = True
                        elif error_type == 'connection' and retry_on_connection_error:
                            should_retry = True

                    if not should_retry:
                        # Log final error and raise
                        logger.error(
                            f"[Retry] {func.__name__} failed after {attempt + 1} attempts: "
                            f"error_type={error_type}, error={str(e)}"
                        )
                        raise APICallError(
                            message=f"{func.__name__} failed: {str(e)}",
                            error_type=error_type,
                            original_error=e
                        ) from e

                    # Calculate backoff with exponential increase and optional jitter
                    backoff = backoff_base * (2 ** attempt)
                    if jitter:
                        # Add random jitter: 0 to 50% of base backoff
                        backoff += random.uniform(0, 0.5 * backoff_base)

                    logger.warning(
                        f"[Retry] {func.__name__} attempt {attempt + 1}/{max_retries + 1} "
                        f"failed ({error_type}): {str(e)}. "
                        f"Retrying in {backoff:.2f}s..."
                    )
                    time.sleep(backoff)

        return wrapper
    return decorator
