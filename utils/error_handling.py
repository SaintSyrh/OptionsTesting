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


# Additional validation utilities for the refactored architecture

def validate_option_parameters(S: float, K: float, T: float, r: float, sigma: float) -> Dict[str, float]:
    """
    Validate Black-Scholes option parameters
    
    Args:
        S: Spot price
        K: Strike price  
        T: Time to expiration
        r: Risk-free rate
        sigma: Volatility
    
    Returns:
        Dictionary of validated parameters
    
    Raises:
        ValidationError: If any parameter is invalid
    """
    try:
        ParameterValidator.validate_positive(S, "Spot price (S)")
        ParameterValidator.validate_positive(K, "Strike price (K)")
        ParameterValidator.validate_positive(T, "Time to expiration (T)")
        
        if r < -0.1 or r > 1.0:  # Reasonable bounds for interest rates
            raise ValueError(f"Risk-free rate seems unrealistic: {r}")
        
        ParameterValidator.validate_positive(sigma, "Volatility (σ)")
        if sigma > 10.0:  # 1000% volatility seems unrealistic
            raise ValueError(f"Volatility seems too high: {sigma}")
        
        return {'S': S, 'K': K, 'T': T, 'r': r, 'sigma': sigma}
    except Exception as e:
        raise ValidationError(f"Invalid option parameters: {str(e)}")


def validate_percentage_input(value: Union[int, float], field_name: str, allow_negative: bool = False) -> float:
    """
    Validate percentage input and convert to decimal
    
    Args:
        value: Input value as percentage (e.g., 10 for 10%)
        field_name: Name of field for error messages  
        allow_negative: Whether negative values are allowed
    
    Returns:
        Value as decimal (e.g., 0.1 for 10%)
    """
    try:
        float_value = float(value)
        if not allow_negative and float_value < 0:
            raise ValidationError(f"{field_name} cannot be negative, got {float_value}%")
        if float_value > 1000:  # Reasonable upper bound
            raise ValidationError(f"{field_name} seems too large, got {float_value}%")
        return float_value / 100.0
    except (ValueError, TypeError):
        raise ValidationError(f"{field_name} must be a valid number, got {value}")


class EntityDataValidator:
    """Specialized validator for entity data"""
    
    @staticmethod
    def validate_entity(data: Dict[str, Any]) -> Dict[str, str]:
        """Validate entity data and return validation errors"""
        errors = {}
        
        # Validate name
        name = data.get('name', '').strip()
        if not name:
            errors['name'] = "Entity name is required"
        elif len(name) > 100:
            errors['name'] = "Entity name must be less than 100 characters"
        
        # Validate loan duration
        try:
            loan_duration = int(data.get('loan_duration', 0))
            if loan_duration <= 0:
                errors['loan_duration'] = "Loan duration must be positive"
            elif loan_duration > 1200:  # 100 years seems like a reasonable max
                errors['loan_duration'] = "Loan duration seems unreasonably long"
        except (ValueError, TypeError):
            errors['loan_duration'] = "Loan duration must be a valid number"
        
        return errors


class OptionDataValidator:
    """Specialized validator for option contract data"""
    
    @staticmethod
    def validate_option(data: Dict[str, Any]) -> Dict[str, str]:
        """Validate option contract data and return validation errors"""
        errors = {}
        
        # Validate option type
        if data.get('option_type') not in ['call', 'put']:
            errors['option_type'] = "Option type must be 'call' or 'put'"
        
        # Validate strike price
        try:
            strike_price = float(data.get('strike_price', 0))
            if strike_price <= 0:
                errors['strike_price'] = "Strike price must be positive"
        except (ValueError, TypeError):
            errors['strike_price'] = "Strike price must be a valid number"
        
        # Validate token share percentage
        try:
            token_share = float(data.get('token_share_pct', 0))
            if token_share <= 0 or token_share > 100:
                errors['token_share_pct'] = "Token share must be between 0 and 100"
        except (ValueError, TypeError):
            errors['token_share_pct'] = "Token share must be a valid number"
        
        # Validate time to expiration
        try:
            time_to_exp = float(data.get('time_to_expiration', 0))
            if time_to_exp <= 0:
                errors['time_to_expiration'] = "Time to expiration must be positive"
        except (ValueError, TypeError):
            errors['time_to_expiration'] = "Time to expiration must be a valid number"
        
        return errors


class DepthDataValidator:
    """Specialized validator for market depth data"""
    
    @staticmethod
    def validate_depth(data: Dict[str, Any]) -> Dict[str, str]:
        """Validate market depth data and return validation errors"""
        errors = {}
        
        # Validate entity
        if not data.get('entity', '').strip():
            errors['entity'] = "Entity is required"
        
        # Validate exchange
        if not data.get('exchange', '').strip():
            errors['exchange'] = "Exchange is required"
        
        # Validate numeric fields
        numeric_fields = {
            'spread': 'Bid-ask spread',
            'depth_50': 'Depth at 50bps',
            'depth_100': 'Depth at 100bps', 
            'depth_200': 'Depth at 200bps'
        }
        
        for field, display_name in numeric_fields.items():
            try:
                value = float(data.get(field, 0))
                if value < 0:
                    errors[field] = f"{display_name} cannot be negative"
            except (ValueError, TypeError):
                errors[field] = f"{display_name} must be a valid number"
        
        return errors


def display_validation_results(validation_errors: Dict[str, str]) -> bool:
    """
    Display validation errors to user and return whether validation passed
    
    Args:
        validation_errors: Dictionary of field -> error message
    
    Returns:
        True if validation passed (no errors), False otherwise
    """
    if validation_errors:
        st.error("Please fix the following validation errors:")
        for field, error in validation_errors.items():
            st.write(f"• **{field.replace('_', ' ').title()}**: {error}")
        return False
    return True


def with_error_boundary(title: str = "Error Boundary"):
    """
    Decorator that creates an error boundary around Streamlit components
    
    Args:
        title: Title to display in error message
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                st.error(f"Error in {title}: {str(e)}")
                st.write("Please refresh the page or contact support if this error persists.")
                logger.error(f"Error boundary caught exception in {title}: {e}")
                logger.debug(f"Full traceback: {traceback.format_exc()}")
                return None
        return wrapper
    return decorator


# Global error handler instance
error_handler_instance = ErrorHandler()