import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    log_dir = "logs" # variable that holds the name of the directory the log files will be stored
    os.makedirs(log_dir, exist_ok=True) # this creates the directoryif it does not exist
    
    #  Create a logger instance
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)

     #  Define the log file name and rotation parameters
    log_file = os.path.join(log_dir, "app.log")
    max_bytes = 5 * 1024 * 1024
    backup_count = 3

    #  Create the RotatingFileHandler
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )

    #  Create a console handler and set its level/formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Attach formatter and level to file handler
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    
    # Add the handler to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

        