# -*- coding: utf-8 -*-
"""
Security Logger for Package Delivery System

Provides centralized security logging for API events such as login attempts,
registration, payments, and profile updates.

@author: laisz
"""
import logging
from platformdirs import user_log_dir
from os import makedirs
from os.path import join, exists

# Module-level logger instance
_security_logger = None


def get_security_logger() -> logging.Logger:
    """
    Get the security logger instance.
    
    Creates the logger on first call, reuses on subsequent calls.
    Logs are written to: <user_log_dir>/PackageSystem/security.log
    
    Returns
    -------
    logging.Logger
        Configured security logger instance.
    
    Example
    -------
    >>> from logger import get_security_logger
    >>> log = get_security_logger()
    >>> log.info("LOGIN_SUCCESS | email=test@example.com")
    """
    global _security_logger
    
    if _security_logger is None:
        _security_logger = logging.getLogger("SECURITY")
        _security_logger.setLevel(logging.INFO)
        
        # Avoid adding duplicate handlers
        if not _security_logger.handlers:
            # Create log directory
            log_dir = user_log_dir("PackageSystem", "SE_Project")
            makedirs(log_dir, exist_ok=True)
            
            # File handler
            log_file = join(log_dir, "security.log")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            
            _security_logger.addHandler(file_handler)
            
            # Also log to console for debugging
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)  # Only warnings+ to console
            console_handler.setFormatter(formatter)
            _security_logger.addHandler(console_handler)
    
    return _security_logger


def get_log_path() -> str:
    """
    Get the path to the security log file.
    
    Returns
    -------
    str
        Absolute path to the security.log file.
    """
    log_dir = user_log_dir("PackageSystem", "SE_Project")
    return join(log_dir, "security.log")


if __name__ == "__main__":
    # Demo usage
    log = get_security_logger()
    log.info("LOGIN_SUCCESS | email=demo@example.com")
    log.warning("LOGIN_FAILED | email=hacker@example.com")
    log.info("REGISTER | customer=C00001 | email=new@example.com")
    log.info("PAYMENT | customer=C00001 | bill=B000010001 | amount=250.0")
    
    print(f"Log file location: {get_log_path()}")
