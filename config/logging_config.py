import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(level=logging.DEBUG):
    """
    Set up the logging configuration for the application.
    """
    logger = logging.getLogger()
    logger.setLevel(level)

    # Create handlers
    stdout_handler = logging.StreamHandler(sys.stdout)
    file_handler = RotatingFileHandler('app.log', maxBytes=1024*1024*5, backupCount=5)

    # Create formatters and add it to handlers
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stdout_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)
