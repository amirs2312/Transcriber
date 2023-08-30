import wx
from wx.lib.filebrowsebutton import FileBrowseButton
from spleeter.separator import Separator
import os
from basic_pitch.inference import predict_and_save
from music21 import converter


#PyQt5 was throwing a tantrum so I switched frameworks.

class PianoExtractorApp(wx.Frame):
    def __init__(self, parent, title):
        super(PianoExtractorApp, self).__init__(parent, title=title, size=(400, 200))


        # Creating a panel which will contain all the widgets (buttons, labels etc.)
        panel = wx.Panel(self)

        # Setting a vertical box sizer to manage layout of the widgets vertically
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # File browsing button to select MP3 files
        self.fileBrowseBtn = FileBrowseButton(panel, labelText="Select MP3 File:", fileMask="*.mp3")
        vbox.Add(self.fileBrowseBtn, 0, wx.EXPAND | wx.ALL, 10)


        # Button that activates spleeters processing function 
        self.processBtn = wx.Button(panel, label="Extract Piano")
        # "Binds" Button click event to the processing function
        self.processBtn.Bind(wx.EVT_BUTTON, self.process_with_spleeter)
        vbox.Add(self.processBtn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)


        # Label that will show the save path (eventually)
        # self.savePathLabel = wx.StaticText(panel, label="Saved path: Not processed yet.")
        # vbox.Add(self.savePathLabel, 0, wx.EXPAND | wx.ALL, 10)


        # Button to close the application
        self.quitBtn = wx.Button(panel, label="Quit")
        # Bind to the quit function
        self.quitBtn.Bind(wx.EVT_BUTTON, self.quit_application)  
        vbox.Add(self.quitBtn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        self.infoLabel = wx.StaticText(panel, label="No file selected.")
        vbox.Add(self.infoLabel, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(vbox)




    #IM DEPRECATING MY OWN CODE


    #def midi_to_musicxml(self, midi_path):
     #   score = converter.parse(midi_path)
      #  musicxml_directory = "OutputXML"
      #  if not os.path.exists(musicxml_directory):
       #     os.makedirs(musicxml_directory)
       # musicxml_filename = os.path.splitext(os.path.basename(midi_path))[0] + ".xml"
        #musicxml_path = os.path.join(musicxml_directory, musicxml_filename)
        #score.write('musicxml', musicxml_path)
        #return musicxml_path
    



    def musicxml_to_pdf(self, musicxml_path):
        pdf_directory = "OutputPDF"
        if not os.path.exists(pdf_directory):
            os.makedirs(pdf_directory)
        output_pdf_path = os.path.join(pdf_directory, os.path.splitext(os.path.basename(musicxml_path))[0] + ".pdf")
        os.system(f'mscore "{musicxml_path}" -o "{output_pdf_path}"')
        return output_pdf_path
    

    def midi_to_pdf(self, midi_path):
        pdf_directory = "OutputPDF"
        if not os.path.exists(pdf_directory):
            os.makedirs(pdf_directory)
        output_pdf_path = os.path.join(pdf_directory, os.path.splitext(os.path.basename(midi_path))[0] + ".pdf")
        os.system(f'mscore "{midi_path}" -o "{output_pdf_path}"')
        return output_pdf_path
    



    def process_with_spleeter(self, event):
        # Get the file from the path listed by the browse files button
        filepath = self.fileBrowseBtn.GetValue()

        # If a filepath is selected
        if filepath:
            # Intialise spleeters 5 stem model
            separator = Separator('spleeter:5stems')
            # Leave the files in output directory
            separator.separate_to_file(filepath, 'OutputPiano')

            # Cleaning up (keeping only the piano.wav and deleting other files)
            output_directory = os.path.join('OutputPiano', os.path.splitext(os.path.basename(filepath))[0])
            for filename in os.listdir(output_directory):
                if filename != 'piano.wav':
                    os.remove(os.path.join(output_directory, filename))


            

               # Change this line to use "Output MIDI" folder in the same directory
            midi_output_directory = "OutputMIDI"
            os.makedirs(midi_output_directory, exist_ok=True)
            predict_and_save(
                [os.path.join(output_directory, 'piano.wav')],
                midi_output_directory,
                save_midi=True,
                sonify_midi=False, # set to True if you want .wav version of the MIDI
                save_model_outputs=False,
                save_notes=False # set to True if you want note events as CSV
            )

            midi_filename = "piano_basic_pitch.mid"
            midi_output_path = os.path.join(midi_output_directory, midi_filename)

            

            pdf_path = self.midi_to_pdf(midi_output_path)

            self.infoLabel.SetLabel(f"Piano track saved in {output_directory}/piano.wav\nMIDI saved in {midi_output_path}\nSheet music saved in {pdf_path}")




        else:
            self.infoLabel.SetLabel("Please select a file first.")


    # Self Explanatory
    def quit_application(self, event):
        self.Close()


# Creating the main app object
if __name__ == "__main__":

    # Creating an instance of our main window/frame and showing it 
    app = wx.App(False)
    frame = PianoExtractorApp(None, "Piano Extractor")
    frame.Show(True)

    # Setting the apps main event loop
    app.MainLoop()