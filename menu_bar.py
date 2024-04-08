import wx
import threading
import time

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Waitress/Flask Server Control')
        panel = wx.Panel(self)

        # Create a menu bar
        menubar = wx.MenuBar()
        server_menu = wx.Menu()

        # Add menu items
        self.start_item = server_menu.Append(wx.ID_ANY, 'Start Server')
        self.stop_item = server_menu.Append(wx.ID_ANY, 'Stop Server')
        self.restart_item = server_menu.Append(wx.ID_ANY, 'Restart Server')
        server_menu.AppendSeparator()
        self.logs_item = server_menu.Append(wx.ID_ANY, 'Logs')

        # Bind menu events
        self.Bind(wx.EVT_MENU, self.on_start, self.start_item)
        self.Bind(wx.EVT_MENU, self.on_stop, self.stop_item)
        self.Bind(wx.EVT_MENU, self.on_restart, self.restart_item)
        self.Bind(wx.EVT_MENU, self.on_logs, self.logs_item)

        menubar.Append(server_menu, '&Server')
        self.SetMenuBar(menubar)

        self.server_status = {'running': False}
        self.flask_thread = None

    def start_server(self):
        self.server_status['running'] = True
        self.flask_thread = threading.Thread(target=aidetour_api_handler.run_flask_app,
                                             args=(self.host, self.port, self.api_key, self.server_status),
                                             daemon=True)
        self.flask_thread.start()

    def stop_server(self):
        # Send a shutdown request to the server
        response = requests.post(f'http://{self.host}:{self.port}/v1/shutdown')
        if response.status_code == 200:
            while self.server_status['running']:
                time.sleep(1)  # Wait for the server to stop running
            self.flask_thread = None
            print("Flask server has stopped")
        else:
            print(f"Failed to stop the server. Status code: {response.status_code}")

    def on_start(self, event):
        if not self.server_status['running']:
            self.start_server()
            print("Flask server started")

    def on_stop(self, event):
        if self.server_status['running']:
            self.stop_server()

    def on_restart(self, event):
        if self.server_status['running']:
            self.stop_server()
        self.start_server()
        print("Flask server restarted")

    def on_logs(self, event):
        # Implement the logic to display logs
        print("Displaying logs...")

if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()

