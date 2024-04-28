import wx
from wx import svg
from wx.adv import TaskBarIcon as TaskBarIcon
import wx.adv
import requests

# import logging
# logging.basicConfig(
#     format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
#     level=logging.DEBUG
# )
# logging.basicConfig(level=logging.DEBUG)


class LogsDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(LogsDialog, self).__init__(parent, title=title, size=(720, 400), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
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
        
        self.load_logs()
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    
    def load_logs(self):
        try:
            with open('requirements.txt', "r") as file:
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


class MyTaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        super().__init__()
        self.frame = frame
        self.server_status = False
        self.set_icon("Aidetour.png")

        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        # self.ping_server()

    def CreatePopupMenu(self):
        menu = wx.Menu()
        status_item = menu.Append(wx.ID_ANY, "Status")
        menu.Append(wx.ID_ANY, "Settings")
        # menu.Append(wx.ID_ANY, "Chat log")
        logs_item = menu.Append(wx.ID_ANY, "Chat log")
        menu.Append(wx.ID_ANY, "About")
        exit_item = menu.Append(wx.ID_EXIT, "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_status, status_item)
        self.Bind(wx.EVT_MENU, self.on_logs, logs_item)
        return menu

    def set_icon(self, icon_path):
        try:
            icon = wx.Icon(icon_path, wx.BITMAP_TYPE_PNG)
            self.SetIcon(icon, "Aidetour")
        except Exception as e:
            print(f"Error setting icon: {e}")

    def on_left_down(self, event):
        print("menu clicked")

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        wx.Exit()

    def on_logs(self, event):
        self.logs_dialog = LogsDialog(None, f"spud Chat Log")
        self.logs_dialog.Show()
        self.logs_dialog.Raise() # give it the focus

    def on_status(self, event):
        self.ping_server()

    def ping_server(self):
        try:
            self.set_icon("status_down.png")
            reqSess = requests.Session()
            reqSess.mount('http://', requests.adapters.HTTPAdapter(max_retries=0))
            response = reqSess.get("http://127.0.0.1:5600/")
            # response = reqSess.get("http://127.0.0.1:5600/smuffin.html") # 404
            # response.raise_for_status()  # raise an exception for 4xx or 5xx status codes
            print(f"ping_server: response={response.ok}")
            self.server_status = response.ok
            if self.server_status:
                self.set_icon("status_up.png")
        except Exception as e:
            print(f"ping_server: an error occurred:\n\"{e}\"\n")
            self.set_icon("status_down.png")
        finally:
            response = None
            reqSess.close()

if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    frame.Show(False)
    icon = MyTaskBarIcon(frame)
    app.MainLoop()
