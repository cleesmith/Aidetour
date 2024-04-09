import sys
# pip install loguru
from loguru import logger
# import logging
from aidetour_api_handler import run_flask_app

# Aidetour modules:
import aidetour_utilities
import aidetour_logging


# logger = logging.getLogger('run_server')

from aidetour_logging import setup_logger
setup_logger('Server.log')


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5600
    api_key = sys.argv[3] if len(sys.argv) > 3 else 'your_api_key'

    logger.info("run_server.py: {} {}", host, port)

    run_flask_app(host, port, api_key)
