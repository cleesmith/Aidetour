import shelve
import wx
from wx.adv import TaskBarIcon as TaskBarIcon
import wx.adv
import wx.html2
import webbrowser


class SettingsDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(SettingsDialog, self).__init__(parent, 
            title=title, 
            size=(350, 440))
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.api_key = wx.TextCtrl(panel, -1, style=wx.TE_PROCESS_ENTER, size=(200, -1))
        self.host = wx.TextCtrl(panel, -1, style=wx.TE_PROCESS_ENTER, size=(200, -1))
        self.port = wx.TextCtrl(panel, -1, style=wx.TE_PROCESS_ENTER, size=(200, -1))
        self.models = wx.TextCtrl(panel, 
            pos=(10, 10), 
            size=(300, 120), 
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        
        vbox.AddSpacer(20)
        vbox.Add(wx.StaticText(panel, -1, 'Anthropic API Key:'), flag=wx.LEFT|wx.TOP, border=10)
        vbox.Add(self.api_key, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        vbox.AddSpacer(10)
        vbox.Add(wx.StaticText(panel, -1, 'Host:'), flag=wx.LEFT|wx.TOP, border=10)
        vbox.Add(self.host, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        vbox.AddSpacer(10)
        vbox.Add(wx.StaticText(panel, -1, 'Port:'), flag=wx.LEFT|wx.TOP, border=10)
        vbox.Add(self.port, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)
        vbox.AddSpacer(10)
        vbox.Add(wx.StaticText(panel, -1, 'Claude 3 models'), flag=wx.CENTER|wx.LEFT|wx.TOP, border=10)
        vbox.Add(self.models, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)

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

        self.load_settings()
    
    def load_settings(self):
        settings = shelve.open('Aidetour_Settings')
        self.api_key.SetValue(settings.get('api_key', ''))
        self.host.SetValue(settings.get('host', ''))
        self.port.SetValue(str(settings.get('port', '')))
        models_dict = settings['Claude']
        models_str = "The list of available Claude models \nmay not be changed or edited.\n\n"
        models_str += "\n".join([f"{key}:\t {value}" for key, value in models_dict.items()])
        self.models.SetValue(models_str)
        settings.close()
    
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
        # Clear the textbox
        self.textbox.Clear()

        # Add each model to the textbox on a new line
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
            with open("Aidetour.log", "r") as file:
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
        self.SetIcon(wx.Icon('Aidetour.png', wx.BITMAP_TYPE_PNG), 'Aidetour')
        self.Bind(wx.EVT_MENU, self.OnSettings, id=1)
        self.Bind(wx.EVT_MENU, self.OnLogs,     id=2)
        self.Bind(wx.EVT_MENU, self.OnVideo,    id=3)
        self.Bind(wx.EVT_MENU, self.OnExit,     id=4)
    
    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(1, 'Settings')
        menu.Append(2, 'Log')
        menu.Append(3, 'Video')
        menu.Append(4, 'Exit')
        return menu

    def OnExit(self, event):
        wx.CallAfter(self.Destroy)
        wx.Exit()  # Exit the application
    
    def OnSettings(self, event):
        # Open the settings dialog non-modally
        dlg = SettingsDialog(None, "Aidetour Settings")
        dlg.Show()
    
    def OnLogs(self, event):
        # Open the logs dialog non-modally
        dlg = LogsDialog(None, "Aidetour Log")
        dlg.Show()
    
    def OnVideo(self, event):
        # video_id = "Seu8KkqBY1k?si=hqK9lKTbT6xYf3HX"
        video_id = "-oPYGeAdgFI?si=RXHxkWUfzsxh5aYr"
        dlg = YouTubeDialog(None, video_id)
        dlg.Show()


class MyApp(wx.App):
    def OnInit(self):
        self.SetTopWindow(wx.Frame(None, size=(0, 0)))  # Ensure it's properly hidden
        MyTaskBarIcon()  # Just initialize the task bar icon
        return True


app = MyApp(False)
app.MainLoop()
