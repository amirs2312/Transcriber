import wx

class CustomButton(wx.Button):
    def __init__(self, *args, **kw):
        kw['style'] = wx.BORDER_NONE  # Add the border none style
        super(CustomButton, self).__init__(*args, **kw)
        
        self.SetBackgroundColour(wx.Colour(0,0,0,0))
        font = wx.Font(24, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_HEAVY, False, "Ariel")
        self.SetFont(font)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnPress)
        self.Bind(wx.EVT_LEFT_UP, self.OnRelease)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnHover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)


        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        
        self.pressed = False
        self.hovered = False

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        width, height = self.GetSize()

        base_color = wx.Colour(201,239,199)
        my_grey = wx.Colour(69,69,69,255)

        if self.pressed:
            dc.SetBrush(wx.Brush(base_color.ChangeLightness(60)))  # Slightly darker when pressed
        elif self.hovered:
            dc.SetBrush(wx.Brush(base_color.ChangeLightness(70)))  # Lightened up when hovered
        else:
            dc.SetBrush(wx.Brush(base_color))

        dc.SetPen(wx.Pen(base_color, 1))
        dc.DrawRoundedRectangle(0, 0, width, height, 5)  # Rounded Rectangle with 5 as the radius

        dc.SetTextForeground(my_grey) 

        dc.DrawLabel(self.GetLabel(), self.GetClientRect(), wx.ALIGN_CENTER)

        
        

    def OnPress(self, event):
        self.pressed = True
        self.Refresh()

    def OnRelease(self, event):
        self.pressed = False
        self.Refresh()

        # Generate EVT_BUTTON event
        new_event = wx.CommandEvent(wx.EVT_BUTTON.typeId, self.GetId())
        wx.PostEvent(self, new_event)

        event.Skip()


    def OnHover(self, event):
        self.hovered = True
        self.Refresh()

    def OnLeave(self, event):
        self.hovered = False
        self.Refresh()

    def OnEraseBackground(self, event):
        pass



