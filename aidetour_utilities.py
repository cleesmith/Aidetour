# aidetour_utilities.py

import os
import shelve
import socket
import sys
from loguru import logger
import configparser
import subprocess
import tkinter as tk
from tkinter import messagebox

import aidetour_logging
from aidetour_logging import setup_logger

APP_NAME = "Aidetour"
APP_LOG = "Aidetour.log"
APP_LOGO = "Aidetour.png"
APP_SPLASH = 'aidetour_splash.py'
HOST = None
PORT = None
ANTHROPIC_API_KEY = None
ANTHROPIC_API_MODELS = None

    
def load_settings():
    # required to assign a new value to any global value:
    global ANTHROPIC_API_KEY, ANTHROPIC_API_MODELS, HOST, PORT
    settings = shelve.open('Aidetour_Settings')
    ANTHROPIC_API_KEY = settings.get('api_key', '')
    ANTHROPIC_API_MODELS = settings['Claude']
    models_str = "\n".join([f"{key}:\t {value}" for key, value in ANTHROPIC_API_MODELS.items()])
    HOST = settings.get('host', '')
    PORT = str(settings.get('port', ''))
    settings.close()

def is_port_in_use(host, port):
    # note: these 3 host values all catch the error:
    # host = 'localhost'
    # host = '0.0.0.0'
    # host = '127.0.0.1'
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, int(port))) == 0

def show_splash_screen():
#     welcome_message = '''
# ------------------------------------------------------------------------------
# Aidetour is an app that acts as a middleman between the OpenAI API and 
# the Anthropic Claude API. When Aidetour receives a request intended for the 
# OpenAI system, it translates that request into a proper Anthropic API request.
# The translated request is sent to the Anthropic API then waits for a response. 
# Once the response is received, Aidetour converts that back into an OpenAI API
# formatted streamed response.
# ------------------------------------------------------------------------------
# 1. Configure your Anthropic API key in .env file.
# 2. Configure your host and port in config.ini file.
# 3. Configure the Claude 3 models available from Anthropic.
# '''
    welcome_message = '''\n\n
                        Aidetour\n
'speaks like Sam; thinks like Claude'\n
OpenAI API  <----> Anthropic API\n\n
'''
    subprocess.Popen(['python', APP_SPLASH, APP_LOGO, welcome_message])

def show_custom_message(title, message):
    # Create a root window
    root = tk.Tk()
    root.title(title)

    # Set window size and position
    root.geometry('400x300+300+300')  # Width x Height + X_offset + Y_offset

    # Create a label for the message, with text left-justified
    message_label = tk.Label(root, text=message, justify=tk.LEFT, wraplength=350)
    message_label.pack(pady=20, padx=20, anchor='w')  # anchor 'w' aligns the label itself to the left

    # Create an OK button to close the dialog
    ok_button = tk.Button(root, text='OK', command=root.destroy)
    ok_button.pack(pady=20)

    root.mainloop()

def show_simple_message(title, message):
    # Create a root window, but keep it hidden
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Show the message box
    messagebox.showinfo(title, message)

    # Destroy the root window after the message box is dismissed
    root.destroy()

def executable_dir():
    """Get the directory where the executable resides."""
    if getattr(sys, 'frozen', False):
        # If the application is run as a PyInstaller bundle
        executable_dir = os.path.dirname(sys.executable)
    else:
        # Otherwise, just use the current working directory
        executable_dir = os.path.dirname(os.path.realpath(__file__))

    logger.info(f">>>>>>>> executable_dir={executable_dir}")
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

def check_create_config_files():
    return True
    config_files = [
        '.env',
        'config.ini',
        'models.ini',
        'Aidetour.log'
    ]
    all_files_ok = True

    for file in config_files:
        if not os.path.isfile(file):
            all_files_ok = False
            if file == '.env':
                with open(file, 'w') as f:
                    f.write('ANTHROPIC_API_KEY=your_api_key_here\n')
            elif file == 'config.ini':
                config = configparser.ConfigParser()
                config['Server'] = {
                    'host': '127.0.0.1',
                    'port': '5600'
                }
                with open(file, 'w') as f:
                    config.write(f)
            elif file == 'models.ini':
                config = configparser.ConfigParser()
                config['Claude'] = {
                    'Opus': 'claude-3-opus-20240229',
                    'Sonnet': 'claude-3-sonnet-20240229',
                    'Haiku': 'claude-3-haiku-20240307'
                }
                with open(file, 'w') as f:
                    config.write(f)
            elif file == 'Aidetour.log':
                with open(file, 'w') as f:
                    pass

    if all_files_ok:
        logger.info("All configuration files are present.")
    else:
        print("Configuration files checked and created if necessary.")
        logger.info("Configuration files checked and created if necessary.")
        print("Please edit the following files with your specific settings:")
        logger.info("Please edit the following files with your specific settings:")
        print("- .env: Set your Anthropic API key")
        logger.info("- .env: Set your Anthropic API key")
        print("- config.ini: Configure the server settings (host and port)")
        logger.info("- config.ini: Configure the server settings (host and port)")
        print("- models.ini: Update with details about Claude's different models")
        logger.info("- models.ini: Update with details about Claude's different models")

    return all_files_ok

def read_config_ini():
    config = configparser.ConfigParser()
    config.read('config.ini')
    host = config.get('Server', 'host', fallback='127.0.0.1')
    port = config.getint('Server', 'port', fallback=5600)
    logger.info(f"read_config_ini: config.ini: host={host} port={port}.")
    return host, port

# Function to load models from models.ini and construct MODELS_DATA
def load_models_data():
    config = configparser.ConfigParser()
    # config.optionxform = str
    config.read('models.ini')

    models_data = {
        "data": [],
        "object": "list"
    }

    # Assuming all models belong to 'anthropic' and have the same structure
    for model_name, model_id in config['Claude'].items():
        model_data = {
            "id": model_id,
            "object": "model",
            "owned_by": "anthropic",
            "permission": [{}]
        }
        models_data["data"].append(model_data)

    # logger.info("load_models_data: models_data: %s", models_data)
    return models_data

def list_models():
    models = "Anthropic API models\nClaude 3 Models:\n"
    models_data = load_models_data()
    for index, model in enumerate(models_data["data"], start=1):
        models += f"{model['id']}\n"
    return models

