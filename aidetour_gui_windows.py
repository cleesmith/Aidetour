# aidetour_gui_windows

import os
import sys
import subprocess
from loguru import logger
import time
import requests
import wx
import wx.adv
from wx import svg

# Aidetour modules:
import aidetour_logging
import aidetour_api_handler
import aidetour_utilities
from aidetour_utilities import APP_NAME, APP_LOGO
from aidetour_utilities import HOST, PORT, ANTHROPIC_API_KEY


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
        self.server_process = None
        icon_path = aidetour_utilities.resource_path(APP_LOGO)
        self.SetIcon(wx.Icon(icon_path), APP_NAME)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

        if aidetour_utilities.is_port_in_use(host, port):
            self.abort_app()
        else:
            self.start_server()

    def CreatePopupMenu(self):
        menu = wx.Menu()
        settings_item = menu.Append(wx.ID_ANY, 'Settings')
        self.Bind(wx.EVT_MENU, self.on_settings, settings_item)
        models_item = menu.Append(wx.ID_ANY, 'Models')
        self.Bind(wx.EVT_MENU, self.on_models, models_item)
        logs_item = menu.Append(wx.ID_ANY, 'Logs')
        self.Bind(wx.EVT_MENU, self.on_logs, logs_item)
        menu.AppendSeparator()
        start_item = menu.Append(wx.ID_ANY, 'Start Server')
        self.Bind(wx.EVT_MENU, self.on_start_server, start_item)
        shutdown_item = menu.Append(wx.ID_ANY, 'Stop Server')
        self.Bind(wx.EVT_MENU, self.on_shutdown, shutdown_item)
        restart_item = menu.Append(wx.ID_ANY, 'Restart Server')
        self.Bind(wx.EVT_MENU, self.on_restart_server, restart_item)
        menu.AppendSeparator()
        exit_item = menu.Append(wx.ID_EXIT, 'Exit')
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        return menu

    def on_left_down(self, event):
        # this "def on_left_down" seems required for some wx reason ?
        pass  

    def on_settings(self, event):
        afile = "config.ini"
        afile = "requirements.txt"
        file_path = aidetour_utilities.resource_path(afile)
        logger.info(f"aidetour_gui_windows: on_settings: file_path={file_path}")
        try:
            # subprocess.run(["notepad.exe", file_path], check=True)
            subprocess.run(["open", afile], check=True) # must be a known filetype, like: .txt
        except Exception as e:
            logger.error(f"Unexpected error occurred while opening {afile} file: {e}", exc_info=True)
            wx.LogError(f"Unexpected error occurred while opening the {afile} file.")

    def on_models(self, event):
        models = aidetour_utilities.list_models()
        dialog = SplitImageDialog(None, APP_NAME, models, aidetour_utilities.resource_path(APP_LOGO))
        dialog.ShowModal()
        dialog.Destroy()

    def on_logs(self, event):
        afile = "Aidetour.log"
        file_path = aidetour_utilities.resource_path(afile)
        try:
            subprocess.run(["notepad.exe", file_path], check=True)
        except Exception as e:
            logger.error(f"Unexpected error occurred while opening {afile} file: {e}", exc_info=True)
            wx.LogError(f"Unexpected error occurred while opening the {afile} file.")

    def on_start_server(self, event):
        logger.info("aidetour_gui_windows: on_start_server")
        if not self.server_process:
            self.server_process = self.start_server()

    def on_shutdown(self, event):
        logger.info("on_shutdown")
        if self.server_process:
            self.stop_server(self.server_process)
            self.server_process = None

    def on_restart_server(self, event):
        logger.info(f"aidetour_gui_windows: on_restart_server: before: {self.server_process}")
        self.restart_server(self.server_process)
        # if self.server_process:
        #     temp_server_process = None
        #     temp_server_process = self.restart_server(self.server_process)
        #     self.server_process = temp_server_process
        logger.info(f"aidetour_gui_windows: on_restart_server: after: {self.server_process}")

    def abort_app(self):
        logger.info(f"ERROR: http://{self.host}:{self.port} is already in use!")
        message = f"ERROR: \n\n\nhttp://{self.host}:{self.port} \n\n\n...is already in use!\n\n\nPlease check your {APP_NAME} configuration."
        # Ensure GUI operations are run in the main thread
        wx.CallAfter(self.show_abort_dialog, message)

    def show_abort_dialog(self, message):
        dialog = SplitImageDialog(None, 
                                  APP_NAME, 
                                  message, 
                                  aidetour_utilities.resource_path(APP_LOGO),
                                  button_label="Exit")
        dialog.ShowModal()
        dialog.Destroy()
        
        # Perform cleanup and exit the application
        self.on_exit(None)
        sys.exit(1)  # Exit the application with an error status code.

    def start_server(self):
        self.server_process = subprocess.Popen(['python', 'run_server.py',
                                                self.host, str(self.port), self.api_key])
        logger.info(f"Server started on {self.host}:{self.port}")

    def stop_server(self, server_process):
        if sys.platform == 'win32':
            self.server_process.terminate()
        else:
            self.server_process.terminate()
            self.server_process.wait()
        logger.info("Server stopped.")

    def restart_server(self, server_process):
        logger.info(f"aidetour_gui_windows: restart_server: before: {self.server_process}")
        if self.server_process:
            self.stop_server(self.server_process)
            self.server_process = None
        time.sleep(1)
        if not self.server_process:
            self.start_server()
        logger.info(f"aidetour_gui_windows: restart_server: after: {self.server_process}")

    def on_exit(self, event=None):
        logger.info(f"aidetour_gui_windows: on_exit: before: {self.server_process}")
        if self.server_process:
            self.stop_server(self.server_process)
            self.server_process = None
        logger.info(f"aidetour_gui_windows: on_exit: after: {self.server_process}")

        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            self.tray_icon.RemoveIcon()
            self.tray_icon.Destroy()
            self.tray_icon = None

        if hasattr(self, 'frame') and self.frame is not None:
            self.frame.Destroy()
            self.frame = None

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

