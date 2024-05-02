# aidetour_utilities.py

import os
import socket
import sys
import platform
import time
from datetime import datetime, timezone
import re
import json
import textwrap
import configparser
import subprocess
from loguru import logger

# Aidetour modules:
import aidetour_logging
from aidetour_logging import setup_logger


APP_NAME = "Aidetour"
APP_MODE = "gui" # or "cli"
APP_LOGO = "Aidetour.png"
APP_SPLASH = 'aidetour_splash_wx.py'
APP_LOG = "Log_aidetour.txt"
SERVER_LOG = "Server_log_aidetour.txt"
CHAT_LOG = None
RUN_SERVER = 'aidetour_run_server.py'
APP_SETTINGS_LOCATION = None
HOST = None
PORT = None
ANTHROPIC_API_KEY = None
ANTHROPIC_API_MODELS = None
DEFAULT_MODEL = "claude-3-haiku-20240307"
ANTHROPIC_MESSAGES_API_URL = 'https://api.anthropic.com/v1/messages'


# def get_log_dir():
#     # Get the user's home directory
#     home_dir = os.path.expanduser("~")
#     # Define the log directory name
#     log_dir = os.path.join(home_dir, "aidetour_logs")
    
#     try:
#         # Try to create the 'aidetour_logs' directory if it doesn't exist
#         if not os.path.exists(log_dir):
#             os.makedirs(log_dir)
#         return log_dir
#     except Exception as e:
#         print(f"Warning: Unable to create directory '{log_dir}'. Reason: {e}")
#         print(f"Logs will be written directly to the user's home directory '{home_dir}' instead.")
#         return home_dir

# # Usage
# log_directory = get_log_dir()
# print(f"Log files will be saved in: {log_directory}")


def prepend_home_dir(filename):
    users_home = os.path.expanduser('~') # while different, this works for all
    return os.path.join(users_home, filename)

def set_chat_log():
    global CHAT_LOG
    # milliseconds since the Unix Epoch
    timestamp_milliseconds = int(time.time() * 1000)
    current_datetime = datetime.now()
    chat_log_name = f"{timestamp_milliseconds}_{APP_NAME}_Chat_log_{current_datetime.strftime('%Y_%m_%d')}_{current_datetime.strftime('%H%M%S')}.txt"
    # users_home = os.path.expanduser('~') # while different, this works for all platforms
    # CHAT_LOG = os.path.join(users_home, chat_log_name)
    CHAT_LOG = prepend_home_dir(chat_log_name)
    logger.info(f"aidetour_utilities: set_chat_log(): CHAT_LOG={CHAT_LOG}")
    if not os.path.exists(CHAT_LOG):
        with open(CHAT_LOG, 'a+') as file:
            file.write(f"Chat Log created at {current_datetime.strftime('%Y-%m-%d %H:%M:%S')} and named:\n{CHAT_LOG}\n{'_' * 70}")
            logger.info(f"aidetour_utilities: set_chat_log(): Chat Log Created:\n{CHAT_LOG}\n")

def set_app_mode(mode):
    global APP_MODE
    APP_MODE = mode

def set_port_usable(port):
    try:
        port = int(port)
    except ValueError:
        port = 5600 # just use a default for wonky user entries
    return port

def log_app_settings(logger):
    logger.info(f"APP_NAME: {APP_NAME}")
    logger.info(f"APP_MODE: {APP_MODE}")
    logger.info(f"APP_LOGO: {APP_LOGO}")
    logger.info(f"APP_SPLASH: {APP_SPLASH}")
    logger.info(f"APP_SETTINGS_LOCATION: {APP_SETTINGS_LOCATION}")
    logger.info(f"APP_LOG: {APP_LOG}")
    logger.info(f"SERVER_LOG: {SERVER_LOG}")
    logger.info(f"CHAT_LOG: {CHAT_LOG}")
    logger.info(f"RUN_SERVER: {RUN_SERVER}")
    logger.info(f"HOST: {HOST}")
    logger.info(f"PORT: {PORT}")
    # don't show user's api key in log files:
    logger.info(f"ANTHROPIC_API_KEY: [redacted]")
    logger.info(f"ANTHROPIC_API_MODELS: {ANTHROPIC_API_MODELS}")
    logger.info(f"ANTHROPIC_MESSAGES_API_URL: {ANTHROPIC_MESSAGES_API_URL}")
    logger.info(f"DEFAULT_MODEL: {DEFAULT_MODEL}")

def set_app_settings_location():
    global APP_SETTINGS_LOCATION
    # define the user's home directory for each platform:
    # if platform.system() == 'Windows':
    #     APP_SETTINGS_LOCATION = os.path.expanduser('~')
    # elif platform.system() == 'Darwin':  # macOS
    #     APP_SETTINGS_LOCATION = os.path.expanduser('~/Documents/Aidetour')
    # else:  # Linux
    #     APP_SETTINGS_LOCATION = os.path.expanduser('~/.config')

    settings_db_name = f"{APP_NAME}_Settings.json"
    # users_home = os.path.expanduser('~') # while different, this works for all
    # settings_location = os.path.join(users_home, settings_db_name)
    settings_location = prepend_home_dir(settings_db_name)
    APP_SETTINGS_LOCATION = settings_location
    logger.info(f"set_app_settings_location: APP_SETTINGS_LOCATION: {APP_SETTINGS_LOCATION}")
    return APP_SETTINGS_LOCATION

def create_default_settings_db():
    default_settings = {
        'host': '127.0.0.1',
        'port': '5600',
        'api_key': 'your_api_key_here',
        'default_model': "claude-3-haiku-20240307",
        'anthropic_messages_api_url': 'https://api.anthropic.com/v1/messages',
        'Claude': {
            'Opus': 'claude-3-opus-20240229',
            'Sonnet': 'claude-3-sonnet-20240229',
            'Haiku': 'claude-3-haiku-20240307'
        }
    }

    # save default settings to a JSON file, overwriting any existing file
    with open(APP_SETTINGS_LOCATION, 'w') as json_file:
        json.dump(default_settings, json_file, indent=4)

    # update global variables from the default settings:
    global HOST, PORT, ANTHROPIC_API_KEY, ANTHROPIC_API_MODELS
    HOST = default_settings['host']
    PORT = default_settings['port']
    ANTHROPIC_API_KEY = default_settings['api_key']
    ANTHROPIC_API_MODELS = default_settings['Claude']

def load_settings():
    # required to assign a new value to any global value:
    global ANTHROPIC_API_KEY, ANTHROPIC_API_MODELS, HOST, PORT

    set_app_settings_location() # sets APP_SETTINGS_LOCATION

    try:
        with open(APP_SETTINGS_LOCATION, 'r') as json_file:
            settings = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        create_default_settings_db()
        with open(APP_SETTINGS_LOCATION, 'r') as json_file:
            settings = json.load(json_file)

    # check if the settings are incomplete and reinitialize if necessary
    if 'host' not in settings:
        create_default_settings_db()
        with open(APP_SETTINGS_LOCATION, 'r') as json_file:
            settings = json.load(json_file)

    ANTHROPIC_API_KEY = settings.get('api_key')
    ANTHROPIC_API_MODELS = settings.get('Claude', {})
    HOST = settings.get('host')
    PORT = settings.get('port')

def is_port_in_use(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)  # 1 seconds timeout coz app'a api server is local
            result = s.connect_ex((host, int(port)))
            if result == 0:
                logger.info(f"Port {port} on {host} is in use.")
                return True
            else:
                logger.info(f"Port {port} on {host} is not in use.")
                return False
    except Exception as e:
        logger.error(f"Error checking port {host}:{port} - {e}")
        return False

def show_splash_screen():
    welcome_message = '''\n\n
                        Aidetour\n
'talks like Sam; thinks like Claude'\n
OpenAI API  <----> Anthropic API\n\n
'''
    subprocess.Popen(['python', APP_SPLASH, APP_LOGO, welcome_message])

def executable_dir():
    # get the directory where the executable resides:
    if getattr(sys, 'frozen', False):
        # if the application is run as a PyInstaller bundle
        executable_dir = os.path.dirname(sys.executable)
    else:
        # otherwise, just use the current working directory
        executable_dir = os.path.dirname(os.path.realpath(__file__))

    logger.info(f"aidetour_utilities: executable_dir={executable_dir}")
    return executable_dir

def resource_path(relative_path):
    """ Get the absolute path to a resource. This is necessary because PyInstaller
    creates a temporary folder, and the path to resources (like images) needs to be 
    adjusted when the application is bundled into a standalone executable."""
    try:
        # If the application is run by PyInstaller, the `_MEIPASS` attribute contains the path 
        # to the temporary folder containing the application's resources. This attribute is 
        # created by PyInstaller at runtime.
        base_path = sys._MEIPASS
    except Exception:
        # If the application is not bundled, use the current directory.
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def load_models_data():
    models_data = {
        "data": [],
        "object": "list"
    }

    # iterate through the models in ANTHROPIC_API_MODELS
    for model_name, model_id in ANTHROPIC_API_MODELS.items():
        model_data = {
            "id": model_id,
            "object": "model",
            "owned_by": "anthropic",
            "permission": [{}]  # Modify this as per your actual permissions requirements
        }
        models_data["data"].append(model_data)

    return models_data

def remove_markdown(text):
    clean_lines = []
    for line in text.split('\n'):
        # adjusted regex to capture and keep punctuation next to the link
        line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)([,.])?', lambda m: f"{m.group(1)} ({m.group(2)}){m.group(3) if m.group(3) else ''}", line)
        # remove bold and italic Markdown
        line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
        line = re.sub(r'\*([^*]+)\*', r'\1', line)
        # remove Markdown headers
        line = re.sub(r'#+\s*(.*)', r'\1', line)
        clean_lines.append(line)
    return '\n'.join(clean_lines)

def wrap_text(text, width=70):
    wrapped_text = []
    lines = text.split('\n')
    for line in lines:
        if line.strip() == '':
            wrapped_text.append('')
        else:
            wrapped_text.append(textwrap.fill(line, width=width, replace_whitespace=False))

    return '\n'.join(wrapped_text)

