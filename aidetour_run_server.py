import sys
from loguru import logger
from aidetour_api_handler import run_flask_app

# Aidetour modules:
import aidetour_utilities
import aidetour_logging
from aidetour_logging import setup_logger

setup_logger('Server.log')

if __name__ == '__main__':
    logger.info("aidetour_run_server.py")

    run_flask_app()
