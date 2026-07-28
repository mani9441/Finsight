import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Formatter with timestamp, level, source path, line number, and message
LOG_FORMAT = "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

def setup_logging():
    """
    Sets up the global logging configuration.
    Registers a rotating file handler and a standard output stream handler.
    """
    from config.settings import settings

    # Ensure logs folder exists
    log_dir = Path(settings.LOG_FILE_PATH).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Determine numeric log level
    numeric_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    
    # Avoid duplicate handlers if setup_logging is called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.setLevel(numeric_level)

    # 1. Console stream handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    console_handler.setLevel(numeric_level)
    root_logger.addHandler(console_handler)

    # 2. Rotating File handler (limit size to 5MB, keep 3 backups)
    try:
        file_handler = RotatingFileHandler(
            filename=settings.LOG_FILE_PATH,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        file_handler.setLevel(numeric_level)
        root_logger.addHandler(file_handler)
    except Exception as e:
        # Fallback if log directory is write-protected
        print(f"Warning: Failed to setup rotating file logger: {e}", file=sys.stderr)

    # Log application startup details
    logging.info(f"Logging system initialized successfully. Log Level: {settings.LOG_LEVEL}")
    logging.info(f"Log files are stored at: {settings.LOG_FILE_PATH.resolve()}")
    logging.info(f"Application environment: {settings.APP_ENV} (Debug={settings.DEBUG})")


def get_logger(name: str) -> logging.Logger:
    """
    Returns a custom logger with the specified module name.
    """
    return logging.getLogger(name)

