# Mac and Windows version:
# 
# to stop creation of __pycache__ folder do this:
# PYTHONDONTWRITEBYTECODE=1 python -B Aidetour.py
# 
# 
# prep for PyPi:
# pip install --upgrade setuptools wheel
# python setup.py sdist bdist_wheel
# pip install twine
# twine upload dist/*
# 
# 
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
# conda activate Aidetour python=3.10.14
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
from aidetour_logging import setup_logger
import aidetour_api_handler
import aidetour_utilities
# an alias to 'config.' instead of 'aidetour_utilities.'
import aidetour_utilities as config 


def run_gui_version():
    logger.info(f"Starting {config.APP_NAME}...")
    aidetour_utilities.set_app_mode('gui')
    import aidetour_gui
    logger.info("GUI launched...")
    app = aidetour_gui.GuiStuff(False)
    app.MainLoop()

def run_cli_version():
    # for app usage in "terminal" (Mac/Linux) or "cmd" (Windows):
    aidetour_utilities.set_app_mode('cli')
    print(f"{config.APP_NAME}: CLI mode launched using settings in:\n{config.APP_SETTINGS_LOCATION}\nRunning local API server on: http://{config.HOST}:{config.PORT}\nSee logs in: {aidetour_utilities.get_log_dir()}")
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

    # FIXME 
    #   ask AI for a command line way to allow user to edit Settings
    parser = argparse.ArgumentParser(description=f"{config.APP_NAME} with Mac/Windows GUI or CLI terminal mode.")
    parser.add_argument('--cli', action='store_true', help=f"run {config.APP_NAME} in CLI mode (no GUI).")
    args = parser.parse_args()

    aidetour_utilities.load_settings()
    APP_MODE = "gui" # default

    from aidetour_logging import setup_logger
    app_log = aidetour_utilities.prepend_log_dir(config.APP_LOG)
    setup_logger(app_log)

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

