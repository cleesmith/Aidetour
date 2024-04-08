import wx
import subprocess
import time
import sys

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Server Control')
        self.server_process = None
        self.host = '127.0.0.1'
        self.port = 5600
        self.api_key = 'your_api_key'
        self.server_status = 'status'
        self.init_ui()

    def init_ui(self):
        menubar = wx.MenuBar()
        server_menu = wx.Menu()

        start_item = server_menu.Append(wx.ID_ANY, 'Start Server')
        self.Bind(wx.EVT_MENU, self.on_start_server, start_item)

        stop_item = server_menu.Append(wx.ID_ANY, 'Stop Server')
        self.Bind(wx.EVT_MENU, self.on_stop_server, stop_item)

        restart_item = server_menu.Append(wx.ID_ANY, 'Restart Server')
        self.Bind(wx.EVT_MENU, self.on_restart_server, restart_item)

        menubar.Append(server_menu, '&Server')
        self.SetMenuBar(menubar)

    def on_start_server(self, event):
        if not self.server_process:
            self.server_process = self.start_server()

    def on_stop_server(self, event):
        if self.server_process:
            self.stop_server(self.server_process)
            self.server_process = None

    def on_restart_server(self, event):
        if self.server_process:
            self.server_process = self.restart_server(self.server_process)

    def start_server(self):
        server_process = subprocess.Popen(['python', 'run_server.py',
                                           self.host, str(self.port), self.api_key, self.server_status])
        print(f"Server started on {self.host}:{self.port}")
        return server_process

    def stop_server(self, server_process):
        if sys.platform == 'win32':
            server_process.terminate()
        else:
            server_process.terminate()
            server_process.wait()
        print("Server stopped.")

    def restart_server(self, server_process):
        self.stop_server(server_process)
        time.sleep(1)
        new_server_process = self.start_server()
        return new_server_process

if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()

