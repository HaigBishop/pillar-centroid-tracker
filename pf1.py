"""
Module:  All classes related to Position to Force Screen 1
Program: Pillar Centroid Tracker
Author: Haig Bishop (hbi34@uclive.ac.nz)
"""

# Import local modules
from popup_elements import BackPopup, ErrorPopup, ContinuePopup
from file_management import (
    file_header,
    is_csv_xml,
    file_name,
    detect_encoding,
    unlabel_columns,
)

# Kivy imports
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen

# Import modules for dealing with files
from os.path import getctime
from datetime import datetime
from plyer import filechooser
import re
import csv
import os
import xml.etree.ElementTree as et
from subprocess import Popen as p_open


# Set default force calculation parameters
PILLAR_DIAMETER = 7.3
PILLAR_HEIGHT = 11.1
PILLAR_CONTACT = 5.55
PIXEL_MICRON_RATIO = 10
PDMS_E = 1.47
PDMS_GAMA = 0.5
TIME_BASE = 0.13


class PF1Window(Screen):
    """position -> force screen"""

    def __init__(self, **kwargs):
        """init method for PF1"""
        # Call Screen init method
        super(PF1Window, self).__init__(**kwargs)
        # Set current job
        self.current_job = None
        # Set list of which options are disabled
        self.disabled_options = []
        # Set fg1_window (cant access yet)
        self.fg1_window = None
        # These two attributes help solve an issue when deselecting
        self.deselecting = False
        self.wait_until = "none"
        # Save app as an attribute
        self.app = App.get_running_app()

    def convert(self):
        """called when convert button is pressed
        - checks if data is ok to convert
        - if no errors the continue popup is made"""
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
            if self.fg1_window == None:
                # Get fg1_window
                self.fg1_window = self.manager.get_screen("FG1")
            # Make pop up - asks if you are sure you want to continue
            popup = ContinuePopup(self.clear_jobs, self.pf1_scroll, self.fg1_window)
            popup.open()

    def check_data(self):
        """checks data before converting
        - returns list of errors"""
        # Make regular expression for job name
        name_regex = r"^[a-zA-Z0-9][a-zA-Z0-9[\]()_-]{0,30}$"
        name_list = []
        errors = []
        # For all jobs on job list
        for job in self.pf1_scroll.grid_layout.children:
            # Check for invalid parameters
            for param in [
                job.pixel_micron_ratio,
                job.time_base,
                job.pillar_height,
                job.pillar_contact,
                job.pdms_E,
                job.pdms_gama,
                job.pillar_diameter,
            ]:
                try:
                    # Try convert to float
                    float(param)
                except ValueError:
                    # Invalid float
                    errors.append(" • invalid float (" + str(param) + ")\n")
                    break
            # Check for invalid name
            if not re.match(name_regex, job.name):
                # Invalid name
                errors.append(" • invalid name (" + str(job.name) + ")\n")
            # Check for invalid columns selected
            if job.x_column == (None, None) or job.y_column == (None, None):
                # Invalid column(s)
                errors.append(" • unselected column\n")
            else:
                # Check for invalid column lengths
                x_col, y_col = job.column_values()
                unequal = len(x_col) != len(y_col)
                lessthan3 = len(x_col) < 3
                if unequal or lessthan3:
                    # Invalid column lengths
                    errors.append(" • invlaid column length(s)\n")
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

    def update_drop_downs(self):
        """update drop down menus to match the current job"""
        if self.current_job is not None:
            # Get list of header values in the file
            header = file_header(self.current_job.file_location)
            # Set the dropdown x & y menu values (minus selected value of opposite dropdown)
            self.dropdownx.values = header
            self.dropdowny.values = header
            # Reset the diabled option list
            self.disabled_options = []
            # Set column text
            if self.current_job.x_column[1] == None:
                # Reset
                self.dropdownx.text = "select column"
            else:
                # Set to current jobs selection
                self.dropdownx.text = self.current_job.x_column[1]
                self.disabled_options.append(self.current_job.x_column[1])
            if self.current_job.y_column[1] == None:
                # Reset
                self.dropdowny.text = "select column"
            else:
                # Set to current jobs selection
                self.dropdowny.text = self.current_job.y_column[1]
                self.disabled_options.append(self.current_job.y_column[1])
        else:
            # Reset to default values
            self.dropdownx.values = []
            self.dropdowny.values = []
            self.dropdownx.text = "select column"
            self.dropdowny.text = "select column"

    def select_columnx(self, column_name):
        """called when column x is selected in"""
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
                    jobs_to_try_update = list(self.pf1_scroll.grid_layout.children)
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
        """called when column y is selected in"""
        # Dont run this code if we are deselecting and column_name isn't None
        if self.deselecting == False and column_name == self.wait_until:
            self.wait_until = "none"
            self.current_job.y_column = (None, None)
            self.dropdownytext = "select column"
        elif column_name is None:  # Deselect
            self.current_job.y_column = (None, None)
            self.dropdowny.text = "select column"
        elif self.deselecting == False:
            # This line might not make sense but it fixes a bug
            if self.current_job is not None:
                # If bulk checkboc is ticked
                if self.my_checkbox.active:
                    jobs_to_try_update = list(self.pf1_scroll.grid_layout.children)
                else:
                    jobs_to_try_update = [self.current_job]
                # Update all these jobs
                for job in jobs_to_try_update:
                    # Update the job attribute
                    if column_name in job.header:
                        col_num = job.header.index(column_name)
                        job.y_column = (col_num, column_name)
        self.update_drop_downs()
        if column_name is None:
            self.deselecting = False

    def select_file(self):
        """called when [select file(s)] button is pressed
        - opens the file select window
        - selection is sent to self.selected()"""
        # Only allow selection of csv or xml
        filters = [("CSV files", "*.csv"), ("XML files", "*.xml")]
        # Open file selector window - send selection to self.selected
        filechooser.open_file(
            on_selection=self.selected,
            title="Select file(s)",
            filters=filters,
            multiple=True,
        )

    def selected(self, selection):
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
                if self.non_duplicate(file_loc):
                    # Create a new baby on the job list
                    new_box = PF1JobListBox(file_location=file_loc, pf1_window=self)
                    self.pf1_scroll.grid_layout.add_widget(new_box)
                    # Set as current job
                    self.current_job = new_box
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
            # Update location label to show user the error
            self.location_label.text = error_string

    def non_duplicate(self, file_loc):
        """takes a location of a file
        returns True if the file is not a current job"""
        # For all jobs on job list
        for job in self.pf1_scroll.grid_layout.children:
            # If this job is the same
            if job.file_location == file_loc:
                return False
        return True

    def update_fields(self):
        """updates the text inputs and the the "location label"
        new values are determined by the current job"""
        # If a job is currently selected
        if self.current_job is not None:
            # Set labels and inputs and dropdowns to the job
            self.location_label.text = str(self.current_job.file_location)
            self.name_input.text = str(self.current_job.name)
            self.pixel_micron_input.text = str(self.current_job.pixel_micron_ratio)
            self.time_base_input.text = str(self.current_job.time_base)
            self.pill_heig_input.text = str(self.current_job.pillar_height)
            self.pill_cont_input.text = str(self.current_job.pillar_contact)
            self.pdms_E_input.text = str(self.current_job.pdms_E)
            self.pdms_gama_input.text = str(self.current_job.pdms_gama)
            self.pill_diam_input.text = str(self.current_job.pillar_diameter)
            self.update_drop_downs()
        # If NO job is currently selected
        else:
            # Reset labels and inputs and dropdowns
            self.location_label.text = "No file(s) selected"
            self.name_input.text = ""
            self.pixel_micron_input.text = ""
            self.time_base_input.text = ""
            self.pill_heig_input.text = ""
            self.pill_cont_input.text = ""
            self.pdms_E_input.text = ""
            self.pdms_gama_input.text = ""
            self.pill_diam_input.text = ""
            self.update_drop_downs()

    def update_job_selected(self):
        """updates every job's is_selected boolean, which affects it visually"""
        # For each job
        for job in self.pf1_scroll.grid_layout.children:
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

    def on_pixelmicron_text(self, text):
        """called when pixel2micron ratio text input is changed"""
        # If a job is selected
        if self.current_job is not None:
            # If bulk checkboc is ticked
            if self.my_checkbox.active:
                # Update all jobs
                for job in self.pf1_scroll.grid_layout.children:
                    job.pixel_micron_ratio = text
            else:
                # Upadte the job's pixel2micron ratio
                self.current_job.pixel_micron_ratio = text

    def on_timebase_text(self, text):
        """called when timebase text input is changed"""
        # If a job is selected
        if self.current_job is not None:
            # If bulk checkboc is ticked
            if self.my_checkbox.active:
                # Update all jobs
                for job in self.pf1_scroll.grid_layout.children:
                    job.time_base = text
            else:
                # Upadte the job's time_base ratio
                self.current_job.time_base = text

    def on_pillheig_text(self, text):
        """called when pillheight text input is changed"""
        # If a job is selected
        if self.current_job is not None:
            # If bulk checkboc is ticked
            if self.my_checkbox.active:
                # Update all jobs
                for job in self.pf1_scroll.grid_layout.children:
                    job.pillar_height = text
            else:
                # Upadte the job's pillar_height ratio
                self.current_job.pillar_height = text

    def on_pillcont_text(self, text):
        """called when pillcontact text input is changed"""
        # If a job is selected
        if self.current_job is not None:
            # If bulk checkboc is ticked
            if self.my_checkbox.active:
                # Update all jobs
                for job in self.pf1_scroll.grid_layout.children:
                    job.pillar_contact = text
            else:
                # Upadte the job's pillar_contact ratio
                self.current_job.pillar_contact = text

    def on_pdmsE_text(self, text):
        """called when pdmsE text input is changed"""
        # If a job is selected
        if self.current_job is not None:
            # If bulk checkboc is ticked
            if self.my_checkbox.active:
                # Update all jobs
                for job in self.pf1_scroll.grid_layout.children:
                    job.pdms_E = text
            else:
                # Upadte the job's pdmsE ratio
                self.current_job.pdms_E = text

    def on_pdmsgama_text(self, text):
        """called when pdms gamma text input is changed"""
        # If a job is selected
        if self.current_job is not None:
            # If bulk checkboc is ticked
            if self.my_checkbox.active:
                # Update all jobs
                for job in self.pf1_scroll.grid_layout.children:
                    job.pdms_gama = text
            else:
                # Upadte the job's pdms_gama ratio
                self.current_job.pdms_gama = text

    def on_pilldiam_text(self, text):
        """called when pilldiam text input is changed"""
        # If a job is selected
        if self.current_job is not None:
            # If bulk checkboc is ticked
            if self.my_checkbox.active:
                # Update all jobs
                for job in self.pf1_scroll.grid_layout.children:
                    job.pillar_diameter = text
            else:
                # Upadte the job's pillar_diameter ratio
                self.current_job.pillar_diameter = text

    def on_diam_reset_btn(self):
        """called when the reset button by the pillar diam textbox is pressed
        - toggles the pillar diameter between 5.4 and 7.3"""
        # If 7.3
        if self.pill_diam_input.text == "7.3":
            # Toggle to 5.4
            self.pill_diam_input.text = "5.4"
        else:
            # Else set to 7.3
            self.pill_diam_input.text = "7.3"

    def on_back_btn(self):
        """called by back btn
        - makes a BackPopup object
        - if there are no jobs, it immediately closes it"""
        # If there are any jobs
        if len(self.pf1_scroll.grid_layout.children) > 0:
            # Make pop up - asks if you are sure you want to exit
            popup = BackPopup(self.clear_jobs, "PF1")
            # Open it
            popup.open()
        # If there are not jobs
        else:
            # Make pop up - asks if you are sure you want to exit
            popup = BackPopup(self.clear_jobs, "PF1")
            # THEN IMMEDIATELY CLOSE IT
            popup.on_answer("yes")

    def clear_jobs(self):
        """simply empties the job list
        - this has to be a while loop, because the list changes size while looping"""
        # While there are still jobs
        while len(self.pf1_scroll.grid_layout.children) != 0:
            # Remove the first job using on_x_btn
            self.pf1_scroll.on_x_btn(self.pf1_scroll.grid_layout.children[0])

    def _on_file_drop(self, file_path, x, y):
        """called when a file is dropped on this screen
        - sends the file path to the selected method"""
        self.selected([file_path])


class PF1ScrollView(ScrollView):
    """scrolling widget in PF1"""

    def __init__(self, **kwargs):
        """init method for the scrolling widget in PF1"""
        # Call ScrollView init method
        super(PF1ScrollView, self).__init__(**kwargs)

    def on_x_btn(self, box):
        """called when an x button on a box is pressed or using clear_jobs
        - disables the layouts because there is nothing selected now
        - removes the jobs
        - updates visuals"""
        # Disabled layouts
        self.pf1_window.param_grid_layout.disabled = True
        self.pf1_window.name_grid_layout.disabled = True
        # Remove that job
        self.grid_layout.remove_widget(box)
        # Update current job to none
        self.pf1_window.current_job = None
        # Update visual stuff
        self.pf1_window.update_fields()
        self.pf1_window.update_job_selected()


class PF1JobListBox(Button):
    """job widget on the PF1ScrollView widget"""

    def __init__(self, file_location, pf1_window, **kwargs):
        """init method for the job widgets on the scrolling widget in PF1"""
        # Save the pf1_window as a reference
        self.pf1_window = pf1_window
        # Save app as an attribute
        self.app = App.get_running_app()
        # Call Button init method
        super().__init__(**kwargs)
        # Save file location
        self.file_location = file_location
        # Get the header of the file (list of column names)
        self.header = file_header(self.file_location)
        # Set the same as the file name (e.g. '...\folder\filename.txt'  -> 'filename')
        self.name = file_name(file_location)
        # Grab the date of creation of the file
        if os.path.exists(file_location):
            self.date = datetime.fromtimestamp(getctime(file_location)).strftime(
                "%d/%m/%Y"
            )
        else:
            self.date = "File no longer exists"

        # Set default parameters
        self.pillar_diameter = PILLAR_DIAMETER
        self.pillar_height = PILLAR_HEIGHT
        self.pillar_contact = PILLAR_CONTACT
        self.pixel_micron_ratio = PIXEL_MICRON_RATIO
        self.pdms_E = PDMS_E
        self.pdms_gama = PDMS_GAMA
        self.time_base = TIME_BASE

        # Column # And name for x & y  (e.g. (0, 'X'))
        self.x_column = (None, None)
        self.y_column = (None, None)
        self.x_vals = []
        self.y_vals = []
        # This job should be selected at creation!
        self.is_selected = True
        # Set columns
        self.set_columns()

    def on_press(self):
        """called when the job box is pressed
        - sets this job to be current
        - enables layouts
        - updates visuals
        - scrolls textboxes back to the start"""
        # Temporarily uncheck mycheckbox (stops unwanted updating of fields)
        checkstate = self.pf1_window.my_checkbox.active and True
        self.pf1_window.my_checkbox.active = False
        # This is now the current job
        self.pf1_window.current_job = self
        # Enable layouts
        self.pf1_window.param_grid_layout.disabled = False
        self.pf1_window.name_grid_layout.disabled = False
        # Update the visuals
        self.pf1_window.update_fields()
        self.pf1_window.update_job_selected()
        # Reset texbox positions
        self.pf1_window.name_input.scroll_x = 0
        self.pf1_window.pill_diam_input.scroll_x = 0
        self.pf1_window.pixel_micron_input.scroll_x = 0
        self.pf1_window.time_base_input.scroll_x = 0
        self.pf1_window.pill_heig_input.scroll_x = 0
        self.pf1_window.pill_cont_input.scroll_x = 0
        self.pf1_window.pdms_E_input.scroll_x = 0
        self.pf1_window.pdms_gama_input.scroll_x = 0
        self.pf1_window.pill_diam_input.scroll_x = 0
        # Return checkbox to previous state
        self.pf1_window.my_checkbox.active = checkstate

    def floaterise(self):
        """makes all string inputs into floats
        - also affects position data"""
        self.pixel_micron_ratio = float(self.pixel_micron_ratio)
        self.time_base = float(self.time_base)
        self.pillar_height = float(self.pillar_height)
        self.pillar_contact = float(self.pillar_contact)
        self.pdms_E = float(self.pdms_E)
        self.pdms_gama = float(self.pdms_gama)
        self.pillar_diameter = float(self.pillar_diameter)
        self.x_vals = [float(x) for x in self.x_vals]
        self.y_vals = [float(y) for y in self.y_vals]

    def update_is_selected(self):
        """update the is_selected attribute, which affects visuals"""
        # If this job is selected
        if self.pf1_window.current_job == self:
            # Remember that
            self.is_selected = True
        else:
            # Remember that
            self.is_selected = False

    def set_columns(self):
        """sets the job attributes for each column when the job is imported
        - these are like this:
        - (column #, column name) e.g. (0, 'X')
        - if the column names are defaults it auto selects them"""
        # Strip the [1], [2], etc. from the self.header values
        unlabelled_header = unlabel_columns(self.header)
        # If default column names
        if all(
            [
                col in unlabelled_header
                for col in ["x Position [pixels]", "y Position [pixels]"]
            ]
        ):
            self.x_column = (
                unlabelled_header.index("x Position [pixels]"),
                self.header[unlabelled_header.index("x Position [pixels]")],
            )
            self.y_column = (
                unlabelled_header.index("y Position [pixels]"),
                self.header[unlabelled_header.index("y Position [pixels]")],
            )
            # Set values accordingly
            self.x_vals, self.y_vals = self.column_values()
        else:
            # Just do empty ones, so the user can select manually
            self.x_column = (None, None)
            self.y_column = (None, None)
            self.x_vals = []
            self.y_vals = []

    def column_values(self):
        """read the file and returns a value list for each column"""
        # Set empty lists
        x_col_list, y_col_list = [], []
        # If a csv file
        if self.file_location[-4:] == ".csv":
            # If this file exists
            if os.path.exists(self.file_location):
                # Read the csv file and extract the values
                encoding = detect_encoding(self.file_location)
                # Read the CSV file and extract the header row
                with open(self.file_location, "r", encoding=encoding) as csv_file:
                    reader = csv.reader(csv_file)
                    next(reader)  # Skip header row
                    # Read the rows
                    for row in reader:
                        x_col_list.append(row[self.x_column[0]])
                        y_col_list.append(row[self.y_column[0]])
        # If an xml file
        elif self.file_location[-4:] == ".xml":
            # If this file exists
            if os.path.exists(self.file_location):
                tree = et.parse(self.file_location)
                root = tree.getroot()
                # Read the 'rows'
                for detection in root.findall(".//detection"):
                    x_col_list.append(detection.get(self.x_column[1]))
                    y_col_list.append(detection.get(self.y_column[1]))
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
