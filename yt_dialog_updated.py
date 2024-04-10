# import wx
# import wx.adv
# import wx.html2
# import webbrowser

# class YouTubeDialog(wx.Dialog):
#     def __init__(self, parent, video_id):
#         super().__init__(parent, 
#             title="YouTube Video", 
#             style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
#         self.panel = wx.Panel(self)

#         self.webview = wx.html2.WebView.New(self.panel)
#         video_url = f"https://www.youtube.com/embed/{video_id}"
#         self.webview.LoadURL(video_url)

#         self.btn_youtube = wx.Button(self.panel, label="Open on YouTube")
#         self.btn_youtube.Bind(wx.EVT_BUTTON, self.on_youtube_click)
#         self.btn_youtube.SetMinSize((120, 50))  # Set minimum size to make the button "fatter"

#         self.btn_done = wx.Button(self.panel, label="Done")
#         self.btn_done.Bind(wx.EVT_BUTTON, self.on_done_click)
#         self.btn_done.SetMinSize((120, 50))  # Set minimum size to make the button "fatter"

#         # Layout for buttons using a horizontal box sizer
#         self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
#         self.button_sizer.Add(self.btn_youtube, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
#         self.button_sizer.Add(self.btn_done, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)

#         # Main sizer for the dialog, including the webview and the button sizer
#         self.main_sizer = wx.BoxSizer(wx.VERTICAL)
#         self.main_sizer.Add(self.webview, 1, wx.EXPAND | wx.ALL, 5)
#         self.main_sizer.Add(self.button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)

#         self.panel.SetSizer(self.main_sizer)
#         self.SetSize((600, 400))

#     def on_youtube_click(self, event):
#         # Open the YouTube video in the default web browser
#         webbrowser.open(f"https://www.youtube.com/watch?v={video_id}")

#     def on_done_click(self, event):
#         # Close the dialog
#         self.Close()


import wx
import wx.adv
import wx.html2
import webbrowser

class YouTubeDialog(wx.Dialog):
    def __init__(self, parent, video_id):
        super().__init__(parent, 
            title="YouTube Video", 
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.panel = wx.Panel(self)

        self.webview = wx.html2.WebView.New(self.panel)
        video_url = f"https://www.youtube.com/embed/{video_id}"
        self.webview.LoadURL(video_url)

        self.btn_youtube = wx.Button(self.panel, label="Open on YouTube")
        self.btn_youtube.Bind(wx.EVT_BUTTON, self.on_youtube_click)

        self.btn_done = wx.Button(self.panel, label="Done")
        self.btn_done.Bind(wx.EVT_BUTTON, self.on_done_click)

        # Layout for buttons using a horizontal box sizer
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_sizer.Add(self.btn_youtube, 0, wx.ALL, 10)
        self.button_sizer.Add(self.btn_done, 0, wx.ALL, 10)

        # Main sizer for the dialog, including the webview and the button sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.webview, 1, wx.EXPAND | wx.ALL, 12)
        self.main_sizer.Add(self.button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 12)

        self.panel.SetSizer(self.main_sizer)
        self.SetSize((600, 400))

    def on_youtube_click(self, event):
        webbrowser.open(f"https://www.youtube.com/watch?v={video_id}")

    def on_done_click(self, event):
        self.Close()


if __name__ == "__main__":
    app = wx.App(False)
    video_id = "Seu8KkqBY1k?si=hqK9lKTbT6xYf3HX"
    dlg = YouTubeDialog(None, video_id)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()
