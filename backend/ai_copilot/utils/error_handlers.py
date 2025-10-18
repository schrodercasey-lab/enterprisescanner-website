"""
Error Handlers for AI Copilot

Centralized error handling and recovery mechanisms.

Author: Enterprise Scanner Team
Version: 1.0.0
"""

import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CopilotError(Exception):
    """Base exception for AI Copilot"""
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        self.message = message
        self.severity = severity
        super().__init__(self.message)


class AccessDeniedError(CopilotError):
    """Raised when access is denied"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, ErrorSeverity.MEDIUM)


class RateLimitError(CopilotError):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, ErrorSeverity.LOW)


class ValidationError(CopilotError):
    """Raised when input validation fails"""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, ErrorSeverity.LOW)


class LLMError(CopilotError):
    """Raised when LLM provider fails"""
    def __init__(self, message: str = "LLM provider error"):
        super().__init__(message, ErrorSeverity.HIGH)


class DatabaseError(CopilotError):
    """Raised when database operation fails"""
    def __init__(self, message: str = "Database error"):
        super().__init__(message, ErrorSeverity.HIGH)


class ErrorHandler:
    """
    Centralized error handling system
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_stats = {
            'total_errors': 0,
            'by_type': {},
            'by_severity': {
                'low': 0,
                'medium': 0,
                'high': 0,
                'critical': 0
            }
        }
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle error and return standardized response
        
        Args:
            error: Exception that occurred
            context: Additional context
            user_message: User-friendly message
            
        Returns:
            Error response dict
        """
        # Update statistics
        self.error_stats['total_errors'] += 1
        error_type = type(error).__name__
        self.error_stats['by_type'][error_type] = \
            self.error_stats['by_type'].get(error_type, 0) + 1
        
        # Determine severity
        if isinstance(error, CopilotError):
            severity = error.severity.value
            self.error_stats['by_severity'][severity] += 1
        else:
            severity = 'medium'
            self.error_stats['by_severity']['medium'] += 1
        
        # Log error
        log_message = f"Error: {error_type} - {str(error)}"
        if context:
            log_message += f" | Context: {context}"
        
        if severity in ['critical', 'high']:
            self.logger.error(log_message, exc_info=True)
        else:
            self.logger.warning(log_message)
        
        # Build response
        response = {
            'success': False,
            'error': {
                'type': error_type,
                'message': user_message or self._get_user_message(error),
                'severity': severity
            }
        }
        
        # Add recovery suggestions
        recovery = self._get_recovery_suggestions(error)
        if recovery:
            response['error']['recovery'] = recovery
        
        return response
    
    def _get_user_message(self, error: Exception) -> str:
        """Get user-friendly error message"""
        if isinstance(error, AccessDeniedError):
            return "You don't have permission to perform this action."
        
        elif isinstance(error, RateLimitError):
            return "You've made too many requests. Please wait a moment and try again."
        
        elif isinstance(error, ValidationError):
            return f"Invalid input: {str(error)}"
        
        elif isinstance(error, LLMError):
            return "Our AI service is temporarily unavailable. Please try again."
        
        elif isinstance(error, DatabaseError):
            return "We're experiencing technical difficulties. Please try again later."
        
        else:
            return "An unexpected error occurred. Our team has been notified."
    
    def _get_recovery_suggestions(self, error: Exception) -> Optional[list]:
        """Get recovery suggestions"""
        if isinstance(error, AccessDeniedError):
            return [
                "Contact your administrator for elevated permissions",
                "Sign in with a different account",
                "Review your access level requirements"
            ]
        
        elif isinstance(error, RateLimitError):
            return [
                "Wait a few minutes before trying again",
                "Upgrade your plan for higher limits",
                "Reduce query frequency"
            ]
        
        elif isinstance(error, ValidationError):
            return [
                "Check your input format",
                "Review required fields",
                "See documentation for examples"
            ]
        
        elif isinstance(error, LLMError):
            return [
                "Try again in a moment",
                "Rephrase your query",
                "Contact support if issue persists"
            ]
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return self.error_stats.copy()


def handle_errors(fallback_response: Optional[str] = None):
    """
    Decorator for error handling
    
    Args:
        fallback_response: Response to return on error
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger = logging.getLogger(func.__module__)
                logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                
                if fallback_response:
                    return fallback_response
                else:
                    raise
        
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator for retrying on failure
    
    Args:
        max_retries: Maximum retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        raise
            
            raise last_exception
        
        return wrapper
    return decorator


# Export
__all__ = [
    'ErrorHandler',
    'CopilotError',
    'AccessDeniedError',
    'RateLimitError',
    'ValidationError',
    'LLMError',
    'DatabaseError',
    'ErrorSeverity',
    'handle_errors',
    'retry_on_failure'
]
