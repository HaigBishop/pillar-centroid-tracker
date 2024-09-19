"""
Module:  All classes related to Image -> Position Screen 1
Program: Pillar Centroid Tracker
Author: Haig Bishop (hbi34@uclive.ac.nz)
"""

# Import local modules
from popup_elements import BackPopup, ErrorPopup
from file_management import (
    folder_name,
    is_valid_folder,
    images_from_folder,
    valid_image_dims,
)

# Kivy imports
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

# Import modules for dealing with files
from os.path import getctime
from datetime import datetime
import os
import re
from subprocess import Popen as p_open
from plyer import filechooser


class IP1Window(Screen):
    """position -> force screen"""

    def __init__(self, **kwargs):
        """init method for IP1 screen"""
        # Call ScrollView init method
        super(IP1Window, self).__init__(**kwargs)
        # Set current job
        self.current_job = None
        # Set (an empty) reference for the IP2 window
        self.ip2_window = None
        # Save app as an attribute
        self.app = App.get_running_app()
        # Make the loading screen invisible
        Clock.schedule_once(self.end_loading, 0.01)

    def detect(self):
        """called by pressing the Detect button
        - starts the loading screen
        - schedules the detect method to be called"""
        # Set up the loading screen
        self.start_loading()
        # Schedule the export to start
        Clock.schedule_once(self.start_detect)

    def start_detect(self, *args):
        """starts the detection process"""
        # Check if the selected data is valid
        errors = self.check_data()
        # If there are issues with the data
        if errors != []:
            # Make pop up - alerts of invalid data
            popup = ErrorPopup()
            # Adjust the text on the popup
            popup.error_label.text = "Invalid Data:\n" + "".join(errors)
            popup.open()
            self.end_loading()
        # If no issues with the data
        else:
            # Schedule the export to start
            Clock.schedule_once(self.detect_start, 0.01)

    def start_loading(self):
        """makes the loading screen visible"""
        self.loading_layout.opacity = 1

    def end_loading(self, *args):
        """makes the loading screen invisible"""
        self.loading_layout.opacity = 0

    def detect_start(self, *args):
        """copys all the jobs to the IP2 window"""
        # Get the ip2_window reference
        if self.ip2_window is None:
            self.ip2_window = self.manager.get_screen("IP2")
        # Add all new jobs to the IP2 window
        self.ip2_window.copy_jobs(self)
        # Grab the last job added
        final_job = self.ip2_window.ip2_scroll.grid_layout.children[-1]
        # Change screen
        app = App.get_running_app()
        app.root.current = "IP2"
        app.root.transition.direction = "left"
        # Set as current job
        self.ip2_window.current_job = final_job
        # Update everything visually
        self.ip2_window.update_job_selected()
        self.ip2_window.image_widget.update_image()
        # Removes the loading screen
        self.end_loading()

    def check_data(self):
        """checks data before converting - returns list of errors
        - valid name
        - is folder
        - contains > 3 images of same type
        - images are the same dimensions"""
        # Make regular expression for job name
        name_regex = r"^[a-zA-Z0-9][a-zA-Z0-9[\]()_-]{0,30}$"
        name_list = []
        errors = []
        # For all jobs on job list
        for job in self.ip1_scroll.grid_layout.children:
            # Check for invalid name
            if not re.match(name_regex, job.name):
                # Invalid name
                errors.append(" • invalid name (" + str(job.name) + ")\n")
            # Check if folder
            if not is_valid_folder(job.folder_location):
                # Invalid image contents (or folder doesn't exist)
                errors.append(" • invalid folder contents (" + str(job.name) + ")\n")
            # Check if all images are the same (valid dimensions)
            elif not valid_image_dims(job.image_locations):
                # Invalid image dimensions, etc
                errors.append(" • invalid image (" + str(job.name) + ")\n")
            # Add this job's name to list (to check for duplicates)
            name_list.append(job.name)
        # Check for duplicate names
        if len(name_list) != len(set(name_list)):
            # Duplicate names
            errors.append(" • duplicate names\n")
        # Return the errors which have been found
        return list(set(errors))

    def select_folder(self):
        """called when [select folder(s)] button is pressed
        - opens the folder select window
        - selection is sent to self.selected()"""
        # Open folder selector window - send selection to self.selected
        filechooser.choose_dir(
            on_selection=self.selected, title="Select folder(s)", multiple=True
        )

    def selected(self, selection):
        """receives selection from selector window
        - checks if the selections are valid
        - if they are it adds them as jobs
        - if any are not valid it will display an error string"""
        # Set booleans to test if selection is valid
        no_valid, duplicate, invalid_contents = True, False, False
        # For each folder
        for folder_location in selection:
            # If the folder is a valid image sequence
            if is_valid_folder(folder_location):
                # If this folder is not already a job
                if self.non_duplicate(folder_location):
                    # Create a new baby on the job list
                    new_box = IP1JobListBox(
                        folder_location=folder_location, ip1_window=self
                    )
                    self.ip1_scroll.grid_layout.add_widget(new_box)
                    # Set as current job
                    self.current_job = new_box
                    # Enable layouts
                    self.param_grid_layout.disabled = False
                    self.name_grid_layout.disabled = False
                    # Update everything visually
                    self.update_fields()
                    self.update_job_selected()
                    no_valid = False
                # If this folder is already a job
                else:
                    duplicate = True
            # If the folder is an invalid image sequence
            else:
                invalid_contents = True
        # If none are valid
        if no_valid:
            # Deselect any jobs, update location label
            self.current_job = None
            # Disable layouts
            self.param_grid_layout.disabled = True
            self.name_grid_layout.disabled = True
            # Update everything visually
            self.update_fields()
            self.update_job_selected()
        # If there was a failed selection
        if duplicate or invalid_contents:
            # Make an error string describing the issue
            error_string = ""
            if duplicate == True:
                # Update error string
                error_string += "File duplicate(s)  "
            if invalid_contents == True:
                # Update error string
                error_string += "Incorrect file type(s)"
            # Update location label
            self.location_label.text = error_string

    def non_duplicate(self, folder_loc):
        """takes a folder location
        - returns true if the location is not found in a current job"""
        # For all jobs on job list
        for job in self.ip1_scroll.grid_layout.children:
            # If this job has the same location
            if job.folder_location == folder_loc:
                return False
        return True

    def update_fields(self):
        """updates the text inputs and the 'location label'
        - new values are determined by the current job"""
        # If there is a current job
        if self.current_job is not None:
            # Update with current job's values
            self.location_label.text = str(self.current_job.folder_location)
            self.name_input.text = str(self.current_job.name)
        else:
            # Reset with defaults
            self.location_label.text = "No folder(s) selected"
            self.name_input.text = ""

    def update_job_selected(self):
        """updates every job's is_selected boolean, which affects it visually"""
        # For each job
        for job in self.ip1_scroll.grid_layout.children:
            # Update whether or not it is selected
            job.update_is_selected()

    def on_name_text(self, text):
        """called when name text input is changed
        - takes the new text
        - updates the current job if there is one"""
        # If a job is selected
        if self.current_job is not None:
            # Upadte the job's name
            self.current_job.name = text

    def on_back_btn(self):
        """called by back btn
        - makes a BackPopup object
        - if there are no jobs, it immediately closes it"""
        # If there are any jobs
        if len(self.ip1_scroll.grid_layout.children) > 0:
            # Make pop up - asks if you are sure you want to exit
            popup = BackPopup(self.clear_jobs, "IP1")
            # Open it
            popup.open()
        # If there are not jobs
        else:
            # Make pop up - asks if you are sure you want to exit
            popup = BackPopup(self.clear_jobs, "IP1")
            # THEN IMMEDIATELY CLOSE IT
            popup.on_answer("yes")

    def clear_jobs(self):
        """simply empties the job list
        - this has to be a while loop, because the list changes size while looping"""
        # While there are still jobs
        while len(self.ip1_scroll.grid_layout.children) != 0:
            # Remove the first job using on_x_btn
            self.ip1_scroll.on_x_btn(self.ip1_scroll.grid_layout.children[0])

    def _on_file_drop(self, file_path, x, y):
        """called when a file is dropped on this screen
        - sends the file path to the selected method"""
        self.selected([file_path])


class IP1ScrollView(ScrollView):
    """scrolling widget in IP1"""

    def __init__(self, **kwargs):
        """init method for the scrolling widget in IP1"""
        # Call ScrollView init method
        super(IP1ScrollView, self).__init__(**kwargs)

    def on_x_btn(self, box):
        """called when an x button on a box is pressed or using clear_jobs
        - disables the layouts because there is nothing selected now
        - removes the jobs
        - updates visuals"""
        # Disabled layouts
        self.ip1_window.param_grid_layout.disabled = True
        self.ip1_window.name_grid_layout.disabled = True
        # Remove that job
        self.grid_layout.remove_widget(box)
        # Update current job to none
        self.ip1_window.current_job = None
        # Update visual stuff
        self.ip1_window.update_fields()
        self.ip1_window.update_job_selected()


class IP1JobListBox(Button):
    """job widget on the IP1ScrollView widget"""

    def __init__(self, folder_location, ip1_window, **kwargs):
        """init method for the job widgets on the scrolling widget in IP1"""
        # Save the ip1_window as a reference
        self.ip1_window = ip1_window
        # Save file location
        self.folder_location = folder_location
        # Images from folder
        self.image_locations, self.image_type = images_from_folder(folder_location)
        # Save app as an attribute
        self.app = App.get_running_app()
        # Call Button init method
        super().__init__(**kwargs)
        # Set the same as the file name (e.g. '...\folder\filename.txt'  -> 'filename')
        self.name = folder_name(folder_location)
        # Grab the date of creation of the file
        if os.path.exists(folder_location):
            self.date = datetime.fromtimestamp(getctime(folder_location)).strftime(
                "%d/%m/%Y"
            )
        else:
            self.date = "File no longer exists"
        # This job should be selected at creation!
        self.is_selected = True
        # Save app as an attribute
        self.app = App.get_running_app()

    def on_press(self):
        """called when the job box is pressed
        - sets this job to be current
        - enables layouts
        - updates visuals
        - scrolls textboxes back to the start"""
        # This is now the current job
        self.ip1_window.current_job = self
        # Enable layouts
        self.ip1_window.param_grid_layout.disabled = False
        self.ip1_window.name_grid_layout.disabled = False
        # Update the visuals
        self.ip1_window.update_fields()
        self.ip1_window.update_job_selected()

    def update_is_selected(self):
        """update the is_selected attribute, which affects visuals"""
        # If this job is selected
        if self.ip1_window.current_job == self:
            # Remember that
            self.is_selected = True
        else:
            # Remember that
            self.is_selected = False

    def on_open_btn(self, file_or_folder):
        """Called by button on job box
        Opens the file/folder associated with the job"""
        if file_or_folder == "file":
            # Use the path for the directory containing the file
            # Find last slash
            s = str(self.file_location).rfind("\\") + 1
            # E.g. 'C:\Desktop\folder\'
            path = str(self.file_location)[:s]
        elif file_or_folder == "folder":
            # Just use that path
            path = self.folder_location
        # Open that folder in the explorer
        p_open('explorer "' + str(path) + '"')
