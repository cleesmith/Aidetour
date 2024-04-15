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

# Aidetour modules:
import aidetour_logging
from aidetour_logging import setup_logger

APP_NAME = "Aidetour"
APP_LOGO = "Aidetour.png"
APP_SPLASH = 'aidetour_splash.py'
APP_LOG = "Log_aidetour.txt"
SERVER_LOG = "Server_log_aidetour.txt"
RUN_SERVER = 'aidetour_run_server.py'
HOST = None
PORT = None
ANTHROPIC_API_KEY = None
ANTHROPIC_API_MODELS = None
ANTHROPIC_MESSAGES_API_URL = 'https://api.anthropic.com/v1/messages'
DEFAULT_MODEL = "claude-3-haiku-20240307"

    
def load_settings():
    # required to assign a new value to any global value:
    global ANTHROPIC_API_KEY, ANTHROPIC_API_MODELS, HOST, PORT
    settings = shelve.open(f"{APP_NAME}_Settings")
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
    welcome_message = '''\n\n
                        Aidetour\n
'talks like Sam; thinks like Claude'\n
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
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showinfo(title, message)
    root.destroy()

def executable_dir():
    # get the directory where the executable resides:
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

def load_models_data():
    models_data = {
        "data": [],
        "object": "list"
    }

    # as of April 2024:
    # ANTHROPIC_API_MODELS = {
    #     'Opus': 'claude-3-opus-20240229', 
    #     'Sonnet': 'claude-3-sonnet-20240229', 
    #     'Haiku': 'claude-3-haiku-20240307'
    # }

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

