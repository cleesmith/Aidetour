import sys
import wx

class ImageViewer(wx.Frame):
    def __init__(self, parent, title):
        super(ImageViewer, self).__init__(parent, title=title, size=(600, 650))
        try:
            self.SetUpUI()
            self.Centre()
            self.Show()
            # set a timer to close the window after ? milliseconds
            wx.CallLater(3000, self.Close)
        except Exception as e:
            sys.exit(0)

    def SetUpUI(self):
        panel = wx.Panel(self)
        try:
            image = wx.Image('Aidetour.png', wx.BITMAP_TYPE_PNG)
            image = image.Scale(512, 512, wx.IMAGE_QUALITY_HIGH)
            imageBitmap = wx.StaticBitmap(panel, wx.ID_ANY, wx.Bitmap(image))
            caption = wx.StaticText(panel, label=f"\"talks like Sam;  thinks like Claude\"")
            caption.SetFont(wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD))
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(imageBitmap, 1, wx.ALL | wx.CENTER, 5)
            sizer.Add((0, 0), 1, wx.EXPAND)  # add an expanding spacer
            sizer.Add(caption, 0, wx.ALL | wx.CENTER, 20)  # increase the border to 20 pixels
            panel.SetSizer(sizer)
            panel.Layout()
        except Exception:
            sys.exit(0)

class App(wx.App):
    def OnInit(self):
        try:
            frame = ImageViewer(None, "Aidetour")
            frame.Show(True)
            return True
        except Exception:
            sys.exit(0)

if __name__ == '__main__':
    # raise Exception(f"test exception")
    try:
        app = App()
        app.MainLoop()
    except Exception:
        sys.exit(0)
    finally:
        sys.exit(0)
