"""
Advanced Error Handling Utilities
==================================

Provides robust error handling for Enterprise Scanner:
- Retry logic with exponential backoff
- Circuit breaker pattern
- Fallback responses
- Error logging and monitoring
- Graceful degradation

Author: Enterprise Scanner Team
Version: 1.0.0
"""

import time
import logging
from functools import wraps
from typing import Callable, Any, Optional, Dict, List
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, stop calling
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit Breaker Pattern Implementation
    
    Prevents cascading failures by stopping calls to failing services.
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before trying again (half-open)
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or raises exception
        """
        if self.state == CircuitState.OPEN:
            # Check if timeout has elapsed
            if self.last_failure_time and \
               (datetime.now() - self.last_failure_time).seconds >= self.timeout:
                logger.info(f"Circuit breaker {func.__name__}: OPEN -> HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception(f"Circuit breaker OPEN for {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset if in half-open state
            if self.state == CircuitState.HALF_OPEN:
                logger.info(f"Circuit breaker {func.__name__}: HALF_OPEN -> CLOSED")
                self.failure_count = 0
                self.state = CircuitState.CLOSED
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            logger.error(f"Circuit breaker {func.__name__}: Failure {self.failure_count}/{self.failure_threshold}")
            
            # Open circuit if threshold reached
            if self.failure_count >= self.failure_threshold:
                logger.warning(f"Circuit breaker {func.__name__}: CLOSED -> OPEN")
                self.state = CircuitState.OPEN
            
            raise e
    
    def reset(self):
        """Reset circuit breaker to closed state"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        logger.info("Circuit breaker reset to CLOSED")


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each attempt
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch and retry
        
    Example:
        @retry_with_backoff(max_attempts=3, initial_delay=1.0)
        def api_call():
            return requests.get('https://api.example.com')
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
            
            raise last_exception
        
        return wrapper
    return decorator


def with_fallback(fallback_value: Any = None, log_errors: bool = True):
    """
    Decorator that provides fallback value on exception
    
    Args:
        fallback_value: Value to return if function fails
        log_errors: Whether to log errors
        
    Example:
        @with_fallback(fallback_value="Default response")
        def get_data():
            return api.fetch()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"{func.__name__} failed, using fallback: {e}")
                return fallback_value
        return wrapper
    return decorator


def with_timeout(seconds: float):
    """
    Decorator to enforce timeout on function execution
    
    Args:
        seconds: Maximum execution time in seconds
        
    Example:
        @with_timeout(30.0)
        def slow_operation():
            time.sleep(60)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"{func.__name__} exceeded {seconds}s timeout")
            
            # Set the signal handler
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(seconds))
            
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)  # Disable alarm
            
            return result
        return wrapper
    return decorator


class ErrorAggregator:
    """
    Aggregates and tracks errors for monitoring
    """
    
    def __init__(self, window_minutes: int = 60):
        """
        Initialize error aggregator
        
        Args:
            window_minutes: Time window for error tracking
        """
        self.window_minutes = window_minutes
        self.errors: List[Dict] = []
    
    def record_error(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict] = None
    ):
        """
        Record an error
        
        Args:
            error_type: Type/category of error
            message: Error message
            context: Additional context data
        """
        error_record = {
            'timestamp': datetime.now(),
            'type': error_type,
            'message': message,
            'context': context or {}
        }
        
        self.errors.append(error_record)
        self._cleanup_old_errors()
        
        logger.error(f"Error recorded - {error_type}: {message}")
    
    def _cleanup_old_errors(self):
        """Remove errors outside the time window"""
        cutoff = datetime.now() - timedelta(minutes=self.window_minutes)
        self.errors = [e for e in self.errors if e['timestamp'] > cutoff]
    
    def get_error_stats(self) -> Dict:
        """
        Get error statistics
        
        Returns:
            Dictionary with error counts and rates
        """
        self._cleanup_old_errors()
        
        total = len(self.errors)
        by_type = {}
        
        for error in self.errors:
            error_type = error['type']
            by_type[error_type] = by_type.get(error_type, 0) + 1
        
        return {
            'total_errors': total,
            'errors_by_type': by_type,
            'window_minutes': self.window_minutes,
            'error_rate': total / self.window_minutes  # Errors per minute
        }
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """
        Get most recent errors
        
        Args:
            limit: Maximum number of errors to return
            
        Returns:
            List of recent error records
        """
        self._cleanup_old_errors()
        return sorted(self.errors, key=lambda x: x['timestamp'], reverse=True)[:limit]


class GracefulDegradation:
    """
    Manages graceful degradation of features when services fail
    """
    
    def __init__(self):
        self.feature_status: Dict[str, bool] = {}
        self.fallback_responses: Dict[str, Any] = {}
    
    def register_feature(
        self,
        feature_name: str,
        enabled: bool = True,
        fallback: Any = None
    ):
        """
        Register a feature with fallback
        
        Args:
            feature_name: Name of the feature
            enabled: Initial enabled status
            fallback: Fallback value/response when disabled
        """
        self.feature_status[feature_name] = enabled
        if fallback is not None:
            self.fallback_responses[feature_name] = fallback
    
    def is_enabled(self, feature_name: str) -> bool:
        """Check if feature is enabled"""
        return self.feature_status.get(feature_name, False)
    
    def disable_feature(self, feature_name: str, reason: str = ""):
        """
        Disable a feature
        
        Args:
            feature_name: Name of feature to disable
            reason: Reason for disabling
        """
        self.feature_status[feature_name] = False
        logger.warning(f"Feature '{feature_name}' disabled: {reason}")
    
    def enable_feature(self, feature_name: str):
        """Enable a feature"""
        self.feature_status[feature_name] = True
        logger.info(f"Feature '{feature_name}' enabled")
    
    def get_fallback(self, feature_name: str) -> Any:
        """Get fallback response for disabled feature"""
        return self.fallback_responses.get(feature_name)
    
    def execute_with_fallback(
        self,
        feature_name: str,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with fallback if feature disabled
        
        Args:
            feature_name: Name of feature
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or fallback value
        """
        if not self.is_enabled(feature_name):
            logger.warning(f"Feature '{feature_name}' is disabled, using fallback")
            return self.get_fallback(feature_name)
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Feature '{feature_name}' failed: {e}")
            self.disable_feature(feature_name, reason=str(e))
            return self.get_fallback(feature_name)


# Global instances
error_aggregator = ErrorAggregator()
graceful_degradation = GracefulDegradation()


# Utility functions

def safe_api_call(
    func: Callable,
    fallback: Any = None,
    max_retries: int = 3,
    log_name: str = "API"
) -> Any:
    """
    Safely call an API with retry and fallback
    
    Args:
        func: API function to call
        fallback: Fallback value on failure
        max_retries: Number of retry attempts
        log_name: Name for logging
        
    Returns:
        API result or fallback value
    """
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except Exception as e:
            logger.warning(f"{log_name} attempt {attempt}/{max_retries} failed: {e}")
            
            if attempt == max_retries:
                logger.error(f"{log_name} failed after {max_retries} attempts")
                error_aggregator.record_error(
                    error_type=log_name,
                    message=str(e),
                    context={'attempts': max_retries}
                )
                return fallback
            
            time.sleep(2 ** (attempt - 1))  # Exponential backoff
    
    return fallback


def validate_and_sanitize(data: Any, schema: Dict) -> Dict:
    """
    Validate and sanitize input data
    
    Args:
        data: Input data to validate
        schema: Validation schema
        
    Returns:
        Validated and sanitized data
        
    Raises:
        ValueError: If validation fails
    """
    # TODO: Implement comprehensive validation
    return data


# Error response builders

def build_error_response(
    error: Exception,
    user_message: str = "An error occurred",
    include_details: bool = False
) -> Dict:
    """
    Build standardized error response
    
    Args:
        error: Exception that occurred
        user_message: User-friendly message
        include_details: Whether to include technical details
        
    Returns:
        Error response dictionary
    """
    response = {
        'error': True,
        'message': user_message,
        'timestamp': datetime.now().isoformat()
    }
    
    if include_details:
        response['details'] = {
            'type': type(error).__name__,
            'message': str(error)
        }
    
    return response


def handle_api_error(error: Exception, context: str = "") -> str:
    """
    Handle API errors and return user-friendly message
    
    Args:
        error: Exception that occurred
        context: Context where error occurred
        
    Returns:
        User-friendly error message
    """
    error_messages = {
        'ConnectionError': "Unable to connect to the service. Please check your internet connection.",
        'TimeoutError': "The request timed out. Please try again.",
        'HTTPError': "The server returned an error. Please try again later.",
        'APIKeyError': "API authentication failed. Please check your API key.",
        'RateLimitError': "Rate limit exceeded. Please wait a moment and try again.",
    }
    
    error_type = type(error).__name__
    message = error_messages.get(error_type, f"An unexpected error occurred: {error_type}")
    
    if context:
        message = f"{context}: {message}"
    
    logger.error(f"{message} - {str(error)}")
    return message
