"""
Error handling utilities for the Options Pricing Calculator
"""
import streamlit as st
import traceback
from typing import Any, Callable, Dict, Optional, Type, Union
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class CalculationError(Exception):
    """Custom exception for calculation errors"""
    pass


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class DataError(Exception):
    """Custom exception for data-related errors"""
    pass


class UIError(Exception):
    """Custom exception for UI-related errors"""
    pass


class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def handle_error(error: Exception, 
                    context: str = "Unknown", 
                    show_in_ui: bool = True,
                    log_error: bool = True) -> None:
        """Handle errors with logging and optional UI display"""
        if log_error:
            logger.error(f"Error in {context}: {str(error)}")
            logger.debug(f"Full traceback: {traceback.format_exc()}")
        
        if show_in_ui:
            if isinstance(error, ValidationError):
                st.error(f"Validation Error: {str(error)}")
            elif isinstance(error, CalculationError):
                st.error(f"Calculation Error: {str(error)}")
            elif isinstance(error, DataError):
                st.error(f"Data Error: {str(error)}")
            elif isinstance(error, UIError):
                st.error(f"UI Error: {str(error)}")
            else:
                st.error(f"Error in {context}: {str(error)}")
    
    @staticmethod
    def handle_warning(message: str, 
                      context: str = "Unknown",
                      show_in_ui: bool = True,
                      log_warning: bool = True) -> None:
        """Handle warnings with logging and optional UI display"""
        if log_warning:
            logger.warning(f"Warning in {context}: {message}")
        
        if show_in_ui:
            st.warning(f"{message}")
    
    @staticmethod
    def handle_info(message: str,
                   context: str = "Unknown",
                   show_in_ui: bool = True,
                   log_info: bool = True) -> None:
        """Handle info messages with logging and optional UI display"""
        if log_info:
            logger.info(f"Info in {context}: {message}")
        
        if show_in_ui:
            st.info(f"{message}")
    
    @staticmethod
    def safe_execute(func: Callable, 
                    context: str = "Unknown",
                    default_return: Any = None,
                    show_errors: bool = True) -> Any:
        """Safely execute a function with error handling"""
        try:
            return func()
        except Exception as e:
            ErrorHandler.handle_error(e, context=context, show_in_ui=show_errors)
            return default_return


def error_handler(context: str = None, 
                 default_return: Any = None,
                 show_in_ui: bool = True,
                 re_raise: bool = False):
    """Decorator for error handling"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_context = context or f"{func.__module__}.{func.__name__}"
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.handle_error(e, context=func_context, show_in_ui=show_in_ui)
                if re_raise:
                    raise
                return default_return
        return wrapper
    return decorator


def validation_handler(func: Callable) -> Callable:
    """Decorator specifically for validation functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Validation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in validation: {e}")
            raise ValidationError(f"Validation error: {str(e)}")
    return wrapper


def calculation_handler(func: Callable) -> Callable:
    """Decorator specifically for calculation functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ZeroDivisionError, ValueError, TypeError) as e:
            raise CalculationError(f"Calculation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in calculation: {e}")
            raise CalculationError(f"Calculation error: {str(e)}")
    return wrapper


def ui_handler(func: Callable) -> Callable:
    """Decorator specifically for UI functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"UI error in {func.__name__}: {e}")
            st.error(f"UI Error: Unable to display {func.__name__}")
            return None
    return wrapper


class ParameterValidator:
    """Utility class for parameter validation"""
    
    @staticmethod
    @validation_handler
    def validate_required_params(params: Dict[str, Any], required_keys: list) -> None:
        """Validate that required parameters are present"""
        missing = [key for key in required_keys if key not in params]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")
    
    @staticmethod
    @validation_handler
    def validate_numeric_range(value: Union[int, float], 
                             min_val: Union[int, float], 
                             max_val: Union[int, float],
                             param_name: str = "Parameter") -> None:
        """Validate that numeric value is within range"""
        if not isinstance(value, (int, float)):
            raise TypeError(f"{param_name} must be numeric")
        
        if value < min_val or value > max_val:
            raise ValueError(f"{param_name} must be between {min_val} and {max_val}")
    
    @staticmethod
    @validation_handler
    def validate_positive(value: Union[int, float], param_name: str = "Parameter") -> None:
        """Validate that value is positive"""
        if not isinstance(value, (int, float)):
            raise TypeError(f"{param_name} must be numeric")
        
        if value <= 0:
            raise ValueError(f"{param_name} must be positive")
    
    @staticmethod
    @validation_handler
    def validate_string_not_empty(value: str, param_name: str = "Parameter") -> None:
        """Validate that string is not empty"""
        if not isinstance(value, str):
            raise TypeError(f"{param_name} must be a string")
        
        if not value.strip():
            raise ValueError(f"{param_name} cannot be empty")
    
    @staticmethod
    @validation_handler
    def validate_list_not_empty(value: list, param_name: str = "Parameter") -> None:
        """Validate that list is not empty"""
        if not isinstance(value, list):
            raise TypeError(f"{param_name} must be a list")
        
        if not value:
            raise ValueError(f"{param_name} cannot be empty")


class SafeOperations:
    """Utility class for safe mathematical operations"""
    
    @staticmethod
    def safe_divide(numerator: Union[int, float], 
                   denominator: Union[int, float],
                   default: Union[int, float] = 0) -> Union[int, float]:
        """Safely divide with default value for zero division"""
        try:
            if denominator == 0:
                return default
            return numerator / denominator
        except (TypeError, ValueError):
            return default
    
    @staticmethod
    def safe_percentage(value: Union[int, float],
                       total: Union[int, float],
                       default: float = 0.0) -> float:
        """Safely calculate percentage with default for invalid inputs"""
        try:
            if total == 0:
                return default
            return (value / total) * 100
        except (TypeError, ValueError):
            return default
    
    @staticmethod
    def safe_log(value: Union[int, float],
                base: Union[int, float] = None,
                default: float = 0.0) -> float:
        """Safely calculate logarithm with default for invalid inputs"""
        try:
            import math
            if value <= 0:
                return default
            if base is None:
                return math.log(value)
            else:
                return math.log(value, base)
        except (TypeError, ValueError, ZeroDivisionError):
            return default


# Global error handler instance
error_handler_instance = ErrorHandler()