import sys
import time
from datetime import datetime
from loguru import logger
from aidetour_api_handler import run_flask_app

# Aidetour modules:
import aidetour_logging
from aidetour_logging import setup_logger
import aidetour_utilities
# an alias to 'config.' instead of 'aidetour_utilities.'
import aidetour_utilities as config 

from aidetour_logging import setup_logger
app_log = aidetour_utilities.prepend_log_dir(config.APP_LOG)
setup_logger(app_log)


if __name__ == '__main__':
    logger.info(f"{config.RUN_SERVER}: attempting to run flask app.")

    run_flask_app()  # see: aidetour_api_handler
