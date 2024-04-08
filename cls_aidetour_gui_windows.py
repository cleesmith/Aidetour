# aidetour_gui_windows

import os
import sys
import subprocess
import logging
import threading
# pip install requests
import requests
 
# wxPython systray GUI for Windows related:
# pip install wxPython
import wx
import wx.adv
from wx import svg

# Aidetour modules:
import aidetour_logging
import aidetour_api_handler
import aidetour_utilities
from aidetour_utilities import APP_NAME, APP_LOGO
from aidetour_utilities import HOST, PORT, ANTHROPIC_API_KEY


# cls: used to debug exit/quit behavior:
# rumps.debug_mode(True)

logger = logging.getLogger('aidetour_gui_windows')


class SplitImageDialog(wx.Dialog):
    def __init__(self, parent, title, message, image_path, button_label="OK"):
        super().__init__(parent, title=title)
        self.SetBackgroundColour(wx.Colour(30, 30, 30))
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        img = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        img = img.Scale(300, 200, wx.IMAGE_QUALITY_HIGH)
        imageBitmap = wx.Bitmap(img)
        imageControl = wx.StaticBitmap(self, -1, imageBitmap)
        mainSizer.Add(imageControl, 0, wx.ALL | wx.CENTER, 10)
        rightSizer = wx.BoxSizer(wx.VERTICAL)
        font = wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        messageText = wx.StaticText(self, label=message)
        messageText.SetFont(font)  # Set the font for the message text
        messageText.SetForegroundColour(wx.WHITE)  # Set the text color to white
        rightSizer.Add(messageText, 0, wx.ALL | wx.EXPAND, 5)
        aButton = wx.Button(self, label=button_label)
        aButton.SetBackgroundColour(wx.Colour(60, 60, 60))  # Set the button background color
        aButton.SetForegroundColour(wx.RED)  # Set the button text color to white
        aButton.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_OK))
        rightSizer.AddStretchSpacer(prop=1)
        rightSizer.Add(aButton, 0, wx.LEFT, 5)
        mainSizer.Add(rightSizer, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(mainSizer)
        mainSizer.Fit(self)
        self.Layout()


class TrayIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame, host, port, api_key):
        super().__init__()
        self.frame = frame
        self.host = host
        self.port = port
        self.api_key = api_key
        # icon_path = aidetour_utilities.resource_path("Icon_300x200.ico")
        icon_path = aidetour_utilities.resource_path("Aidetour.png")
        self.SetIcon(wx.Icon(icon_path), "Aidetour")
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)


        # self.abort_app()

        # let's check here first for host+port in use, but also
        # double check this again within def init_flask_server (if possible):
        if aidetour_utilities.is_port_in_use(host, port):
            self.abort_app()
        else:
            self.init_flask_server()

    def init_flask_server(self):
        server_status = {'error': False, 'exception': None}
        self.flask_thread = threading.Thread(target=aidetour_api_handler.run_flask_app, 
            args=(self.host, self.port, self.api_key, server_status), 
            daemon=True)
        self.flask_thread.start()
        # cls: does not work on Mac:
        # flask_thread.join()  # Wait for the thread to complete = this blocks
        # if server_status['error']:
        #     self.abort_app()
        # elif server_status['exception'] is not None:
        #     # Handle or log the exception as needed
        #     print(f"Exception occurred: {server_status['exception']}")

    def CreatePopupMenu(self):
        menu = wx.Menu()
        info_item = menu.Append(wx.ID_ANY, 'Info')
        self.Bind(wx.EVT_MENU, self.on_info, info_item)
        models_item = menu.Append(wx.ID_ANY, 'Models')
        self.Bind(wx.EVT_MENU, self.on_models, models_item)
        logs_item = menu.Append(wx.ID_ANY, 'Logs')
        self.Bind(wx.EVT_MENU, self.on_logs, logs_item)
        menu.AppendSeparator()
        shutdown_item = menu.Append(wx.ID_ANY, 'Shutdown Server')
        self.Bind(wx.EVT_MENU, self.on_shutdown, shutdown_item)
        menu.AppendSeparator()
        exit_item = menu.Append(wx.ID_EXIT, 'Exit')
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        return menu

    def on_left_down(self, event):
        # this "def on_left_down" seems required for some wx reason ?
        pass  

    def on_info(self, event):
        # dialog = SplitImageDialog(None, "Aidetour", f"LISTENING ON:\n\nhttp://{self.host}:{self.port}\n\n", aidetour_utilities.resource_path("icon_300x200.png"))
        # message = f"LISTENING ON:\n\nhttp://{self.host}:{self.port}\n\n"
        # dialog = wx.MessageDialog(None, message, "Aidetour", wx.OK|wx.ICON_INFORMATION)
        # dialog.ShowModal()
        # dialog.Destroy()
        afile = "config.ini"
        afile = "requirements.txt"
        file_path = aidetour_utilities.resource_path(afile)
        try:
            # subprocess.run(["notepad.exe", file_path], check=True)
            subprocess.run(["open", afile], check=True) # must be a known filetype, like: .txt
        except Exception as e:
            logger.error(f"Unexpected error occurred while opening {afile} file: {e}", exc_info=True)
            wx.LogError(f"Unexpected error occurred while opening the {afile} file.")

    def on_models(self, event):
        models = aidetour_utilities.list_models()
        dialog = SplitImageDialog(None, "Aidetour", models, aidetour_utilities.resource_path("Aidetour.png"))
        # dialog = wx.MessageDialog(None, models, "Aidetour", wx.OK|wx.ICON_INFORMATION)
        dialog.ShowModal()
        dialog.Destroy()

    def on_logs(self, event):
        afile = "Aidetour.log"
        file_path = aidetour_utilities.resource_path(afile)
        try:
            subprocess.run(["notepad.exe", file_path], check=True)
        except Exception as e:
            logger.error(f"Unexpected error occurred while opening Aidetour.log file: {e}", exc_info=True)
            wx.LogError(f"Unexpected error occurred while opening the {afile} file.")

    def on_shutdown(self, event):
        # Send a shutdown request to the server
        response = requests.post(f'http://{self.host}:{self.port}/v1/shutdown')
        if response.status_code == 200:
            # while self.server_status['running']:
            #     time.sleep(1)  # Wait for the server to stop running
            self.flask_thread = None
            print("Flask server has stopped")
        else:
            print(f"Failed to stop the server. Status code: {response.status_code}")

    def abort_app(self):
        logger.info(f"ERROR: http://{self.host}:{self.port} is already in use!")
        message = f"ERROR: \n\n\nhttp://{self.host}:{self.port} \n\n\n...is already in use!\n\n\nPlease check your {APP_NAME} configuration."
        # Ensure GUI operations are run in the main thread
        wx.CallAfter(self.show_abort_dialog, message)

    def show_abort_dialog(self, message):
        dialog = SplitImageDialog(None, 
                                  "Aidetour", 
                                  message, 
                                  aidetour_utilities.resource_path("Aidetour.png"),
                                  button_label="Exit")
        dialog.ShowModal()
        dialog.Destroy()
        
        # Perform cleanup and exit the application
        self.on_exit(None)
        sys.exit(1)  # Exit the application with an error status code.

    def on_exit(self, event=None):
        # Remove the tray icon to avoid leaving a phantom icon in the system tray
        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            self.tray_icon.RemoveIcon()
            self.tray_icon.Destroy()
            self.tray_icon = None

        # Close the main application window, if it exists
        if hasattr(self, 'frame') and self.frame is not None:
            self.frame.Destroy()
            self.frame = None

        # Explicitly terminate the application's main loop
        wx.GetApp().ExitMainLoop()


class Aidetour(wx.App):
    def __init__(self, host, port, api_key, redirect=False):
        self.host = host
        self.port = port
        self.api_key = api_key
        super().__init__(redirect)

    def OnInit(self):
        frame = wx.Frame(None)
        self.SetTopWindow(frame)
        TrayIcon(frame, self.host, self.port, self.api_key)
        return True

