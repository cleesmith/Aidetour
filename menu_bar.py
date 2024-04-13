import shelve
from loguru import logger
import wx
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

class SettingsDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(SettingsDialog, self).__init__(parent, 
            title=title, 
            size=(350, 480))
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.host = wx.TextCtrl(panel, -1, style=wx.TE_PROCESS_ENTER, size=(200, -1))
        self.port = wx.TextCtrl(panel, -1, style=wx.TE_PROCESS_ENTER, size=(200, -1))
        self.api_key = wx.TextCtrl(panel, -1, style=wx.TE_PROCESS_ENTER, size=(200, -1))
        self.models = wx.TextCtrl(panel, 
            pos=(10, 10), 
            size=(300, 120), 
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        self.models.SetBackgroundColour("DARK GRAY")
        self.models.SetForegroundColour("WHEAT")
        
        vbox.AddSpacer(5)

        label00 = wx.StaticText(panel, -1, 'Your Local API Server', style=wx.ALIGN_CENTER)
        label00.SetForegroundColour('SEA GREEN')
        font = wx.Font(16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        label00.SetFont(font)
        vbox.Add(label00, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        vbox.AddSpacer(2)

        # label0 = wx.StaticText(panel, -1, 
        #     '"speaks like Sam; thinks like Claude"',
        #     style=wx.ALIGN_CENTER)
        # label0.SetForegroundColour('WHEAT')
        # font = wx.Font(12, wx.FONTFAMILY_SCRIPT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 
        #     faceName="Comic Sans MS")
        # label0.SetFont(font)
        # vbox.Add(label0, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        # vbox.AddSpacer(3)

        label1 = wx.StaticText(panel, -1, 'Host:', style=wx.LEFT)
        label1.SetForegroundColour('SEA GREEN')
        font = wx.Font(16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        label1.SetFont(font)
        vbox.Add(label1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(self.host, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        vbox.AddSpacer(10)

        label2 = wx.StaticText(panel, -1, 'Port:', style=wx.LEFT)
        label2.SetForegroundColour('SEA GREEN')
        font = wx.Font(16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        label2.SetFont(font)
        vbox.Add(label2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        vbox.Add(self.port, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        vbox.AddSpacer(10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((10, -1), proportion=0)  # Left margin, adjust '20' as needed for indentation
        line = wx.Panel(panel, -1, size=(330, 2))  # Adjust '100' to required width, '2' for height
        line.SetBackgroundColour('SIENNA')
        hbox.Add(line, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)
        hbox.Add((20, -1), proportion=0)  # Right margin, adjust '20' as needed
        vbox.Add(hbox, proportion=0, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=10)
        vbox.AddSpacer(10)

        label3 = wx.StaticText(panel, -1, 'Your Anthropic API Key:', style=wx.LEFT)
        label3.SetForegroundColour('FIREBRICK')
        font = wx.Font(20, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_EXTRABOLD)
        label3.SetFont(font)
        vbox.Add(label3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        vbox.AddSpacer(5)
        vbox.Add(self.api_key, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        vbox.AddSpacer(20)

        label4 = wx.StaticText(panel, -1, 'Claude 3 models', style=wx.ALIGN_CENTER)
        label4.SetForegroundColour('WHEAT')
        font = wx.Font(16, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        label4.SetFont(font)
        vbox.Add(label4, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        vbox.AddSpacer(5)
        vbox.Add(self.models, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)

        # bottom row of buttons:
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(panel, label='Ok')
        hbox.Add(okButton)
        restartButton = wx.Button(panel, label='Restart Server')
        hbox.Add(restartButton, flag=wx.LEFT, border=15)
        closeButton = wx.Button(panel, label='Cancel')
        hbox.Add(closeButton, flag=wx.LEFT, border=15)
        vbox.AddSpacer(20)
        vbox.Add(hbox, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=5)
        panel.SetSizer(vbox)
        self.Bind(wx.EVT_BUTTON, self.OnSave, okButton)
        self.Bind(wx.EVT_BUTTON, self.OnRestart, restartButton)
        self.Bind(wx.EVT_BUTTON, self.OnClose, closeButton)
        vbox.AddSpacer(50)

        self.load_settings_for_dialog()
    
    def load_settings_for_dialog(self):
        aidetour_utilities.load_settings()
        self.api_key.SetValue(config.ANTHROPIC_API_KEY)
        models_str = "As of April 2024; this list may not be changed.\n\n"
        models_str += "\n".join([f"{key}:\t {value}" for key, value in config.ANTHROPIC_API_MODELS.items()])
        self.models.SetValue(models_str)
        self.host.SetValue(config.HOST)
        self.port.SetValue(config.PORT)
    
    def OnSave(self, event):
        settings = shelve.open('Aidetour_Settings')
        settings['api_key'] = self.api_key.GetValue()
        settings['host'] = self.host.GetValue()
        settings['port'] = int(self.port.GetValue())
        settings.close()
        self.Destroy()
    
    def OnRestart(self, event):
        pass
        # self.Destroy()
    
    def OnClose(self, event):
        self.Destroy()

    def display_models(self, models):
        self.textbox.Clear()
        for model in models:
            self.textbox.AppendText(model + '\n')


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


class MyTaskBarIcon(TaskBarIcon):
    def __init__(self):
        super(MyTaskBarIcon, self).__init__()
        self.SetIcon(wx.Icon(config.APP_LOGO, wx.BITMAP_TYPE_PNG), config.APP_NAME)
        # these 'state control attributes' are used to avoid multiple popups of the same dialog box:
        self.settings_dialog = None
        self.logs_dialog = None
        self.video_dialog = None
        self.Bind(wx.EVT_MENU, self.OnSettings, id=1)
        self.Bind(wx.EVT_MENU, self.OnLogs, id=2)
        self.Bind(wx.EVT_MENU, self.OnVideo, id=3)
        self.Bind(wx.EVT_MENU, self.OnExit, id=4)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(1, 'Settings')
        menu.Append(2, 'Log')
        menu.Append(3, 'Video')
        menu.Append(4, 'Exit')
        return menu

    def OnSettings(self, event):
        if not self.settings_dialog or not self.settings_dialog.IsShown():
            self.settings_dialog = SettingsDialog(None, "Aidetour Settings")
            self.settings_dialog.Show()

    def OnLogs(self, event):
        if not self.logs_dialog or not self.logs_dialog.IsShown():
            self.logs_dialog = LogsDialog(None, "Aidetour Log")
            self.logs_dialog.Show()

    def OnVideo(self, event):
        if not self.video_dialog or not self.video_dialog.IsShown():
            video_id = "-oPYGeAdgFI?si=RXHxkWUfzsxh5aYr"
            self.video_dialog = YouTubeDialog(None, video_id)
            self.video_dialog.Show()

    def OnExit(self, event):
        wx.CallAfter(self.Destroy)
        wx.Exit()


class MyApp(wx.App):
    def OnInit(self):
        self.SetTopWindow(wx.Frame(None, size=(0, 0)))  # Ensure it's properly hidden
        MyTaskBarIcon()
        return True

if __name__ == '__main__':

    # cls: only need these when running as: python -B menu_bar.py
    from aidetour_logging import setup_logger
    setup_logger(config.APP_LOG)
    logger.info(f"Starting {config.APP_NAME}...")

    aidetour_utilities.load_settings()

    app = MyApp(False)
    app.MainLoop()
