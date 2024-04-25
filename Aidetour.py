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

# pip install pipreqs
# pipreqs --force

# pip install wxPython
# pip install requests
# pip install Flask Flask-CORS
# pip install anthropic

import os
import sys
import platform
import subprocess
import logging
import signal
import argparse
import time
import uuid
from loguru import logger
import json
import configparser
import subprocess
import threading
from datetime import datetime, timezone

# Aidetour modules:
import aidetour_logging
import aidetour_api_handler
import aidetour_utilities
# an alias to 'config.' instead of 'aidetour_utilities.'
import aidetour_utilities as config 


def check_api_key():
    # check if the API key is missing or empty
    if config.ANTHROPIC_API_KEY is None or config.ANTHROPIC_API_KEY.strip() == '':
        error_message = "ERROR\n\n"
        error_message += "The ANTHROPIC_API_KEY is missing or empty!"
        error_message += "More details are provided in the README file for this app."
        logger.error(error_message)
        aidetour_utilities.show_custom_message(config.APP_NAME, error_message)
        # sys.exit(1) 

    # check if the API key is the placeholder value
    if config.ANTHROPIC_API_KEY == 'your_api_key_here':
        error_message = "ERROR\n\n"
        error_message += "Please replace the 'your_api_key_here' with your Anthropic API key, then run this app again.\n\n"
        error_message += "More details are provided in the README file for this app."
        logger.error(error_message)
        aidetour_utilities.show_custom_message(config.APP_NAME, error_message)
        # sys.exit(1) 

def run_gui_version():
    aidetour_utilities.set_app_mode('gui')
    import aidetour_gui
    logger.info("GUI launched...")
    app = aidetour_gui.GuiStuff(False)
    app.MainLoop()

def run_cli_version():
    # for app usage in terminal (Mac/Linux) or cmd (Windows):
    aidetour_utilities.set_app_mode('cli')
    logger.info(f"{config.APP_NAME}: CLI mode launched using settings in: {config.APP_SETTINGS_LOCATION}to run API server on: http://{config.HOST}:{config.PORT}")
    print(f"{config.APP_NAME}: CLI mode launched using settings in:\n{config.APP_SETTINGS_LOCATION}\nto run API server on: http://{config.HOST}:{config.PORT}")
    aidetour_api_handler.run_flask_app(True)

def signal_handler(sig, frame):
    print("\nKeyboard interrupt received. Shutting down...")
    logger.info("Keyboard interrupt received. Shutting down...")
    print("Shutdown completed. Exiting.")
    logger.info("Shutdown completed. Exiting.")
    sys.exit(0)

if __name__ == '__main__':
    # register the signal handler for SIGINT = Ctrl-C
    signal.signal(signal.SIGINT, signal_handler)

    from aidetour_logging import setup_logger
    setup_logger(config.APP_LOG)
    logger.info(f"Starting {config.APP_NAME}...")

    # FIXME 
    #   ask AI for a command line way to allow user to edit Settings
    parser = argparse.ArgumentParser(description=f"{config.APP_NAME} with Mac/Windows GUI or CLI terminal mode.")
    parser.add_argument('--cli', action='store_true', help=f"run {config.APP_NAME} in CLI mode (no GUI).")
    args = parser.parse_args()

    aidetour_utilities.load_settings()
    APP_MODE = "gui" # default

    # is this needed since Anthropic yields 401 (400's) for bad keys:
    # check_api_key()

    if args.cli:
        run_cli_version()
    elif sys.platform.startswith('darwin'):
        aidetour_utilities.show_splash_screen()
        run_gui_version()
    elif sys.platform.startswith('win'):
        aidetour_utilities.show_splash_screen()
        run_gui_version()
    else:
        logger.info("GUI mode is only supported on Windows and macOS, so now running in CLI mode...")
        run_cli_version()

