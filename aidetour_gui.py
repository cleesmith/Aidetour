# aidetour_gui

import os
import sys
import shelve
import subprocess
import time
import requests
from loguru import logger
import wx
from wx import svg
from wx.adv import TaskBarIcon as TaskBarIcon
import wx.adv
import wx.html2
import webbrowser

# Aidetour modules:
import aidetour_logging
import aidetour_api_handler
import aidetour_utilities
# an alias to 'config.' instead of 'aidetour_utilities.'
import aidetour_utilities as config 

SERVER_PROCESS = None

def start_server():
    global SERVER_PROCESS
    SERVER_PROCESS = subprocess.Popen(['python', 
        config.RUN_SERVER,
        config.HOST, 
        str(config.PORT), 
        config.ANTHROPIC_API_KEY])
    logger.info(f"Attempting to start API Server on {config.HOST}:{config.PORT}\nSERVER_PROCESS={SERVER_PROCESS}")

def stop_server():
    if sys.platform == 'win32':
        SERVER_PROCESS.terminate()
    else:
        SERVER_PROCESS.terminate()
        SERVER_PROCESS.wait()
    logger.info("Attempting to stop API Server.")


class SplitImageDialog(wx.Dialog):
    def __init__(self, parent, title, message, image_path, button_label="OK"):
        super().__init__(parent, title=title)
        # self.SetBackgroundColour(wx.Colour(30, 30, 30))
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        img = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        img = img.Scale(300, 200, wx.IMAGE_QUALITY_HIGH)
        imageBitmap = wx.Bitmap(img)
        imageControl = wx.StaticBitmap(self, -1, imageBitmap)
        mainSizer.Add(imageControl, 0, wx.ALL | wx.CENTER, 10)
        rightSizer = wx.BoxSizer(wx.VERTICAL)
        font = wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        messageText = wx.StaticText(self, label=message)
        # messageText.SetFont(font)  # Set the font for the message text
        # messageText.SetForegroundColour(wx.WHITE)  # Set the text color to white
        rightSizer.Add(messageText, 0, wx.ALL | wx.EXPAND, 5)
        aButton = wx.Button(self, label=button_label)
        # aButton.SetBackgroundColour(wx.Colour(60, 60, 60))  # Set the button background color
        # aButton.SetForegroundColour(wx.RED)  # Set the button text color to white
        aButton.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(wx.ID_OK))
        rightSizer.AddStretchSpacer(prop=1)
        rightSizer.Add(aButton, 0, wx.LEFT, 5)
        mainSizer.Add(rightSizer, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(mainSizer)
        mainSizer.Fit(self)
        self.Layout()


class AlertsDialog(wx.Dialog):
    def __init__(self, parent, title, message):
        super(AlertsDialog, self).__init__(parent, title=title)
        self.init_ui(message)
        self.SetSize((300, 200))
        self.Centre()

    def init_ui(self, message):
        vbox = wx.BoxSizer(wx.VERTICAL)
        message_label = wx.StaticText(self, label=message)
        vbox.Add(message_label, flag=wx.ALL|wx.CENTER, border=10, proportion=1)
        okButton = wx.Button(self, label='Ok')
        okButton.Bind(wx.EVT_BUTTON, self.on_close)
        vbox.Add(okButton, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)
        self.SetSizer(vbox)

    def on_close(self, event):
        self.Destroy()


class SettingsDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(SettingsDialog, self).__init__(parent, title=title, size=(350, 480))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.host = wx.TextCtrl(panel)
        self.port = wx.TextCtrl(panel)
        self.api_key = wx.TextCtrl(panel)
        self.models = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        vbox.Add(wx.StaticText(panel, -1, 'Local API Server IP:'), flag=wx.EXPAND|wx.ALL, border=10)
        vbox.Add(self.host, flag=wx.EXPAND|wx.ALL, border=10)
        vbox.Add(wx.StaticText(panel, -1, 'Port:'), flag=wx.EXPAND|wx.ALL, border=10)
        vbox.Add(self.port, flag=wx.EXPAND|wx.ALL, border=10)
        vbox.Add(wx.StaticText(panel, -1, 'Your Anthropic API Key:'), flag=wx.EXPAND|wx.ALL, border=10)
        vbox.Add(self.api_key, flag=wx.EXPAND|wx.ALL, border=10)
        vbox.Add(wx.StaticText(panel, -1, 'Claude 3 models:'), flag=wx.EXPAND|wx.ALL, border=10)
        vbox.Add(self.models, flag=wx.EXPAND|wx.ALL, border=10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(panel, label='Ok')
        restartButton = wx.Button(panel, label='Restart Server')
        closeButton = wx.Button(panel, label='Cancel')
        hbox.Add(okButton, flag=wx.RIGHT, border=10)
        hbox.Add(restartButton, flag=wx.LEFT|wx.RIGHT, border=10)
        hbox.Add(closeButton, flag=wx.LEFT, border=10)
        vbox.Add(hbox, flag=wx.ALIGN_CENTER|wx.ALL, border=10)

        panel.SetSizer(vbox)
        
        self.Bind(wx.EVT_BUTTON, self.OnSave, okButton)
        self.Bind(wx.EVT_BUTTON, self.OnRestart, restartButton)
        self.Bind(wx.EVT_BUTTON, self.OnClose, closeButton)

        # super(SettingsDialog, self).__init__(parent, 
        #     title=title, 
        #     size=(350, 480))
        
        # panel = wx.Panel(self)
        # vbox = wx.BoxSizer(wx.VERTICAL)
        
        # self.host = wx.TextCtrl(panel, -1, style=wx.TE_PROCESS_ENTER, size=(200, -1))
        # self.port = wx.TextCtrl(panel, -1, style=wx.TE_PROCESS_ENTER, size=(200, -1))
        # self.api_key = wx.TextCtrl(panel, -1, style=wx.TE_PROCESS_ENTER, size=(200, -1))
        # self.models = wx.TextCtrl(panel, 
        #     pos=(10, 10), 
        #     size=(300, 120), 
        #     style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        # self.models.SetBackgroundColour("DARK GRAY")
        # self.models.SetForegroundColour("WHEAT")
        
        # vbox.AddSpacer(5)

        # label00 = wx.StaticText(panel, -1, 'Your Local API Server', style=wx.ALIGN_CENTER)
        # label00.SetForegroundColour('SEA GREEN')
        # font = wx.Font(16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        # label00.SetFont(font)
        # vbox.Add(label00, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        # vbox.AddSpacer(2)

        # # label0 = wx.StaticText(panel, -1, 
        # #     '"talks like Sam; thinks like Claude"',
        # #     style=wx.ALIGN_CENTER)
        # # label0.SetForegroundColour('WHEAT')
        # # font = wx.Font(12, wx.FONTFAMILY_SCRIPT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 
        # #     faceName="Comic Sans MS")
        # # label0.SetFont(font)
        # # vbox.Add(label0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        # # vbox.AddSpacer(3)

        # label1 = wx.StaticText(panel, -1, 'Host:', style=wx.LEFT)
        # label1.SetForegroundColour('SEA GREEN')
        # font = wx.Font(16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        # label1.SetFont(font)
        # vbox.Add(label1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        # vbox.Add(self.host, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        # vbox.AddSpacer(10)

        # label2 = wx.StaticText(panel, -1, 'Port:', style=wx.LEFT)
        # label2.SetForegroundColour('SEA GREEN')
        # font = wx.Font(16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        # label2.SetFont(font)
        # vbox.Add(label2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        # vbox.Add(self.port, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        # vbox.AddSpacer(10)

        # hbox = wx.BoxSizer(wx.HORIZONTAL)
        # hbox.Add((10, -1), proportion=0)  # Left margin, adjust '20' as needed for indentation
        # line = wx.Panel(panel, -1, size=(330, 2))  # Adjust '100' to required width, '2' for height
        # line.SetBackgroundColour('SIENNA')
        # hbox.Add(line, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)
        # hbox.Add((20, -1), proportion=0)  # Right margin, adjust '20' as needed
        # vbox.Add(hbox, proportion=0, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=10)
        # vbox.AddSpacer(10)

        # label3 = wx.StaticText(panel, -1, 'Your Anthropic API Key:', style=wx.LEFT)
        # label3.SetForegroundColour('FIREBRICK')
        # font = wx.Font(20, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_EXTRABOLD)
        # label3.SetFont(font)
        # vbox.Add(label3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        # vbox.AddSpacer(5)
        # vbox.Add(self.api_key, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        # vbox.AddSpacer(20)

        # label4 = wx.StaticText(panel, -1, 'Claude 3 models', style=wx.ALIGN_CENTER)
        # label4.SetForegroundColour('WHEAT')
        # font = wx.Font(16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        # label4.SetFont(font)
        # vbox.Add(label4, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        # vbox.AddSpacer(5)
        # vbox.Add(self.models, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)

        # # bottom row of buttons:
        # hbox = wx.BoxSizer(wx.HORIZONTAL)
        # okButton = wx.Button(panel, label='Ok')
        # hbox.Add(okButton)
        # restartButton = wx.Button(panel, label='Restart Server')
        # hbox.Add(restartButton, flag=wx.LEFT, border=15)
        # closeButton = wx.Button(panel, label='Cancel')
        # hbox.Add(closeButton, flag=wx.LEFT, border=15)
        # vbox.AddSpacer(20)
        # vbox.Add(hbox, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=5)
        # panel.SetSizer(vbox)
        # self.Bind(wx.EVT_BUTTON, self.OnSave, okButton)
        # self.Bind(wx.EVT_BUTTON, self.OnRestart, restartButton)
        # self.Bind(wx.EVT_BUTTON, self.OnClose, closeButton)
        # vbox.AddSpacer(50)

        # load most recent Settings for this dialog box:
        aidetour_utilities.load_settings()
        self.api_key.SetValue(config.ANTHROPIC_API_KEY)
        # make the list of models more readable for users:
        models_str = "As of April 2024; this list may not be changed.\n\n"
        models_str += "\n".join([f"{key}:\t {value}" for key, value in config.ANTHROPIC_API_MODELS.items()])
        self.models.SetValue(models_str)
        self.host.SetValue(config.HOST)
        self.port.SetValue(config.PORT)

    def OnSave(self, event):
        try:
            settings = shelve.open(config.APP_SETTINGS_LOCATION)
        except Exception as e:
            aidetour_utilities.create_default_settings_db()
            settings = shelve.open(config.APP_SETTINGS_LOCATION)
        settings['api_key'] = self.api_key.GetValue()
        settings['host'] = self.host.GetValue()
        settings['port'] = int(self.port.GetValue())
        settings.close()
        self.Destroy()
    
    def OnRestart(self, event):
        try:
            settings = shelve.open(config.APP_SETTINGS_LOCATION)
        except Exception as e:
            aidetour_utilities.create_default_settings_db()
            settings = shelve.open(config.APP_SETTINGS_LOCATION)
        settings['api_key'] = self.api_key.GetValue()
        settings['host'] = self.host.GetValue()
        settings['port'] = int(self.port.GetValue())
        settings.close()
        stop_server()
        aidetour_utilities.load_settings()
        start_server()
        self.Destroy()
    
    def OnClose(self, event):
        self.Destroy()


class LogsDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(LogsDialog, self).__init__(parent, title=title, size=(600, 400), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.log_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        # font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        # font = wx.Font(16, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        font = wx.Font(16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.log_text.SetFont(font)
        vbox.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 10)
        
        done_button = wx.Button(panel, label="Done")
        done_button.Bind(wx.EVT_BUTTON, self.OnDone)
        vbox.Add(done_button, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        panel.SetSizer(vbox)
        
        self.load_logs()
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    
    def load_logs(self):
        try:
            with open(config.APP_LOG, "r") as file:
                logs = file.read()
                self.log_text.SetValue(logs)
        except FileNotFoundError:
            self.log_text.SetValue("Aidetour.log file not found.")
    
    def OnClose(self, event):
        self.Destroy()
    
    def OnDone(self, event):
        self.Destroy()


class YouTubeDialog(wx.Dialog):
    def __init__(self, parent, video_id):
        super().__init__(parent, 
            title="YouTube Video", 
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.panel = wx.Panel(self)

        self.vid = video_id
        self.webview = wx.html2.WebView.New(self.panel)
        video_url = f"https://www.youtube.com/embed/{self.vid}"
        self.webview.LoadURL(video_url)

        self.btn_youtube = wx.Button(self.panel, label="Open on YouTube")
        self.btn_youtube.Bind(wx.EVT_BUTTON, self.on_youtube_click)

        self.btn_done = wx.Button(self.panel, label="Done")
        self.btn_done.Bind(wx.EVT_BUTTON, self.on_done_click)

        # Layout for buttons using a horizontal box sizer
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_sizer.Add(self.btn_youtube, 0, wx.ALL, 5)
        self.button_sizer.AddSpacer(60)
        self.button_sizer.Add(self.btn_done, 0, wx.ALL, 5)

        # Main sizer for the dialog, including the webview and the button sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.webview, 1, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.panel.SetSizer(self.main_sizer)
        self.SetSize((600, 400))

    def on_youtube_click(self, event):
        webbrowser.open(f"https://www.youtube.com/watch?v={self.vid}")

    def on_done_click(self, event):
        self.Close()

class MenuStuff(TaskBarIcon):
    def __init__(self, frame):
        super(MenuStuff, self).__init__()
        self.SetIcon(wx.Icon(config.APP_LOGO, wx.BITMAP_TYPE_PNG), config.APP_NAME)

        self.frame = frame

        global SERVER_PROCESS
        SERVER_PROCESS = None

        if aidetour_utilities.is_port_in_use(config.HOST, config.PORT):
            self.abort_app()
        else:
            # this sets SERVER_PROCESS, so it can be terminated if needed:
            start_server()
            print(f"MenuStuff: *** SERVER_PROCESS={SERVER_PROCESS}")

        if SERVER_PROCESS is None:
            message = "\nError starting the API Server.\n\nPlease check the Settings.\n"
            message += f"\n{config.HOST}:{config.PORT}\n"
            # wx.MessageBox(message, 'Alert', wx.OK | wx.ICON_ERROR)
            dlg = SplitImageDialog(None, 
                config.APP_NAME, 
                message,
                aidetour_utilities.resource_path(config.APP_LOGO),
                button_label="Ok")
            dlg.ShowModal()
            dlg.Destroy()

        # these 'state control attributes' are used to avoid multiple popups of the same dialog box:
        self.alerts_dialog = None
        self.settings_dialog = None
        self.logs_dialog = None
        self.video_dialog = None
        self.Bind(wx.EVT_MENU, self.OnAlerts, id=1)
        self.Bind(wx.EVT_MENU, self.OnSettings, id=2)
        self.Bind(wx.EVT_MENU, self.OnLogs, id=3)
        self.Bind(wx.EVT_MENU, self.OnVideo, id=4)
        self.Bind(wx.EVT_MENU, self.OnExit, id=5)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(1, 'Alerts')
        menu.Append(2, 'Settings')
        menu.Append(3, 'Log')
        menu.Append(4, 'Video')
        menu.Append(5, 'Exit')
        return menu

    def OnAlerts(self, event):
        if not self.alerts_dialog or not self.alerts_dialog.IsShown():
            self.alerts_dialog = AlertsDialog(None, f"{config.APP_NAME} Alerts", 'This is an alert message.')
            self.alerts_dialog.Show()

    def OnSettings(self, event):
        if not self.settings_dialog or not self.settings_dialog.IsShown():
            self.settings_dialog = SettingsDialog(None, f"{config.APP_NAME} Settings")
            self.settings_dialog.Show()

    def OnLogs(self, event):
        if not self.logs_dialog or not self.logs_dialog.IsShown():
            self.logs_dialog = LogsDialog(None, f"{config.APP_NAME} Log")
            self.logs_dialog.Show()

    def OnVideo(self, event):
        if not self.video_dialog or not self.video_dialog.IsShown():
            video_id = "J7tab9JwbaI?si=sbmaZr6eeLGGjfq_"
            self.video_dialog = YouTubeDialog(None, video_id)
            self.video_dialog.Show()

    def OnExit(self, event=None):
        global SERVER_PROCESS
        if SERVER_PROCESS:
            stop_server()
            SERVER_PROCESS = None

        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            self.tray_icon.RemoveIcon()
            self.tray_icon.Destroy()
            self.tray_icon = None

        if hasattr(self, 'frame') and self.frame is not None:
            self.frame.Destroy()
            self.frame = None

        wx.GetApp().ExitMainLoop()

    def abort_app(self):
        logger.info(f"ERROR: http://{config.HOST}:{config.PORT} is already in use!")
        message = f"ERROR: \n\n\nhttp://{config.HOST}:{config.PORT} \n\n\n...is already in use!\n\n\nPlease check your {config.APP_NAME} configuration."
        # ensure GUI operations are run in the main thread
        wx.CallAfter(self.show_abort_dialog, message)

    def show_abort_dialog(self, message):
        dialog = SplitImageDialog(None, 
                                  config.APP_NAME, 
                                  message, 
                                  aidetour_utilities.resource_path(config.APP_LOGO),
                                  button_label="Exit")
        dialog.ShowModal()
        dialog.Destroy()
        self.on_exit(None)
        sys.exit(1)


class GuiStuff(wx.App):
    def OnInit(self):
        frame = wx.Frame(wx.Frame(None, size=(0, 0)))  # ensure it's properly hidden
        self.SetTopWindow(frame)
        # wx.MessageBox('spud!!!', 'Alert', wx.OK | wx.ICON_INFORMATION)
        MenuStuff(frame)
        return True
