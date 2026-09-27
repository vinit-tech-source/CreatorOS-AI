import logging
import sys
from app.core.config import settings

def setup_logging():
    log_level = logging.INFO
    
    # Base configuration
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Remove existing handlers to prevent duplicates
    if logger.handlers:
        logger.handlers.clear()
        
    handler = logging.StreamHandler(sys.stdout)
    
    # Use JSON formatter in production, otherwise standard readable text
    if settings.ENVIRONMENT == "production":
        try:
            from pythonjsonlogger import jsonlogger
            formatter = jsonlogger.JsonFormatter(
                fmt="%(asctime)s %(name)s %(levelname)s %(message)s"
            )
            handler.setFormatter(formatter)
        except ImportError:
            # Fallback if package is missing
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        
    logger.addHandler(handler)
