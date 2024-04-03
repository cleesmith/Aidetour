# aidetour_gui_mac

import os
import sys
import subprocess
import logging
import threading
# pip install rumps
import rumps

# Aidetour modules:
import aidetour_utilities
import aidetour_logging
import aidetour_api_handler


# cls: used to debug exit/quit behavior:
# rumps.debug_mode(True)

logger = logging.getLogger('aidetour_gui_mac')

class Aidetour(rumps.App):
    def __init__(self, host, port, api_key):
        super(Aidetour, self).__init__("Aidetour", menu=["Info", "Models", "Logs", "Exit"], quit_button=None)
        # super(Aidetour, self).__init__("Aidetour", icon='Icon_300x200.png', menu=["Info", "Models", "Logs", "Exit"], quit_button=None)
        rumps.App.quit_button = None
        self.host = host
        self.port = port
        self.api_key = api_key
        self.init_flask_server()

    def init_flask_server(self):
        flask_thread = threading.Thread(target=aidetour_api_handler.run_flask_app, args=(self.host, self.port, self.api_key), daemon=True)
        flask_thread.start()

    @rumps.clicked("Exit")
    def exit(self, _):
        logger.info("Aidetour has shutdown! Goodbye.")
        rumps.quit_application()

    @rumps.clicked("Info")
    def info(self, _):
        rumps.alert(title="\nAidetour", message=f"\tLISTENING ON:\n\n\t http://{self.host}:{self.port}\n\n")

    @rumps.clicked("Models")
    def models(self, _):
        log_message = aidetour_utilities.list_models()
        rumps.alert(title="Aidetour", message=log_message)

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

