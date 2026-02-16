"""
Professional logging system for the ETL pipeline
WHY: Production systems need traceability and debugging capability
"""
from loguru import logger
import sys
from pathlib import Path

def setup_logger(log_file: str = "logs/pipeline.log"):
    """
    Configure structured logging
    
    Features:
    - Console output (colored, readable)
    - File output (persistent, rotated)
    - Automatic rotation (no disk overflow)
    """
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Remove default handler
    logger.remove()
    
    # Console: colored, human-readable
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # File: complete, rotated, persistent
    logger.add(
        log_file,
        rotation="10 MB",      # Rotate when reaches 10MB
        retention="30 days",   # Keep logs for 30 days
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} | {message}",
        level="DEBUG"          # More verbose in file
    )
    
    return logger

# Global logger instance
log = setup_logger()
