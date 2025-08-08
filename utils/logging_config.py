"""
Logging configuration for the Options Pricing Calculator
"""
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import sys

from config.settings import LOGGING_CONFIG


class LoggingManager:
    """Manages application logging configuration"""
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self._configured = False
    
    def setup_logging(self, 
                     level: str = LOGGING_CONFIG['level'],
                     log_to_file: bool = True,
                     log_to_console: bool = True,
                     log_file: Optional[str] = None) -> None:
        """Setup logging configuration"""
        if self._configured:
            return
        
        # Create root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            LOGGING_CONFIG['format'],
            datefmt=LOGGING_CONFIG['date_format']
        )
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, level.upper()))
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # File handler
        if log_to_file:
            log_file_path = self.log_dir / (log_file or "options_calculator.log")
            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        # Set specific logger levels
        logging.getLogger('streamlit').setLevel(logging.WARNING)
        logging.getLogger('matplotlib').setLevel(logging.WARNING)
        logging.getLogger('PIL').setLevel(logging.WARNING)
        
        self._configured = True
        logging.info("Logging configuration completed")
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get logger instance for specific module"""
        return logging.getLogger(name)
    
    def set_debug_mode(self, debug: bool = True) -> None:
        """Enable or disable debug mode"""
        level = logging.DEBUG if debug else logging.INFO
        logging.getLogger().setLevel(level)
        
        for handler in logging.getLogger().handlers:
            handler.setLevel(level)
        
        if debug:
            logging.info("Debug mode enabled")
        else:
            logging.info("Debug mode disabled")


class ContextualLogger:
    """Logger that includes contextual information"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context = {}
    
    def set_context(self, **kwargs) -> None:
        """Set context variables for logging"""
        self.context.update(kwargs)
    
    def clear_context(self) -> None:
        """Clear context variables"""
        self.context.clear()
    
    def _format_message(self, message: str) -> str:
        """Format message with context"""
        if not self.context:
            return message
        
        context_str = " | ".join(f"{k}={v}" for k, v in self.context.items())
        return f"{message} [{context_str}]"
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context"""
        self.set_context(**kwargs)
        self.logger.debug(self._format_message(message))
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with context"""
        self.set_context(**kwargs)
        self.logger.info(self._format_message(message))
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context"""
        self.set_context(**kwargs)
        self.logger.warning(self._format_message(message))
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with context"""
        self.set_context(**kwargs)
        self.logger.error(self._format_message(message))
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with context"""
        self.set_context(**kwargs)
        self.logger.critical(self._format_message(message))


# Global logging manager instance
logging_manager = LoggingManager()

# Initialize logging on import
logging_manager.setup_logging()


def get_logger(name: str) -> logging.Logger:
    """Get standard logger instance"""
    return logging.getLogger(name)


def get_contextual_logger(name: str) -> ContextualLogger:
    """Get contextual logger instance"""
    return ContextualLogger(name)