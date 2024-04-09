# Mac and Windows version:
# 
# python --version == Python 3.10
# pip --version
# pip 24.0 from /opt/miniconda3/envs/Aidetour/lib/python3.10/site-packages/pip (python 3.10)
# 
# Aidetour is an application that acts as a middleman between the OpenAI API and 
# the Anthropic Claude API. When Aidetour receives a request intended for the 
# OpenAI system, it translates that request into a proper Anthropic API request.
# That translated request is sent to Anthropic API then waits for a response. 
# Once the response is received, Aidetour converts that back into an OpenAI API
# formatted streamed response.
# 
# cls: attempts at building a distribution binary:
# 
# Py2app failed!!!
# 
# PyInstaller works great, so:
# pip install pyinstaller
# pyinstaller --onefile Aidetour.py
# pyinstaller Aidetour.spec
#
# Mac:
# cd Aidetour
# conda activate Aidetour
# python Aidetour.py
# 
# Windows:
# cd Aidetour
# python -m venv Aidetour
# Aidetour\Scripts\activate
# python Aidetour.py

# pip install python-dotenv
# pip install rumps
# pip install wxPython
# pip install requests
# pip install Flask Flask-CORS
# pip install anthropic

import os
import sys
import subprocess
import logging
import signal
import argparse
import time
import uuid
# pip install loguru
from loguru import logger
# import logging
import json
import configparser
import subprocess
import threading
from datetime import datetime, timezone
# pip install python-dotenv
from dotenv import load_dotenv

# Aidetour modules:
import aidetour_logging
import aidetour_api_handler
import aidetour_utilities
from aidetour_utilities import APP_NAME, APP_LOGO
from aidetour_utilities import HOST, PORT, ANTHROPIC_API_KEY


def check_api_key():
    # required to assign a new value to global value:
    # global ANTHROPIC_API_KEY
    # Load environment variables from .env file, assumed to be same folder as app:
    load_dotenv()
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    # Check if the API key is missing or empty
    if ANTHROPIC_API_KEY is None or ANTHROPIC_API_KEY.strip() == '':
        error_message = "ERROR\n\n"
        error_message += "The ANTHROPIC_API_KEY is missing or empty, "
        error_message += "please open and edit the .env file here:\n\n"
        error_message += f"{aidetour_utilities.executable_dir()}/.env\n\n"
        error_message += "then add or set the ANTHROPIC_API_KEY= to your actual Anthropic API key, then run this app again.\n\n"
        error_message += "More details are provided in the README file for this app."
        logger.error(error_message)
        aidetour_utilities.show_custom_message(APP_NAME, error_message)
        sys.exit(1) 

    # Check if the API key is the placeholder value
    if ANTHROPIC_API_KEY == 'your_api_key_here':
        error_message = "ERROR\n\n"
        error_message += "Please change the placeholder API key in the .env file with your actual Anthropic API key.\n\n"
        error_message += "Open and edit the .env file, replace the 'your_api_key_here' with your Anthropic API key, then run this app again.\n\n"
        error_message += f"{aidetour_utilities.executable_dir()}/.env\n\n"
        error_message += "More details are provided in the README file for this app."
        logger.error(error_message)
        aidetour_utilities.show_custom_message(APP_NAME, error_message)
        sys.exit(1) 

    return ANTHROPIC_API_KEY


def run_windows_version():
    import aidetour_gui_windows
    from aidetour_utilities import APP_NAME, APP_LOGO
    from aidetour_utilities import HOST, PORT, ANTHROPIC_API_KEY
    logging.info("Windows detected...")
    app = aidetour_gui_windows.Aidetour(HOST, PORT, ANTHROPIC_API_KEY)
    app.MainLoop()

def run_mac_version():
    run_windows_version()
    # import aidetour_gui_mac
    # from aidetour_utilities import APP_NAME, APP_LOGO
    # from aidetour_utilities import HOST, PORT, ANTHROPIC_API_KEY
    # logging.info("Mac detected...")
    # print("run_mac_version=", APP_NAME, APP_LOGO, HOST, PORT, ANTHROPIC_API_KEY)
    # app = aidetour_gui_mac.Aidetour(HOST, PORT, ANTHROPIC_API_KEY)
    # app.run()

def run_cli_version():
    from aidetour_utilities import APP_NAME, APP_LOGO
    from aidetour_utilities import HOST, PORT, ANTHROPIC_API_KEY
    logging.info(f"Starting {APP_NAME} in CLI mode...")
    print("run_cli_version=", APP_NAME, APP_LOGO, HOST, PORT, ANTHROPIC_API_KEY)
    aidetour_api_handler.run_flask_app(HOST, PORT, ANTHROPIC_API_KEY)

def ensure_config_directory():
    home_dir = os.path.expanduser('~')
    config_dir = os.path.join(home_dir, APP_NAME)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return config_dir

def signal_handler(sig, frame):
    print("\nKeyboard interrupt received. Shutting down...")
    logger.info("Keyboard interrupt received. Shutting down...")
    print("Shutdown completed. Exiting.")
    logger.info("Shutdown completed. Exiting.")
    sys.exit(0)

if __name__ == '__main__':
    # Register the signal handler for SIGINT = Ctrl-C
    signal.signal(signal.SIGINT, signal_handler)

    from aidetour_logging import setup_logger
    setup_logger('Aidetour.log')

    # lots and lots of user hand holding...
    parser = argparse.ArgumentParser(description=f"{APP_NAME} with Mac/Windows GUI or CLI terminal mode.")
    parser.add_argument('--cli', action='store_true', help=f"run {APP_NAME} in CLI mode (no GUI).")
    args = parser.parse_args()

    # aidetour_logging.setup_logging()
    # logger = aidetour_logging.get_logger(__name__)
    logger.info(f"Starting {APP_NAME}...")

    config_dir = ensure_config_directory()

    config_files_ok = aidetour_utilities.check_create_config_files()
    if not config_files_ok:
        logger.error("Configuration files were created or updated. Please change and review them before running Aidetour again.")
        print("Configuration files were created or updated. Please change and review them before running Aidetour again.")
        sys.exit(1)

    aidetour_utilities.HOST, aidetour_utilities.PORT = aidetour_utilities.read_config_ini()

    aidetour_utilities.ANTHROPIC_API_KEY = check_api_key()

    models = aidetour_utilities.list_models()
    logger.info(models)

    if args.cli:
        run_cli_version()
    elif sys.platform.startswith('darwin'):
        aidetour_utilities.show_splash_screen()
        run_mac_version()
    elif sys.platform.startswith('win'):
        aidetour_utilities.show_splash_screen()
        run_windows_version()
    else:
        logger.info("GUI mode is only supported on Windows and macOS, so now running in CLI mode...")
        run_cli_version()

