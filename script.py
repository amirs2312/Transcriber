import wx
from wx.lib.filebrowsebutton import FileBrowseButton
from spleeter.separator import Separator
import os

#PyQt5 was throwing a tantrum so we switched frameworks.

class PianoExtractorApp(wx.Frame):
    def __init__(self, parent, title):
        super(PianoExtractorApp, self).__init__(parent, title=title, size=(400, 200))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.fileBrowseBtn = FileBrowseButton(panel, labelText="Select MP3 File:", fileMask="*.mp3")
        vbox.Add(self.fileBrowseBtn, 0, wx.EXPAND | wx.ALL, 10)

        self.processBtn = wx.Button(panel, label="Extract Piano")
        self.processBtn.Bind(wx.EVT_BUTTON, self.process_with_spleeter)
        vbox.Add(self.processBtn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        self.infoLabel = wx.StaticText(panel, label="No file selected.")
        vbox.Add(self.infoLabel, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(vbox)

    def process_with_spleeter(self, event):
        filepath = self.fileBrowseBtn.GetValue()
        if filepath:
            separator = Separator('spleeter:5stems')
            separator.separate_to_file(filepath, 'OutputPiano')

            # Cleaning up (keeping only the piano.wav and deleting other files)
            output_directory = os.path.join('OutputPiano', os.path.splitext(os.path.basename(filepath))[0])
            for filename in os.listdir(output_directory):
                if filename != 'piano.wav':
                    os.remove(os.path.join(output_directory, filename))

            self.infoLabel.SetLabel(f"Piano track saved in {output_directory}/piano.wav")
        else:
            self.infoLabel.SetLabel("Please select a file first.")

if __name__ == "__main__":
    app = wx.App(False)
    frame = PianoExtractorApp(None, "Piano Extractor")
    frame.Show(True)
    app.MainLoop()