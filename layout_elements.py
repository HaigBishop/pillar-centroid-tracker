"""
Module: Kivy Layout elements (except popups)
Program: Pillar Centroid Tracker
Author: Haig Bishop (hbi34@uclive.ac.nz)
"""


# Kivy imports
from kivy.uix.spinner import Spinner
from kivy.uix.spinner import SpinnerOption
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout

# Import modules for dealing with files
import re


class BlankSpinner(Spinner):
    """class for a custom Kivy spinner object
    - these are drop down menus"""

    def __init__(self, **kwargs):
        """init method for BlankSpinner"""
        # Call init method for Spinner
        super(BlankSpinner, self).__init__(**kwargs)
        # This holds the previous selected value
        self._last_value = None
        # Bind any change to the text attribute to the _on_text method
        self.bind(text=self._on_text)

    def _on_text(self, _, value):
        """called when text is adjusted
        - update the previous value"""
        self._last_value = value


class MySpinnerOption(SpinnerOption):
    """class for a custom Kivy spinner option object
    - these are the options on the drop down menus"""

    def __init__(self, **kwargs):
        """init method for MySpinnerOption"""
        # Call SpinnerOption init method
        super(SpinnerOption, self).__init__(**kwargs)

    def on_press(self):
        """called when the option is selected
        - this function allows deselection of the option"""
        # Access the parent spinner
        spinner = self.parent.parent.attach_to
        # If there is no accessable spinner
        if spinner is None:
            # Set last_val to None
            last_val = None
        # If there is an accessable spinner
        else:
            # Set last_val to the spinner's
            last_val = spinner._last_value
        # Get the new value
        new_val = self.text
        # If the user clicked on the already selected one
        if last_val == new_val:
            # Update these values which prevent errors when deselecting
            spinner.my_window.wait_until = new_val
            spinner.my_window.deselecting = True
            # Deselect that option
            spinner._on_selection(None)


class PF2SpinnerOption(SpinnerOption):
    """class for a custom Kivy spinner option object
    - these are the options on the drop down menus"""

    def __init__(self, **kwargs):
        """init method for PF2SpinnerOption"""
        # Call SpinnerOption init method
        super(PF2SpinnerOption, self).__init__(**kwargs)


class FloatInput(TextInput):
    """A custom Kivy Textbox which filters only floats"""

    # Create the regular expression
    pat = re.compile("[^0-9\-]")

    def insert_text(self, substring, from_undo=False):
        """overwrites the default insert_text function
        - I am not entirely sure how this works
        - but it only allows proper floats in the input"""
        # If there is a '.' in the current text
        if "." in self.text:
            s = re.sub(self.pat, "", substring)
        # If there is no '.' in the current text
        else:
            s = ".".join(re.sub(self.pat, "", s) for s in substring.split(".", 1))
        # Do all normal insert_text stuff now
        return super().insert_text(s, from_undo=from_undo)
