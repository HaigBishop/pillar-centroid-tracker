"""
Program: Pillar Centroid Tracker (Version 1.1.0)
Description:
- semi-automated tracking of pillar position across a series of images
- semi-automated conversion of pillar tracking data to force values 
- to be used alongside the elastomeric micropillar platform as described in:
    Tayagui et al., "An elastomeric micropillar platform for the study of protrusive forces in hyphal invasion", 
    Lab on a Chip, Vol. 17, No.21, pp. 3643-3653, 2017.
Author: Haig Bishop (hbi34@uclive.ac.nz)
Date: 14/01/2024
Version Description:
- fixed size of GUI elements on different dpi screens
"""

# Import os and sys
import os

# Stops debug messages - alsoprevents an error after .exe packaging
# os.environ["KIVY_NO_CONSOLELOG"] = "1"

# Import kivy and make sure that the version is at least 2.2.0
import kivy

kivy.require("2.2.0")

# Import config to adjust settings
from kivy.config import Config

# Set window size
Config.set("graphics", "width", "900")
Config.set("graphics", "height", "600")
# Set min window size
Config.set("graphics", "minimum_width", "750")
Config.set("graphics", "minimum_height", "500")
# Disable red dots from right-clicking
Config.set("input", "mouse", "mouse,multitouch_on_demand")

# Other kivy related imports
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.core.window import Keyboard
from kivy.uix.screenmanager import SlideTransition

# Import local modules
from pf1 import *
from fg1 import *
from fg2 import *
from ip1 import *
from ip2 import *
from ps1 import *
from ps2 import *
from layout_elements import *
from file_management import resource_path, class_resource_path

# Set background colour to grey
DARK_GREY = (32 / 255, 33 / 255, 35 / 255, 1)
Window.clearcolor = DARK_GREY

# Column headers and default plot titles
AUTO_COL_NAMES = {
    "time": "Time [seconds]",
    "x_pos": "x Position [µm]",
    "y_pos": "y Position [µm]",
    "t_for": "Total Force [µN]",
    "x_for": "x Force [µN]",
    "y_for": "y Force [µN]",
    "dfx": "DeltaFx [µN]",
    "dfy": "DeltaFy [µN]",
}
COL_NAMES = [
    "Frame number",
    "Time [seconds]",
    "x Position [pixels]",
    "y Position [pixels]",
    "x Position [µm]",
    "y Position [µm]",
    "Total Force [µN]",
    "x Force [µN]",
    "y Force [µN]",
    "DeltaFx [µN]",
    "DeltaFy [µN]",
]
DEFAULT_TITLES = {
    ("t", 1): "Total force as a function of time",
    ("x_t", 1): "Time [sec]",
    ("y_t", 1): "Total Force [µN]",
    ("t", 2): "Magnitude of forces in x and y-directions",
    ("x_t", 2): "Time [sec]",
    ("y_t", 2): "Force [µN]",
    ("t", 3): "Magnitude of forces in x-direction",
    ("x_t", 3): "Time [sec]",
    ("y_t", 3): "Force [µN]",
    ("t", 4): "Magnitude of forces in y-direction",
    ("x_t", 4): "Time [sec]",
    ("y_t", 4): "Force [µN]",
    ("t", 5): "Position in x-direction",
    ("x_t", 5): "Time [sec]",
    ("y_t", 5): "x Position [µm]",
    ("t", 6): "Position in y-direction",
    ("x_t", 6): "Time [sec]",
    ("y_t", 6): "y Position [µm]",
    ("t", 7): "Change of force in x-direction",
    ("x_t", 7): "Time [sec]",
    ("y_t", 7): "Δ Force [µN]",
    ("t", 8): "Change of force in y-direction",
    ("x_t", 8): "Time [sec]",
    ("y_t", 8): "Δ Force [µN]",
}
# Info page text
INFO_FILE_POS = resource_path("resources\\info_page_text.txt")


class WindowManager(ScreenManager):
    """Screen manager class"""

    def __init__(self, **kwargs):
        """The init method for the screen manager"""
        # Set a transition object so it can be referenced
        self.transition = SlideTransition()
        # Call ScreenManager init method
        super(ScreenManager, self).__init__(**kwargs)
        # Bind key strokes to methods
        Window.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)
        # Save a reference to the app object
        self.app = App.get_running_app()

    def on_key_down(self, _1, keycode, _2, _3, modifiers):
        """called when the user presses a key
        - decodes the key e.g. '241' -> 'e'
        - send it to IP2 or PS2 if they are current screen"""
        # Decodes the key e.g. '241' -> 'e'
        key = Keyboard.keycode_to_string(Keyboard, keycode)
        # If current window is IP2
        if self.app.root.current == "IP2":
            # Call IP2.image_widget.on_key_down
            self.ip2_window.image_widget.on_key_down(key, modifiers)
        # If current window is PS2
        if self.app.root.current == "PS2":
            # Call PS2.image_widget.on_key_down
            self.ps2_window.image_widget.on_key_down(key, modifiers)

    def on_key_up(self, _1, keycode, _2):
        """called when the user stops pressing a key
        - decodes the key e.g. '241' -> 'e'
        - send it to IP2 or PS2 if they are current screen"""
        # Decodes the key e.g. '241' -> 'e'
        key = Keyboard.keycode_to_string(Keyboard, keycode)
        # If current window is IP2
        if self.app.root.current == "IP2":
            # Call IP2.image_widget.on_key_up
            self.ip2_window.image_widget.on_key_up(key)
        # If current window is PS2
        if self.app.root.current == "PS2":
            # Call PS2.image_widget.on_key_up
            self.ps2_window.image_widget.on_key_up(key)


class MainWindow(Screen):
    """The screen for the main menu of PCT"""

    def __init__(self, **kwargs):
        """init method for the main menu"""
        # Initialise the info_text object for the .kv file before the .txt file is read
        self.info_text = ""
        # Call Screen init method
        super(MainWindow, self).__init__(**kwargs)
        # Read the info page text file
        with open(INFO_FILE_POS, "r", encoding="utf8") as file:
            self.info_text = file.read()
        # Get app reference
        self.app = App.get_running_app()

    def toggle_info(self):
        """Toggles the info screen on/off"""
        # If off
        if self.info_layout.disabled:
            # Turn on
            self.info_layout.disabled = False
            self.info_layout.pos = (0, 0)
            self.main_grid.disabled = True
        # If on
        else:
            # Turn off
            self.info_layout.disabled = True
            self.info_layout.pos = (99999, 99999)  # Sends it far away
            self.main_grid.disabled = False
            self.scroll.scroll_y = 1  # Resets the scroll


class PCTApp(App):
    """base of the PCT kivy app"""

    # Save default titles and column headers
    DEFAULT_TITLES = DEFAULT_TITLES
    COL_NAMES = COL_NAMES
    AUTO_COL_NAMES = AUTO_COL_NAMES
    # This function/method allows files to be accessed in the .exe application
    resource_path = class_resource_path

    def build(self):
        """initialises the app
        - sets the title & icon
        - binds methods
        - gets object references for later"""
        # Label window
        self.title = "Pillar Centroid Tracker"
        # Set app icon
        self.icon = resource_path("resources\\icon.png")
        # Bind the file drop call
        Window.bind(on_drop_file=self._on_file_drop)
        # Get a reference to the app
        self.app = App.get_running_app()
        # Get references to the screens needed
        self.ip1_window = self.app.root.get_screen("IP1")
        self.ps1_window = self.app.root.get_screen("PS1")
        self.pf1_window = self.app.root.get_screen("PF1")
        self.fg1_window = self.app.root.get_screen("FG1")
        return

    def _on_file_drop(self, window, file_path, x, y, *args):
        """called when a file is drag & dropped on the app window"""
        # Get the file path decoded
        file_path = file_path.decode("utf-8")
        # Send the path to one of these 4 windows if they are open
        if self.app.root.current == "IP1":
            self.ip1_window._on_file_drop(file_path, x, y)
        elif self.app.root.current == "PS1":
            self.ps1_window._on_file_drop(file_path, x, y)
        elif self.app.root.current == "PF1":
            self.pf1_window._on_file_drop(file_path, x, y)
        elif self.app.root.current == "FG1":
            self.fg1_window._on_file_drop(file_path, x, y)


# If this is the main python file
if __name__ == "__main__":
    # Run the PCT app
    PCTApp().run()
