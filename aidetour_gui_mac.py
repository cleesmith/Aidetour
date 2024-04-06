# aidetour_gui_mac

import os
import sys
import subprocess
import logging
import threading
# pip install rumps
import rumps

# Aidetour modules:
import aidetour_logging
import aidetour_api_handler
import aidetour_utilities
from aidetour_utilities import APP_NAME, APP_LOGO
from aidetour_utilities import HOST, PORT, ANTHROPIC_API_KEY


# cls: used to debug exit/quit behavior:
# rumps.debug_mode(True)

logger = logging.getLogger('aidetour_gui_mac')


#     window = rumps.Window(title='Aidetour', 
#         message=welcome_message,
#         default_text='ANTHROPIC_API_KEY=', 
#         ok='Confirm', 
#         cancel='Abort', 
#         dimensions=(700, 400))
#     window.icon = 'Aidetour.png'
#     response = window.run()

class Aidetour(rumps.App):
    def __init__(self, host, port, api_key):
        super(Aidetour, self).__init__(APP_NAME, 
            icon=APP_LOGO, 
            menu=["Info", "Models", "About", "Logs", "Exit"], 
            # template=True, 
            quit_button=None)

        rumps.App.quit_button = None
        rumps.App.icon = APP_LOGO

        self.host = host
        self.port = port
        self.api_key = api_key

        # let's check here first for host+port in use, but also
        # double check this again within def init_flask_server:
        if aidetour_utilities.is_port_in_use(host, port):
            self.abort_app()
        else:
            self.init_flask_server()

    def abort_app(self):
        logger.info(f"ERROR: http://{self.host}:{self.port} is already in use!")
        rumps.alert(title=f"\n{APP_NAME}", 
            message=f"ERROR: \n\nhttp://{self.host}:{self.port} \n\n...is already in use!\n\nPlease check {APP_NAME}'s configuration.", 
            ok='Exit',
            icon_path=APP_LOGO)
        rumps.quit_application()

    def init_flask_server(self):
        server_status = {'error': False, 'exception': None}
        flask_thread = threading.Thread(target=aidetour_api_handler.run_flask_app, 
            args=(self.host, self.port, self.api_key, server_status), 
            daemon=True)
        flask_thread.start()
        flask_thread.join()  # Wait for the thread to complete = this blocks
        if server_status['error']:
            self.abort_app()
        elif server_status['exception'] is not None:
            # Handle or log the exception as needed
            print(f"Exception occurred: {server_status['exception']}")

    @rumps.clicked("Exit")
    def exit(self, _):
        logger.info(f"{APP_NAME} has shutdown! Goodbye.")
        rumps.quit_application()

    @rumps.clicked("About")
    def splash(self, _):
        aidetour_utilities.show_splash_screen()

    @rumps.clicked("Info")
    def info(self, _):
        rumps.alert(title=f"\n{APP_NAME}", 
            message=f"\tLISTENING ON:\n\n\t http://{self.host}:{self.port}\n\n", 
            icon_path=APP_LOGO)

    @rumps.clicked("Models")
    def models(self, _):
        log_message = aidetour_utilities.list_models()
        rumps.alert(title="Aidetour", 
            message=log_message,
            icon_path=APP_LOGO)

    @rumps.clicked("Logs")
    def logs(self, _):
        # this does not tail properly coz it's a subprocess:
        #   subprocess.run(["open", "-a", "Terminal", "-n", "--args", "tail", "-f", afile])
        # this opens a new Terminal with each click, so this isn't useful:
        #   os.system(f"osascript -e 'tell application \"Terminal\" to do script \"tail -f {afile}\"'")
        # this opens log in TextEdit, so possibly useful:
        #   subprocess.run(["open", "-a", "TextEdit", afile], check=True)
        try:
            # testing in case some Mac users don't have the Console app:
            #   Simulate FileNotFoundError
            #       raise FileNotFoundError("Simulated FileNotFoundError")
            #   Simulate subprocess.CalledProcessError
            #       raise subprocess.CalledProcessError(returncode=1, cmd=["open", afile], output="Simulated CalledProcessError")
            #   Simulate unexpected Exception
            #       raise Exception("Simulated unexpected Exception")
            afile = "Aidetour.log"
            # subprocess.run(["open"... relies on user's default action for "open" and in macOS this is the Console app:
            #   this hide Terminal messages, but not needed as this app can be CLI/GUI:
            #       subprocess.run(["open", "cls.spud"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # subprocess.run(["open", afile], check=True)
            subprocess.run(["open", "-a", "TextEdit", afile], check=True)
        except FileNotFoundError:
            logger.error(f"Log file not found: {afile}", exc_info=True)
            rumps.alert(title="Error", message="The {afile} file could not be found.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to open {afile} file: {e}", exc_info=True)
            rumps.alert(title="Error", message=f"An error occurred while opening the {afile} file.")
        except Exception as e:
            logger.error(f"Unexpected error occurred while opening {afile} file: {e}", exc_info=True)
            rumps.alert(title="Error", message=f"An unexpected error occurred while opening the {afile} file.")

