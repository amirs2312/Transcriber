import wx
from wx.lib.filebrowsebutton import FileBrowseButton
from wx.lib.buttons import GenButton
from spleeter.separator import Separator
import os
from basic_pitch.inference import predict_and_save
from music21 import converter
import pygame
from UI import CustomButton
import shutil


#PyQt5 was throwing a tantrum so I switched frameworks.

class PianoExtractorApp(wx.Frame):
    def __init__(self, parent, title):
        super(PianoExtractorApp, self).__init__(parent, title=title, size=(600, 700))

        dark_background_color = wx.Colour(24, 24, 24)  # A dark gray, almost black
        greenish_button_color = wx.Colour(30, 215, 96)  # Spotify green
        white_text_color = wx.Colour(255, 255, 255)


        # Creating a panel which will contain all the widgets (buttons, labels etc.)
        panel = wx.Panel(self)
        panel.SetBackgroundColour(dark_background_color)

        # Setting a vertical box sizer to manage layout of the widgets vertically
        vbox = wx.BoxSizer(wx.VERTICAL)

        logo_path = "Assets/transcriber-logo.png"  # Path to your logo file
        logo_image = wx.Image(logo_path, wx.BITMAP_TYPE_PNG).Rescale(600, 120)  # Resize the logo to fit
        logo_bitmap = wx.StaticBitmap(panel, -1, wx.Bitmap(logo_image))
        vbox.Add(logo_bitmap, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.BOTTOM, 10)

        
        # File browsing button to select MP3 files
        self.fileBrowseBtn = FileBrowseButton(panel, labelText="Select MP3 File:", fileMask="*.mp3",style=wx.BORDER_NONE)
       
        vbox.Add(self.fileBrowseBtn, 0, wx.EXPAND | wx.ALL, 20) # Increased border space to 20



        # Button that activates spleeters processing function 
        self.processBtn = CustomButton(panel, label="Extract Piano", size=(200, 50)) # Set button size to 200x50
        
        
        # "Binds" Button click event to the processing function
        self.processBtn.Bind(wx.EVT_BUTTON, self.process_with_spleeter)
        vbox.Add(self.processBtn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        vbox.AddSpacer(10)




        # Button to close the application
        self.quitBtn = CustomButton(panel, label="Quit",size=(200, 50))
        
        # Bind to the quit function
        self.quitBtn.Bind(wx.EVT_BUTTON, self.quit_application)  
        vbox.Add(self.quitBtn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        vbox.AddSpacer(10)
        

        self.infoLabel = wx.StaticText(panel, label="No file selected.")
        vbox.Add(self.infoLabel, 0, wx.EXPAND | wx.ALL, 30)

        # Add a Play/Pause button after your existing widgets
        self.playbackLabel = wx.StaticText(panel, label="Playing: Original File")
        vbox.Add(self.playbackLabel, 0, wx.EXPAND | wx.ALL, 10) 
        
        # Determines which of the files gets played.
        self.playbackState = 'original' 

        self.playPauseBtn = CustomButton(panel, label="▶",size=(200, 50))
        
        self.playPauseBtn.Bind(wx.EVT_BUTTON, self.toggle_playback)
        self.playPauseBtn.Bind(wx.EVT_RIGHT_DOWN, self.toggle_playback_state)
        vbox.Add(self.playPauseBtn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        vbox.AddSpacer(10)

        # Add an attribute to keep track of playback state
        self.isPlaying = False

        panel.SetSizer(vbox)

        self.volumeLabel = wx.StaticText(panel, label="Volume")
        vbox.Add(self.volumeLabel, 0, wx.EXPAND | wx.ALL, 10)

        self.volumeSlider = wx.Slider(panel, value=100, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        vbox.Add(self.volumeSlider, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        vbox.AddSpacer(10)
        self.volumeSlider.Bind(wx.EVT_SLIDER, self.on_volume_change)
        pygame.mixer.init()






    def clear_directory(self, directory_path):
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")


    
    def on_volume_change(self, event):
        # Convert slider value to a float between 0 and 1 for pygame
        volume = self.volumeSlider.GetValue() / 100.0
        pygame.mixer.music.set_volume(volume)


    def toggle_playback_state(self, event):
        if self.playbackState == 'original':
            self.playbackState = 'piano'
            self.playbackLabel.SetLabel("Playing: Extracted Piano")
        elif self.playbackState == 'piano':
            self.playbackState = 'original'
            self.playbackLabel.SetLabel("Playing: Original File")

        self.Refresh()  # Redraw the interface to reflect the updated label


    

    def toggle_playback(self, event):
        selected_file = None

        if self.playbackState == 'original':
            selected_file = self.fileBrowseBtn.GetValue()

        elif self.playbackState == 'piano':
            output_directory = os.path.join('OutputPiano', os.path.splitext(os.path.basename(self.fileBrowseBtn.GetValue()))[0])
            selected_file = os.path.join(output_directory, 'piano.wav')


        if not self.isPlaying:  # Play the file
            if selected_file and os.path.exists(selected_file):
                pygame.mixer.init()
                pygame.mixer.music.load(selected_file)
                pygame.mixer.music.play()
                self.isPlaying = True
                self.playPauseBtn.SetLabel("⏸")
            else:
                self.infoLabel.SetLabel("Please select a valid file first.")
        else:  # Pause or unpause the playback
            if self.playbackState == 'midi' and pygame.mixer.music.get_pos() > 0:  # Check if the MIDI file is already playing
                pygame.mixer.music.unpause()  # Resume the MIDI playback
            else:
                pygame.mixer.music.pause()  # Pause the MIDI playback
            self.isPlaying = not self.isPlaying
            self.playPauseBtn.SetLabel("▶" if not self.isPlaying else "⏸")



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

        self.clear_directory('OutputPiano')
        self.clear_directory('OutputMIDI')
        self.clear_directory('OutputPDF')
    

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