"""
Logging utility for the system
"""
import logging
from rich.logging import RichHandler
from pathlib import Path
import sys
import os

# ---------------------------
# Windows CMD UTF-8 Fix
# ---------------------------
if os.name == 'nt':
    # Change code page to UTF-8
    os.system('chcp 65001')
    # Reconfigure stdout to UTF-8
    sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------
# Logger setup
# ---------------------------
def setup_logger(name: str = "tradl", level: str = "INFO") -> logging.Logger:
    """Setup logger with rich formatting"""
    
    # Create logs directory if not exists
    Path("logs").mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler with rich formatting
    console_handler = RichHandler(rich_tracebacks=True, show_time=True)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_format)
    
    # File handler
    file_handler = logging.FileHandler("logs/tradl.log", encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# ---------------------------
# Global logger instance
# ---------------------------
logger = setup_logger()
