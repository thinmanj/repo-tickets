#!/usr/bin/env python3
"""
Structured logging system for repo-tickets.

Provides JSON-formatted logs with context for analysis and debugging.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings for structured logging.
    
    Makes logs easily parseable by log aggregation tools like
    ELK, Splunk, or custom analytics systems.
    """
    
    def __init__(self, include_context: bool = True):
        """
        Initialize JSON formatter.
        
        Args:
            include_context: Include context fields (ticket_id, agent_id, etc.)
        """
        super().__init__()
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add context fields if present
        if self.include_context:
            for key in ['ticket_id', 'agent_id', 'epic_id', 'user', 'operation', 'duration_ms']:
                if hasattr(record, key):
                    log_data[key] = getattr(record, key)
        
        # Add any extra fields
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, default=str)


class StructuredLogger:
    """
    Structured logger with context support.
    
    Provides methods for logging operations with automatic context fields.
    """
    
    def __init__(
        self,
        name: str,
        level: int = logging.INFO,
        log_file: Optional[Path] = None,
        json_format: bool = True
    ):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name (usually module name).
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            log_file: Optional file path for logging.
            json_format: Use JSON formatting (True) or human-readable (False).
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        if json_format:
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            )
        
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(JSONFormatter())
            self.logger.addHandler(file_handler)
    
    def _log_with_context(
        self,
        level: int,
        message: str,
        **context: Any
    ) -> None:
        """Log message with context fields."""
        extra = {}
        for key, value in context.items():
            extra[key] = value
        
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **context: Any) -> None:
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, message, **context)
    
    def info(self, message: str, **context: Any) -> None:
        """Log info message with context."""
        self._log_with_context(logging.INFO, message, **context)
    
    def warning(self, message: str, **context: Any) -> None:
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, message, **context)
    
    def error(self, message: str, **context: Any) -> None:
        """Log error message with context."""
        self._log_with_context(logging.ERROR, message, **context)
    
    def critical(self, message: str, **context: Any) -> None:
        """Log critical message with context."""
        self._log_with_context(logging.CRITICAL, message, **context)
    
    # Convenience methods for common operations
    
    def log_ticket_operation(
        self,
        operation: str,
        ticket_id: str,
        **kwargs: Any
    ) -> None:
        """Log a ticket operation."""
        self.info(
            f"Ticket operation: {operation}",
            ticket_id=ticket_id,
            operation=operation,
            **kwargs
        )
    
    def log_agent_operation(
        self,
        operation: str,
        agent_id: str,
        **kwargs: Any
    ) -> None:
        """Log an agent operation."""
        self.info(
            f"Agent operation: {operation}",
            agent_id=agent_id,
            operation=operation,
            **kwargs
        )
    
    def log_performance(
        self,
        operation: str,
        duration_ms: float,
        **kwargs: Any
    ) -> None:
        """Log performance metrics."""
        self.info(
            f"Performance: {operation}",
            operation=operation,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_error_with_ticket(
        self,
        message: str,
        ticket_id: str,
        error: Optional[Exception] = None,
        **kwargs: Any
    ) -> None:
        """Log error with ticket context."""
        if error:
            self.error(
                message,
                ticket_id=ticket_id,
                error_type=type(error).__name__,
                error_message=str(error),
                **kwargs
            )
        else:
            self.error(message, ticket_id=ticket_id, **kwargs)


class PerformanceLogger:
    """Context manager for logging operation performance."""
    
    def __init__(
        self,
        logger: StructuredLogger,
        operation: str,
        **context: Any
    ):
        """
        Initialize performance logger.
        
        Args:
            logger: StructuredLogger instance.
            operation: Name of operation being measured.
            context: Additional context fields.
        """
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        """Start timing."""
        import time
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Log performance."""
        import time
        duration_ms = (time.time() - self.start_time) * 1000
        
        if exc_type:
            self.logger.error(
                f"Operation failed: {self.operation}",
                operation=self.operation,
                duration_ms=duration_ms,
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                **self.context
            )
        else:
            self.logger.log_performance(
                self.operation,
                duration_ms,
                **self.context
            )


# Global logger instance
_global_logger: Optional[StructuredLogger] = None


def get_logger(
    name: str = "repo_tickets",
    level: int = logging.INFO,
    log_file: Optional[Path] = None
) -> StructuredLogger:
    """
    Get or create a structured logger.
    
    Args:
        name: Logger name.
        level: Logging level.
        log_file: Optional log file path.
        
    Returns:
        StructuredLogger instance.
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = StructuredLogger(name, level, log_file)
    return _global_logger


def set_log_level(level: int) -> None:
    """Set global log level."""
    if _global_logger:
        _global_logger.logger.setLevel(level)


def configure_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    json_format: bool = True
) -> StructuredLogger:
    """
    Configure global logging.
    
    Args:
        level: Logging level.
        log_file: Optional log file path.
        json_format: Use JSON formatting.
        
    Returns:
        Configured StructuredLogger.
    """
    global _global_logger
    _global_logger = StructuredLogger(
        "repo_tickets",
        level=level,
        log_file=log_file,
        json_format=json_format
    )
    return _global_logger


# Convenience function for performance logging
def log_performance(operation: str, **context: Any):
    """
    Context manager for performance logging.
    
    Usage:
        with log_performance("load_ticket", ticket_id="TICKET-1"):
            ticket = storage.load_ticket("TICKET-1")
    """
    logger = get_logger()
    return PerformanceLogger(logger, operation, **context)
