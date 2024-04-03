# aidetour_logging

import os
import logging
import aidetour_utilities

def configure_logging(log_file_path):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create a file handler that logs even debug messages and overwrites the log file on each run
    fh = logging.FileHandler(log_file_path, mode='w')  # Set filemode to 'w' to overwrite
    fh.setLevel(logging.INFO)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    fh.setFormatter(formatter)
    
    # Remove all handlers associated with the root logger to prevent duplication
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])
    
    # Add the handlers to the logger
    logger.addHandler(fh)

    # Add a NullHandler to prevent logging to the console
    logger.addHandler(logging.NullHandler())

def ensure_log_directory_exists():
    # This will correctly resolve the home directory on both Unix and Windows
    # log_dir = os.path.join(os.path.expanduser('~'), '.Aidetour', 'logs')
    # os.makedirs(log_dir, exist_ok=True)  # Creates the directory if it does not exist
    log_dir = os.getcwd()
    return log_dir

def setup_logging():
    aidetour_utilities.executable_dir()  # Ensure this is needed or remove if not necessary
    log_dir = ensure_log_directory_exists()
    log_file_path = os.path.join(log_dir, 'Aidetour.log')
    configure_logging(log_file_path)

def get_logger(name):
    return logging.getLogger(name)
