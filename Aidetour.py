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
# pyinstaller --onefile --windowed Aidetour.py
# pyinstaller Aidetour.spec
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
import logging
import json
import configparser
import subprocess
import threading
from datetime import datetime, timezone
# pip install python-dotenv
from dotenv import load_dotenv

# Aidetour modules:
import aidetour_logging
import aidetour_utilities
import aidetour_api_handler


APP_NAME = "Aidetour"
ANTHROPIC_API_KEY = None # uppercase to indicate it's an environment variable
HOST = None
PORT = None

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
    logging.info("Windows detected...")
    app = aidetour_gui_windows.Aidetour(HOST, PORT, ANTHROPIC_API_KEY)
    app.MainLoop()

def run_mac_version():
    import aidetour_gui_mac
    logging.info("Mac detected...")
    app = aidetour_gui_mac.Aidetour(HOST, PORT, ANTHROPIC_API_KEY)
    app.run()

def run_cli_version():
    logging.info("Starting Aidetour in CLI mode...")
    aidetour_api_handler.run_flask_app(HOST, PORT, ANTHROPIC_API_KEY)

def signal_handler(sig, frame):
    print("\nKeyboard interrupt received. Shutting down...")
    logger.info("Keyboard interrupt received. Shutting down...")
    print("Shutdown completed. Exiting.")
    logger.info("Shutdown completed. Exiting.")
    sys.exit(0)

if __name__ == '__main__':
    # Register the signal handler for SIGINT = Ctrl-C
    signal.signal(signal.SIGINT, signal_handler)

    # lots and lots of user hand holding...
    parser = argparse.ArgumentParser(description="Aidetour with Mac/Windows GUI or CLI terminal mode.")
    parser.add_argument('--cli', action='store_true', help='run Aidetour in CLI mode (no GUI).')
    args = parser.parse_args()

    aidetour_logging.setup_logging()
    logger = aidetour_logging.get_logger(__name__)
    logger.info("Starting Aidetour...")

    config_files_ok = aidetour_utilities.check_create_config_files()
    if not config_files_ok:
        logger.error("Configuration files were created or updated. Please change and review them before running Aidetour again.")
        print("Configuration files were created or updated. Please change and review them before running Aidetour again.")
        sys.exit(1)

    HOST, PORT = aidetour_utilities.read_config_ini()

    ANTHROPIC_API_KEY = check_api_key()

    models = aidetour_utilities.list_models()
    logger.info(models)

    if args.cli:
        run_cli_version()
    elif sys.platform.startswith('darwin'):
        run_mac_version()
    elif sys.platform.startswith('win'):
        run_windows_version()
    else:
        logger.info("GUI mode is only supported on Windows and macOS, so now running in CLI mode...")
        run_cli_version()

