# aidetour_gui

import os
import sys
import json
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

APP_STATUS_MESSAGES = None
SERVER_PROCESS = None


def start_server():
    global SERVER_PROCESS
    logger.info(f"{config.HOST} {config.PORT} type(config.PORT)={type(config.PORT)} {config.RUN_SERVER}")
    aidetour_utilities.log_app_settings(logger)
    # ************   ****************
    SERVER_PROCESS = subprocess.Popen(['python', 
        config.RUN_SERVER,
        config.HOST, 
        config.PORT, 
        config.ANTHROPIC_API_KEY])
    logger.info(f"Attempting to start API Server on {config.HOST}:{config.PORT}\nSERVER_PROCESS={SERVER_PROCESS}")

def stop_server():
    # not needed, plus it's out of place in the log:
    # logger.info(f"Attempting to stop API Server process on platform {sys.platform}.")
    if sys.platform == 'win32':
        SERVER_PROCESS.terminate()
    else:
        SERVER_PROCESS.terminate()
        SERVER_PROCESS.wait()


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


class StatusDialog(wx.Dialog):
    def __init__(self, parent, title, message):
        super(StatusDialog, self).__init__(parent, title=title, size=(600, 400), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.log_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        font = wx.Font(16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.log_text.SetFont(font)
        vbox.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 10)

        clear_button = wx.Button(panel, label="Clear messages")
        clear_button.Bind(wx.EVT_BUTTON, self.OnClear)
        done_button = wx.Button(panel, label="Done")
        done_button.Bind(wx.EVT_BUTTON, self.OnDone)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(clear_button, flag=wx.LEFT|wx.RIGHT, border=10)
        # hbox.Add(done_button, flag=wx.LEFT, border=10)
        hbox.Add(done_button, border=10)
        vbox.Add(hbox, flag=wx.ALIGN_CENTER|wx.ALL, border=10)
                
        panel.SetSizer(vbox)
        self.log_text.SetValue(message)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    
    def OnClear(self, event):
        global APP_STATUS_MESSAGES
        APP_STATUS_MESSAGES = ""
        self.Destroy()
    
    def OnClose(self, event):
        self.Destroy()
    
    def OnDone(self, event):
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
        
        vbox.AddSpacer(15)

        vbox.Add(wx.StaticText(panel, -1, 'Local API Server IP:'), flag=wx.ALIGN_LEFT|wx.ALL, border=5)
        vbox.Add(self.host, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.AddSpacer(10)

        vbox.Add(wx.StaticText(panel, -1, 'Port:'), flag=wx.ALIGN_LEFT|wx.ALL, border=5)
        vbox.Add(self.port, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.AddSpacer(10)

        vbox.Add(wx.StaticText(panel, -1, 'Your Anthropic API Key:'), flag=wx.ALIGN_LEFT|wx.ALL, border=5)
        vbox.Add(self.api_key, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.AddSpacer(20)

        vbox.Add(wx.StaticText(panel, -1, 'Claude 3 models April 2024'), proportion=0, flag=wx.ALIGN_CENTER|wx.ALL, border=5)
        vbox.Add(self.models, flag=wx.EXPAND|wx.ALL, border=5)
        vbox.AddSpacer(20)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(panel, label='Save')
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

        # load Settings for this dialog box:
        aidetour_utilities.load_settings()

        self.api_key.SetValue(config.ANTHROPIC_API_KEY)
        # make the list of models more readable for users:
        models_str = "\n".join([f"{key}:\t {value}" for key, value in config.ANTHROPIC_API_MODELS.items()])
        self.models.SetValue(models_str)
        self.host.SetValue(config.HOST)
        self.port.SetValue(config.PORT)

    def OnSave(self, event):
        settings_filename = config.APP_SETTINGS_LOCATION
        try:
            with open(settings_filename, 'r') as json_file:
                settings = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            # initialize settings if file is missing or corrupted
            settings = {}

        # update settings with values from GUI elements
        settings['api_key'] = self.api_key.GetValue()
        settings['host'] = self.host.GetValue()
        settings['port'] = self.port.GetValue()

        # save the updated settings back to the JSON file
        with open(settings_filename, 'w') as json_file:
            json.dump(settings, json_file, indent=4)

        self.Destroy()
    
    def OnRestart(self, event):
        global SERVER_PROCESS
        settings_filename = config.APP_SETTINGS_LOCATION

        try:
            with open(settings_filename, 'r') as json_file:
                settings = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            # initialize settings if file is missing or corrupted
            settings = {}

        settings['api_key'] = self.api_key.GetValue()
        settings['host'] = self.host.GetValue()
        settings['port'] = self.port.GetValue()

        with open(settings_filename, 'w') as json_file:
            json.dump(settings, json_file, indent=4)

        stop_server()
        aidetour_utilities.load_settings()
        start_server()

        self.Destroy()
    
    def OnClose(self, event):
        self.Destroy()


class ChatLogDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(ChatLogDialog, self).__init__(parent, title=title, size=(720, 400), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.log_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        # font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        font = wx.Font(16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.log_text.SetFont(font)
        vbox.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 10)
        
        done_button = wx.Button(panel, label="Done")
        done_button.Bind(wx.EVT_BUTTON, self.OnDone)
        vbox.Add(done_button, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        panel.SetSizer(vbox)
        
        self.load_chat_log()
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    
    def load_chat_log(self):
        # get the name of the CHAT_LOG file via an api call:
        try:
            url = f"http://{config.HOST}:{config.PORT}/v1/chat_log"
            timeout_config = (1, 1)  # connection and read timeouts
            reqSess = requests.Session()
            reqSess.mount('http://', requests.adapters.HTTPAdapter(max_retries=0))
            response = reqSess.get(url, timeout=timeout_config)
            # response.raise_for_status()  # raise an exception for 4xx or 5xx status codes
            chat_data = response.json()
            chat_log = chat_data['chat_log']
            logger.info(f"load_chat_log(self): chat_log={chat_log}")
        except Exception as e:
            logger.info(f"load_chat_log(self): Error occurred while parsing the API response:\n\"{e}\"")
        finally:
            response = None
            reqSess.close()

        if chat_log is None or not isinstance(chat_log, (str, bytes, os.PathLike)):
            logger.info(f"load_chat_log(self): No chat activity found in: {chat_log}")
            self.log_text.SetValue(f"No chat activity found in: {chat_log}")
        else:
            try:
                with open(chat_log, "r") as file:
                    logs = file.read()
                    self.log_text.SetValue(logs)
            except FileNotFoundError:
                logger.info(f"load_logs(self): except FileNotFoundError")
                self.log_text.SetValue(f"{chat_log} file not found.")
            except Exception as e:
                logger.info(f"load_logs(self): except Exception as e:\n{str(e)}")
                self.log_text.SetValue(f"Error loading log file: {str(e)}")

    def OnClose(self, event):
        self.Destroy()
    
    def OnDone(self, event):
        self.Destroy()


class LogsDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(LogsDialog, self).__init__(parent, title=title, size=(720, 400), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.log_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
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
        app_log = aidetour_utilities.prepend_log_dir(config.APP_LOG)
        try:
            with open(app_log, "r") as file:
                logs = file.read()
                self.log_text.SetValue(logs)
        except FileNotFoundError:
            logger.info(f"load_logs(self): except FileNotFoundError")
            self.log_text.SetValue(f"{app_log} file not found.")
        except Exception as e:
            logger.info(f"load_logs(self): except Exception as e:\n{str(e)}")
            self.log_text.SetValue(f"Error loading log file: {str(e)}")

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

        # layout for buttons using a horizontal box sizer
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_sizer.Add(self.btn_youtube, 0, wx.ALL, 5)
        self.button_sizer.AddSpacer(60)
        self.button_sizer.Add(self.btn_done, 0, wx.ALL, 5)

        # main sizer for the dialog, including the webview and the button sizer
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

        global SERVER_PROCESS, APP_STATUS_MESSAGES
        APP_STATUS_MESSAGES = ""
        SERVER_PROCESS = None

        # to check port in use or back ip use:
        #   python -m http.server 5600 --bind 127.0.0.1
        # 
        # Mac = show listening ports:
        #   lsof -iTCP -sTCP:LISTEN -P -n
        #   kill 123
        # 
        # Windows = show listening ports:
        #   netstat -aon | findstr LISTENING | findstr "127.0.0.1 0.0.0.0"
        #   taskkill /F /PID 123

        if aidetour_utilities.is_port_in_use(config.HOST, config.PORT):
            self.app_warning()
        else:
            # this sets SERVER_PROCESS, so it can be terminated if needed:
            start_server()
            logger.info(f"MenuStuff: start_server(): SERVER_PROCESS={SERVER_PROCESS}")

        if SERVER_PROCESS is None:
            APP_STATUS_MESSAGES += "\nError starting the API Server.\n"
            APP_STATUS_MESSAGES += f"Attempted start of local server on: {config.HOST}:{config.PORT}\n"
            APP_STATUS_MESSAGES += "Please click on Settings in the menu to change."
            APP_STATUS_MESSAGES += "\n________________________________________\n"

        # these 'state control attributes' are used to avoid multiple popups of the same dialog box:
        self.status_dialog   = None
        self.settings_dialog = None
        self.chat_log_dialog     = None
        self.logs_dialog     = None
        self.video_dialog    = None
        self.Bind(wx.EVT_MENU, self.OnStatus,   id=1)
        self.Bind(wx.EVT_MENU, self.OnSettings, id=2)
        self.Bind(wx.EVT_MENU, self.OnChatLog,  id=3)
        self.Bind(wx.EVT_MENU, self.OnLogs,     id=4)
        self.Bind(wx.EVT_MENU, self.OnVideo,    id=5)
        self.Bind(wx.EVT_MENU, self.OnExit,     id=6)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(1, 'Status')
        menu.Append(2, 'Settings')
        menu.Append(3, 'Chat log')
        menu.Append(4, 'Logs')
        menu.Append(5, 'About')
        menu.Append(6, 'Exit')
        return menu

    def set_icon(self, icon_path):
        try:
            icon = wx.Icon(icon_path, wx.BITMAP_TYPE_PNG)
            self.SetIcon(icon, config.APP_NAME)
        except Exception as e:
            logger.info(f"ERROR: setting icon:\n\"{e}\"")

    def on_left_down(self, event):
        pass

    def OnStatus(self, event):
        global APP_STATUS_MESSAGES
        url = f"http://{config.HOST}:{config.PORT}/v1/ping"
        reqSess = requests.Session()
        reqSess.mount('http://', requests.adapters.HTTPAdapter(max_retries=0))
        try:
            self.set_icon("Aidetour_red.png")
            # a "ping" GET request to a local server will be fast, 
            # so only wait for 1 second with no retries:
            response = reqSess.get(url, timeout=1)
            self.server_status = response.ok
            if self.server_status:
                APP_STATUS_MESSAGES += f"Ping to http://{config.HOST}:{config.PORT}/v1/ping was successful;\nstatus code of {response.status_code}. The server is \"go at throttle up\"!"
                logger.info(APP_STATUS_MESSAGES)
                APP_STATUS_MESSAGES += "\n________________________________________\n"
                self.set_icon("Aidetour_green.png")
        except Exception as e:
            APP_STATUS_MESSAGES += "\nError: API Server is not running:\n"
            APP_STATUS_MESSAGES += f"Pinging "
            APP_STATUS_MESSAGES += f"http://{config.HOST}:{config.PORT}/v1/ping failed. \"I'm sorry, Dave, I can't do that\"!\n"
            APP_STATUS_MESSAGES += f"Exception as e:\n{e}"
            APP_STATUS_MESSAGES += "\nPlease click on Settings in the menu to change."
            logger.info(APP_STATUS_MESSAGES)
            APP_STATUS_MESSAGES += "\n________________________________________\n"
            self.set_icon("Aidetour_red.png")
        finally:
            response = None
            reqSess.close()

        if not self.status_dialog or not self.status_dialog.IsShown():
            self.status_dialog = StatusDialog(None, f"{config.APP_NAME} Status Messages", APP_STATUS_MESSAGES)
            self.status_dialog.Show()
            self.status_dialog.Raise() # give it the focus

    def OnSettings(self, event):
        if not self.settings_dialog or not self.settings_dialog.IsShown():
            self.settings_dialog = SettingsDialog(None, f"{config.APP_NAME} Settings")
            self.settings_dialog.Show()
            self.settings_dialog.Raise() # give it the focus
            self.set_icon("Aidetour.png")

    def OnChatLog(self, event):
        if not self.chat_log_dialog or not self.chat_log_dialog.IsShown():
            self.chat_log_dialog = ChatLogDialog(None, f"{config.APP_NAME} Chat Log")
            self.chat_log_dialog.Show()
            self.chat_log_dialog.Raise() # give it the focus

    def OnLogs(self, event):
        if not self.logs_dialog or not self.logs_dialog.IsShown():
            self.logs_dialog = LogsDialog(None, f"{config.APP_NAME} Logs")
            self.logs_dialog.Show()
            self.logs_dialog.Raise() # give it the focus

    def OnVideo(self, event):
        if not self.video_dialog or not self.video_dialog.IsShown():
            video_id = "J7tab9JwbaI?si=sbmaZr6eeLGGjfq_"
            self.video_dialog = YouTubeDialog(None, video_id)
            self.video_dialog.Show()
            self.video_dialog.Raise() # give it the focus

    def OnExit(self, event=None):
        url = f"http://{config.HOST}:{config.PORT}/v1/shutdown"
        # not needed, plus appears in wrong place in log:
        # logger.info(f"Shutdown server at {url}")
        try:
            global SERVER_PROCESS
            if SERVER_PROCESS:
                stop_server()
                SERVER_PROCESS = None
            timeout_config = (1, 1)  # connection and read timeouts
            reqSess = requests.Session()
            reqSess.mount('http://', requests.adapters.HTTPAdapter(max_retries=0))
            response = reqSess.get(url, timeout=timeout_config)
        except Exception as e:
            # ok, the user wants out (exit/quit/whatever) so let them be free,
            # even though the api server may or may not have shutdown
            pass
        finally:
            response = None
            reqSess.close()

        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            self.tray_icon.RemoveIcon()
            self.tray_icon.Destroy()
            self.tray_icon = None

        if hasattr(self, 'frame') and self.frame is not None:
            self.frame.Destroy()
            self.frame = None

        wx.GetApp().ExitMainLoop()

    def app_warning(self):
        logger.info(f"ERROR: http://{config.HOST}:{config.PORT} is already in use!")
        message = f"ERROR: \n\nhttp://{config.HOST}:{config.PORT} \n\n...is already in use!\n\nPlease click on Settings in the menu to change."
        dialog = SplitImageDialog(None, 
                                  config.APP_NAME, 
                                  message, 
                                  aidetour_utilities.resource_path(config.APP_LOGO),
                                  button_label="Exit")
        dialog.ShowModal()
        dialog.Destroy()


class GuiStuff(wx.App):
    def OnInit(self):
        frame = wx.Frame(wx.Frame(None, size=(0, 0)))  # ensure it's properly hidden
        self.SetTopWindow(frame)
        MenuStuff(frame)
        return True

