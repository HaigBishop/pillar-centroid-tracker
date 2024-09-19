"""
Module:  All classes related to Position Screening Screen 1
Program: Pillar Centroid Tracker
Author: Haig Bishop (hbi34@uclive.ac.nz)
"""

# Import local modules
from popup_elements import BackPopup, ErrorPopup
from file_management import (
    folder_name,
    is_valid_folder,
    images_from_folder,
    is_csv_xml,
    file_header,
    detect_encoding,
    valid_image_dims,
    num_valid_images,
)

# Kivy imports
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen

# Import modules for dealing with files
from os.path import getctime
from datetime import datetime
import csv
import os
import re
import xml.etree.ElementTree as et
from subprocess import Popen as p_open
from plyer import filechooser


class PS1Window(Screen):
    """position -> force screen"""

    def __init__(self, **kwargs):
        """init method for PS1"""
        # Call ScrollView init method
        super(PS1Window, self).__init__(**kwargs)
        # Set list of which options are disabled
        self.disabled_options = []
        # Set current job
        self.current_job = None
        # Set (an empty) reference for the PS2 window
        self.ps2_window = None
        # The next three attributes prevent bugs when selecting drop downs
        self.deselecting = False
        self.wait_until = "none"
        # Save app as an attribute
        self.app = App.get_running_app()

    def proceed(self):
        """called when detect button is pressed"""
        # Check if the selected data is good
        errors = self.check_data()
        # If there are issues with the data
        if errors != []:
            # Make pop up - alerts of invalid data
            popup = ErrorPopup()
            # Adjust the text on the popup
            popup.error_label.text = "Invalid Data:\n" + "".join(errors)
            popup.open()
        # If no issues with the data
        else:
            if self.ps2_window == None:
                # Get ps2_window
                self.ps2_window = self.manager.get_screen("PS2")
            # Add all new jobs
            self.ps2_window.copy_jobs(self)
            # Grab the last job added
            final_job = self.ps2_window.ps2_scroll.grid_layout.children[-1]
            # Change screen
            app = App.get_running_app()
            app.root.current = "PS2"
            app.root.transition.direction = "left"
            # Set as current job
            self.ps2_window.current_job = final_job
            # Update everything visually
            self.ps2_window.update_job_selected()
            self.ps2_window.image_widget.update_image()

    def check_data(self):
        """checks data before converting - returns list of errors
        - valid name
        - is folder
        - contains > 3 images of same type
        - images are the same dimensions
        - unselected column(s) *
        - invalid column lengths (+same as num_images) *
        - invalid column values *"""
        # Make regular expression for job name
        name_regex = r"^[a-zA-Z0-9][a-zA-Z0-9[\]()_-]{0,30}$"
        name_list = []
        errors = []
        # For all jobs on job list
        for job in self.ps1_scroll.grid_layout.children:
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
                # Invalid image contents (or folder doesn't exist)
                errors.append(" • invalid image dimensions (" + str(job.name) + ")\n")
            # Check for invalid columns selected
            if job.x_column == (None, None) or job.y_column == (None, None):
                # Invalid column(s)
                errors.append(" • unselected column (" + str(job.name) + ")\n")
            else:
                # Check for invalid column lengths
                num_images = num_valid_images(job.folder_location)
                x_col, y_col = job.column_values()
                unequal = (len(x_col) != len(y_col)) or (len(x_col) != num_images)
                lessthan3 = len(x_col) < 3
                if unequal or lessthan3:
                    # Invalid column lengths
                    errors.append(
                        " • invlaid column length(s) (" + str(job.name) + ")\n"
                    )
                # Check for invalid column values
                for pos in x_col + y_col:
                    try:
                        # Try convert to float
                        float(pos)
                    except ValueError:
                        # Invalid float
                        errors.append(" • invalid column value (" + str(pos) + ")\n")
                        break
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
        - selection is sent to self.selected_folder()"""
        # Open folder selector window - send selection to self.selected
        filechooser.choose_dir(
            on_selection=self.selected_folder, title="Select folder(s)", multiple=True
        )

    def selected_folder(self, selection):
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
                if self.non_duplicate_folder(folder_location):
                    # Create a new baby on the job list
                    new_box = PS1JobListBox(
                        folder_location=folder_location, ps1_window=self
                    )
                    self.ps1_scroll.grid_layout.add_widget(new_box)
                    # Set as current job
                    self.current_job = new_box
                    # Enable layouts
                    self.param_grid_layout.disabled = True
                    self.name_grid_layout.disabled = False
                    self.file_select_layout.disabled = False
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
            self.file_select_layout.disabled = True
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

    def non_duplicate_folder(self, folder_loc):
        """takes a folder location
        - returns true if the object is unique from current jobs"""
        # For all jobs on job list
        for job in self.ps1_scroll.grid_layout.children:
            # If this job is the same
            if job.folder_location == folder_loc:
                return False
        return True

    def update_drop_downs(self):
        """update drop down menus depending on the current job"""
        # If there is a current job
        if self.current_job is not None and self.current_job.file_location is not None:
            # Get list of header values in the file
            header = file_header(self.current_job.file_location)
            # Set the dropdown x & y menu values (minus selected value of opposite dropdown)
            self.dropdownx.values = header
            self.dropdowny.values = header
            # Save the header in the job
            self.current_job.header = header
            # Reset this list
            self.disabled_options = []
            # If this column is not selected for this job
            if self.current_job.x_column[1] == None:
                # Reset
                self.dropdownx.text = "select column"
            # If this column is selected for this job
            else:
                # Set to current jobs selection
                self.dropdownx.text = self.current_job.x_column[1]
                # Append this to the disabled options
                self.disabled_options.append(self.current_job.x_column[1])
            # If this column is not selected for this job
            if self.current_job.y_column[1] == None:
                # Reset
                self.dropdowny.text = "select column"
            # If this column is selected for this job
            else:
                # Set to current jobs selection
                self.dropdowny.text = self.current_job.y_column[1]
                # Append this to the disabled options
                self.disabled_options.append(self.current_job.y_column[1])
        # If there is no current job
        else:
            # Reset to default values
            self.dropdownx.values = []
            self.dropdowny.values = []
            self.dropdownx.text = "select column"
            self.dropdowny.text = "select column"

    def select_columnx(self, column_name):
        """called when column x is selected
        - checks if we should proceed
        - updates the current job
        - updates any other jobs if bulk update is on"""
        # These two statements prevent GUI related bugs
        # Dont run this code if we are deselecting and column_name isn't None
        if self.deselecting == False and column_name == self.wait_until:
            self.wait_until = "none"
            self.current_job.x_column = (None, None)
            self.dropdownx.text = "select column"
        elif column_name is None:  # Deselect
            self.current_job.x_column = (None, None)
            self.dropdownx.text = "select column"
        elif self.deselecting == False:
            # This line might not make sense but it fixes a bug
            if self.current_job is not None:
                # If bulk checkboc is ticked
                if self.my_checkbox.active:
                    jobs_to_try_update = list(self.ps1_scroll.grid_layout.children)
                else:
                    jobs_to_try_update = [self.current_job]
                # Update all these jobs
                for job in jobs_to_try_update:
                    # Update the job attribute
                    if column_name in job.header:
                        col_num = job.header.index(column_name)
                        job.x_column = (col_num, column_name)
            self.update_drop_downs()
        if column_name is None:
            self.deselecting = False

    def select_columny(self, column_name):
        """called when column y is selected
        - checks if we should proceed
        - updates the current job
        - updates any other jobs if bulk update is on"""
        # These two statements prevent GUI related bugs
        # Dont run this code if we are deselecting and column_name isn't None
        if self.deselecting == False and column_name == self.wait_until:
            self.wait_until = "none"
            # Reset column
            self.current_job.y_column = (None, None)
            self.dropdownytext = "select column"
        elif column_name is None:  # Deselect
            # Reset column
            self.current_job.y_column = (None, None)
            self.dropdowny.text = "select column"
        # If we are not deselecting, then update the job(s)
        elif self.deselecting == False:
            # This line might not make sense but it fixes a bug
            if self.current_job is not None:
                # If bulk checkboc is ticked
                if self.my_checkbox.active:
                    # Get all the jobs
                    jobs_to_try_update = list(self.ps1_scroll.grid_layout.children)
                else:
                    # Just get the current job
                    jobs_to_try_update = [self.current_job]
                # Update all these jobs
                for job in jobs_to_try_update:
                    # Update the job attribute
                    if column_name in job.header:
                        col_num = job.header.index(column_name)
                        job.y_column = (col_num, column_name)
            # Update the dropdowns
            self.update_drop_downs()
        # Fixes GUI issue
        if column_name is None:
            self.deselecting = False

    def select_file(self):
        """called when [select file(s)] button is pressed
        - opens the file select window
        - selection is sent to self.selected_file()"""
        # Only allow selection of csv or xml
        filters = [("CSV files", "*.csv"), ("XML files", "*.xml")]
        # Open file selector window - send selection to self.selected
        filechooser.open_file(
            path=self.current_job.folder_location,
            on_selection=self.selected_file,
            title="Select file(s)",
            filters=filters,
            multiple=False,
        )

    def selected_file(self, selection):
        """receives selection from selector window
        - checks if the selections are valid
        - if they are it adds them as jobs
        - if any are not valid it will display an error string"""
        # Set booleans to test if selection is valid
        no_valid, duplicate, invalid_type = True, False, False
        # For each selection
        for file_loc in selection:
            # If is is a genuine selection of valid type
            if is_csv_xml(file_loc):
                # If it doesn't already exist
                if self.non_duplicate_file(file_loc):
                    # Update the jobs file location
                    self.current_job.file_location = file_loc
                    # Reset the jobs attributes
                    self.current_job.x_column = (None, None)
                    self.current_job.y_column = (None, None)
                    self.current_job.x_vals = []
                    self.current_job.y_vals = []
                    self.dropdownx.text = "select column"
                    self.dropdowny.text = "select column"
                    # Enable layouts
                    self.param_grid_layout.disabled = False
                    self.name_grid_layout.disabled = False
                    # Update everything visually
                    self.update_fields()
                    self.update_job_selected()
                    no_valid = False
                # It is a duplicate!
                else:
                    duplicate = True
            # It is invalid type!
            else:
                invalid_type = True
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
        if duplicate or invalid_type:
            # Make an error string depending on the combination of errors
            error_string = ""
            if duplicate == True:
                # Update error string
                error_string += "File duplicate(s)  "
            if invalid_type == True:
                # Update error string
                error_string += "Incorrect file type(s)"
            # Update location label
            self.file_location_label.text = error_string

    def non_duplicate_file(self, file_loc):
        """takes a location of a file
        returns True if the file is not a current job"""
        # For all jobs on job list
        for job in self.ps1_scroll.grid_layout.children:
            # If this job is the same
            if job.file_location == file_loc:
                return False
        return True

    def update_fields(self):
        """updates the text inputs and the the "location label"
        new values are determined by the current job"""
        # If a job is currently selected
        if self.current_job is not None:
            # Set labels and input and dropdowns to the job
            self.location_label.text = str(self.current_job.folder_location)
            self.file_location_label.text = (
                "  No file selected"
                if self.current_job.file_location is None
                else str(self.current_job.file_location)
            )
            self.name_input.text = str(self.current_job.name)
            self.update_drop_downs()
        # If NO job is currently selected
        else:
            # Reset labels and input and dropdowns
            self.location_label.text = "No folder(s) selected"
            self.file_location_label.text = "  No file selected"
            self.name_input.text = ""
            self.update_drop_downs()

    def update_job_selected(self):
        """updates every job's is_selected boolean, which affects it visually"""
        # For each job
        for job in self.ps1_scroll.grid_layout.children:
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
        if len(self.ps1_scroll.grid_layout.children) > 0:
            # Make pop up - asks if you are sure you want to exit
            popup = BackPopup(self.clear_jobs, "PS1")
            # Open it
            popup.open()
            # If there are not jobs
        else:
            # Make pop up - asks if you are sure you want to exit
            popup = BackPopup(self.clear_jobs, "PS1")
            # THEN IMMEDIATELY CLOSE IT
            popup.on_answer("yes")

    def clear_jobs(self):
        """simply empties the job list
        - this has to be a while loop, because the list changes size while looping"""
        # While there are still jobs
        while len(self.ps1_scroll.grid_layout.children) != 0:
            # Remove the first job using on_x_btn
            self.ps1_scroll.on_x_btn(self.ps1_scroll.grid_layout.children[0])

    def _on_file_drop(self, file_path, x, y):
        """called when a file/folder is dropped on this screen
        - sends the file/folder path to the selected method"""
        # Is it a file
        if os.path.isfile(file_path):
            # If there is a job
            if self.current_job is not None:
                self.selected_file([file_path])
        # Is it a folder
        elif os.path.isdir(file_path):
            self.selected_folder([file_path])


class PS1ScrollView(ScrollView):
    """scrolling widget in PS1"""

    def __init__(self, **kwargs):
        """init method for the scrolling widget in PS1"""
        # Call ScrollView init method
        super(PS1ScrollView, self).__init__(**kwargs)

    def on_x_btn(self, box):
        """called when an x button on a box is pressed or using clear_jobs
        - disables the layouts because there is nothing selected now
        - removes the jobs
        - updates visuals"""
        # Disabled layouts
        self.ps1_window.param_grid_layout.disabled = True
        self.ps1_window.name_grid_layout.disabled = True
        self.ps1_window.file_select_layout.disabled = True
        # Remove that job
        self.grid_layout.remove_widget(box)
        # Update current job to none
        self.ps1_window.current_job = None
        # Update visual stuff
        self.ps1_window.update_fields()
        self.ps1_window.update_job_selected()


class PS1JobListBox(Button):
    """job widget on the PS1ScrollView widget"""

    def __init__(self, folder_location, ps1_window, **kwargs):
        """init method for the job widgets on the scrolling widget in PS1"""
        # Save the ps1_window as a reference
        self.ps1_window = ps1_window
        # Save folder location
        self.folder_location = folder_location
        # Save file location
        self.file_location = None
        # Get the image locations and type
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
        # Column # And name for x & y  (e.g. (0, 'X'))
        self.x_column = (None, None)
        self.y_column = (None, None)
        self.x_vals = []
        self.y_vals = []
        self.header = []

    def on_press(self):
        """called when the job box is pressed
        - sets this job to be current
        - enables layouts
        - updates visuals"""
        # This is now the current job
        self.ps1_window.current_job = self
        # Enable layouts
        self.ps1_window.param_grid_layout.disabled = (
            True if self.ps1_window.current_job.file_location is None else False
        )
        self.ps1_window.name_grid_layout.disabled = False
        self.ps1_window.file_select_layout.disabled = False
        # Update the visuals
        self.ps1_window.update_fields()
        self.ps1_window.update_job_selected()

    def update_is_selected(self):
        """update the is_selected attribute, which affects visuals"""
        # If this job is selected
        if self.ps1_window.current_job == self:
            # Remember that
            self.is_selected = True
        else:
            # Remember that
            self.is_selected = False

    def column_values(self):
        """read the file and returns a value list for each column"""
        # Strip the [1], [2], etc. from the self.header values
        x_col_list, y_col_list = [], []
        # If a csv file
        if self.file_location[-4:] == ".csv":
            # If this file exists
            if os.path.exists(self.file_location):
                # Read the csv file and extract the values
                encoding = detect_encoding(self.file_location)
                with open(self.file_location, "r", encoding=encoding) as csv_file:
                    reader = csv.reader(csv_file)
                    next(reader)  # Skip header row
                    # Read the rows
                    for row in reader:
                        x_col_list.append(int(float(row[self.x_column[0]])))
                        y_col_list.append(int(float(row[self.y_column[0]])))
        # If an xml file
        elif self.file_location[-4:] == ".xml":
            # If this file exists
            if os.path.exists(self.file_location):
                # Read the xml file and extract the values
                tree = et.parse(self.file_location)
                root = tree.getroot()
                # Read the 'rows'
                for detection in root.findall(".//detection"):
                    x_col_list.append(int(float(detection.get(self.x_column[1]))))
                    y_col_list.append(int(float(detection.get(self.y_column[1]))))
        # Save col values as an attribute :)
        self.x_vals = x_col_list[:]
        self.y_vals = y_col_list[:]
        return x_col_list, y_col_list

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
