import wx
import wx.adv
import wx.html2
import webbrowser

class YouTubeDialog(wx.Dialog):
    def __init__(self, parent, video_id):
        super().__init__(parent, 
            title="YouTube Video", 
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        panel = wx.Panel(self)

        self.webview = wx.html2.WebView.New(panel)

        video_url = f"https://www.youtube.com/embed/{video_id}"
        self.webview.LoadURL(video_url)

        video_link = f"https://www.youtube.com/watch?v={video_id}"
        hyperlink = wx.adv.HyperlinkCtrl(panel, wx.ID_ANY, label="View on YouTube", url=video_link)
        # hyperlink = wx.adv.HyperlinkCtrl(panel, wx.ID_ANY, "OpenAI", url="https://www.openai.com")
        hyperlink.SetNormalColour(wx.Colour('WHITE'))
        hyperlink.SetHoverColour(wx.Colour('GREEN'))

        hyperlink.Bind(wx.adv.EVT_HYPERLINK, self.on_hyperlink)

        done_button = wx.Button(panel, label="Done")
        done_button.Bind(wx.EVT_BUTTON, self.on_done)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.webview, 1, wx.EXPAND)
        sizer.Add(hyperlink, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        sizer.Add(done_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        panel.SetSizer(sizer)
        self.SetSize((640, 400))  # Increased height to accommodate the hyperlink

        self.CenterOnScreen()

    def on_hyperlink(self, event):
        webbrowser.open(event.GetURL())

    def on_done(self, event):
        self.EndModal(wx.ID_OK)

if __name__ == "__main__":
    app = wx.App()
    video_id = "Seu8KkqBY1k?si=hqK9lKTbT6xYf3HX"
    dialog = YouTubeDialog(None, video_id)
    dialog.ShowModal()
    dialog.Destroy()
    app.MainLoop()

