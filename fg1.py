"""
Module: All classes related to Force to Graph Screen 1
Program: Pillar Centroid Tracker
Author: Haig Bishop (hbi34@uclive.ac.nz)
"""

# Import local modules
from popup_elements import BackPopup, ErrorPopup
from file_management import (
    file_header,
    file_name,
    is_csv_xml,
    detect_encoding,
    unlabel_columns,
)

# Kivy imports
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen

# Import modules used for dealing with files, etc.
from plyer import filechooser
from os.path import getctime
from datetime import datetime
from re import match
from csv import reader as csv_reader
import xml.etree.ElementTree as et
import os
from subprocess import Popen as p_open


class FG1Window(Screen):
    """1st force->graph screen"""

    def __init__(self, **kwargs):
        """init method for FG1"""
        # Call init method
        super(FG1Window, self).__init__(**kwargs)
        # Set current job
        self.current_job = None
        # Set fg2_window (cant access yet)
        self.fg2_window = None
        # The next three attributes prevent bugs when selecting drop downs
        self.deselecting = False
        self.wait_until = "none"
        # Holds a list of dropdown options which are currently used
        self.disabled_options = []
        # Save app as an attribute
        self.app = App.get_running_app()

    def generate(self):
        """called when generate button is pressed
        - checks the validity of the data
        - if not valid it makes a popup
        - if valid it copies the jobs over to FG2"""
        # Check data selected
        errors = self.check_data()
        # If there are errors
        if errors != []:
            # Make pop up - alerts of invalid data
            popup = ErrorPopup()
            popup.error_label.text = "Invalid Data:\n" + "".join(errors)
            popup.open()
        # If there are no errors
        else:
            # Get fg2_window if you haven't already
            if self.fg2_window is None:
                self.fg2_window = self.manager.get_screen("FG2")
            # Add all new jobs
            self.fg2_window.copy_jobs(self)
            # Grab the last job added
            final_job = self.fg2_window.fg2_scroll.grid_layout.children[-1]
            # Change screen
            app = App.get_running_app()
            app.root.current = "FG2"
            app.root.transition.direction = "left"
            # Set as current job
            self.fg2_window.current_job = final_job
            # Enable layouts
            self.fg2_window.param_grid_layout.disabled = False
            self.fg2_window.name_grid_layout.disabled = False
            # Update everything visually
            self.fg2_window.update_fields()
            self.fg2_window.update_job_selected()
            self.fg2_window.graph_widget.update_widget()

    def check_data(self):
        """checks data before converting
        - returns list of any errors"""
        # Make regular expression for job name
        name_regex = r"^[a-zA-Z0-9][a-zA-Z0-9[\]()_-]{0,30}$"
        name_list = []
        errors = []
        # For all jobs on job list
        for job in self.fg1_scroll.grid_layout.children:
            # Check for invalid name
            if not match(name_regex, job.name):
                # Invalid name
                errors.append(" • invalid name (" + str(job.name) + ")\n")
            # Check for unselected columns
            columns = [
                job.x_column,
                job.y_column,
                job.t_column,
                job.tf_column,
                job.xf_column,
                job.yf_column,
                job.dfx_column,
                job.dfy_column,
            ]
            if (None, None) in columns:
                # Invalid column(s)
                errors.append(" • unselected column(s)\n")
            else:
                # Check for invalid column lengths
                (
                    x_col,
                    y_col,
                    t_col,
                    tf_col,
                    xf_col,
                    yf_col,
                    dfx_col,
                    dfy_col,
                ) = job.column_values()
                equal_lens = all(
                    len(lst) == len(x_col)
                    for lst in [y_col, t_col, tf_col, xf_col, yf_col, dfx_col, dfy_col]
                )
                lessthan3 = len(x_col) < 3
                if (not equal_lens) or lessthan3:
                    # Invalid column lengths
                    errors.append(" • invlaid column length(s)\n")
                # Check for invalid column values
                for pos in (
                    x_col + y_col + t_col + tf_col + xf_col + yf_col + dfx_col + dfy_col
                ):
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
        """update dropdown menus to match the current job"""
        # If there is a current job
        if self.current_job is not None:
            # Get list of header values in the file
            header = file_header(self.current_job.file_location)
            # Set the dropdown menu values (minus selected value of opposite dropdown)
            self.dropdownx.values = header
            self.dropdowny.values = header
            self.dropdownt.values = header
            self.dropdowntf.values = header
            self.dropdownxf.values = header
            self.dropdownyf.values = header
            self.dropdowndfx.values = header
            self.dropdowndfy.values = header
            # Reset this list
            self.disabled_options = []
            # If this column is not selected for this job
            if self.current_job.x_column[1] is None:
                # Reset
                self.dropdownx.text = "select column"
            # If this column is selected for this job
            else:
                # Set to current jobs selection
                self.dropdownx.text = self.current_job.x_column[1]
                # Append this to the disabled options
                self.disabled_options.append(self.current_job.x_column[1])
            # If this column is not selected for this job
            if self.current_job.y_column[1] is None:
                # Reset
                self.dropdowny.text = "select column"
            # If this column is selected for this job
            else:
                # Set to current jobs selection
                self.dropdowny.text = self.current_job.y_column[1]
                # Append this to the disabled options
                self.disabled_options.append(self.current_job.y_column[1])
            # If this column is not selected for this job
            if self.current_job.t_column[1] is None:
                # Reset
                self.dropdownt.text = "select column"
            # If this column is selected for this job
            else:
                # Set to current jobs selection
                self.dropdownt.text = self.current_job.t_column[1]
                # Append this to the disabled options
                self.disabled_options.append(self.current_job.t_column[1])
            # If this column is not selected for this job

            if self.current_job.tf_column[1] is None:
                # Reset
                self.dropdowntf.text = "select column"
            # If this column is selected for this job
            else:
                # Set to current jobs selection
                self.dropdowntf.text = self.current_job.tf_column[1]
                # Append this to the disabled options
                self.disabled_options.append(self.current_job.tf_column[1])
            # If this column is not selected for this job
            if self.current_job.xf_column[1] is None:
                # Reset
                self.dropdownxf.text = "select column"
            # If this column is selected for this job
            else:
                # Set to current jobs selection
                self.dropdownxf.text = self.current_job.xf_column[1]
                # Append this to the disabled options
                self.disabled_options.append(self.current_job.xf_column[1])
            # If this column is not selected for this job
            if self.current_job.yf_column[1] is None:
                # Reset
                self.dropdownyf.text = "select column"
            # If this column is selected for this job
            else:
                # Set to current jobs selection
                self.dropdownyf.text = self.current_job.yf_column[1]
                # Append this to the disabled options
                self.disabled_options.append(self.current_job.yf_column[1])
            # If this column is not selected for this job
            if self.current_job.dfx_column[1] == None:
                # Reset
                self.dropdowndfx.text = "select column"
            # If this column is selected for this job
            else:
                # Set to current jobs selection
                self.dropdowndfx.text = self.current_job.dfx_column[1]
                # Append this to the disabled options
                self.disabled_options.append(self.current_job.dfx_column[1])
            # If this column is not selected for this job
            if self.current_job.dfy_column[1] == None:
                # Reset
                self.dropdowndfy.text = "select column"
            # If this column is selected for this job
            else:
                # Set to current jobs selection
                self.dropdowndfy.text = self.current_job.dfy_column[1]
                # Append this to the disabled options
                self.disabled_options.append(self.current_job.dfy_column[1])
        # If there is no current job
        else:
            # Reset to default values
            self.dropdownx.values = []
            self.dropdowny.values = []
            self.dropdownt.values = []
            self.dropdowntf.values = []
            self.dropdownxf.values = []
            self.dropdownyf.values = []
            self.dropdowndfx.values = []
            self.dropdowndfy.values = []
            self.dropdownx.text = "select column"
            self.dropdowny.text = "select column"
            self.dropdownt.text = "select column"
            self.dropdowntf.text = "select column"
            self.dropdownxf.text = "select column"
            self.dropdownyf.text = "select column"
            self.dropdowndfx.text = "select column"
            self.dropdowndfy.text = "select column"

    def select_columnx(self, column_name):
        """called when column x is selected
        - checks if we should proceed
        - updates the current job
        - updates any other jobs if bulk update is on"""
        # These two statements prevent GUI related bugs
        # Dont run this code if we are deselecting and column_name isn't None
        if self.deselecting == False and column_name == self.wait_until:
            self.wait_until = "none"
            # Reset column
            self.current_job.x_column = (None, None)
            self.dropdownx.text = "select column"
        elif column_name is None:  # Deselect
            # Reset column
            self.current_job.x_column = (None, None)
            self.dropdownx.text = "select column"
        # If we are not deselecting, then update the job(s)
        elif self.deselecting == False:
            # This line might not make sense but it fixes a bug
            if self.current_job is not None:
                # If bulk checkbox is ticked
                if self.my_checkbox.active:
                    # Get all the jobs
                    jobs_to_try_update = list(self.fg1_scroll.grid_layout.children)
                else:
                    # Just get the current job
                    jobs_to_try_update = [self.current_job]
                # Update all these jobs
                for job in jobs_to_try_update:
                    # Update the job attribute
                    if column_name in job.header:
                        col_num = job.header.index(column_name)
                        job.x_column = (col_num, column_name)
            # Update the dropdowns
            self.update_drop_downs()
        # Fixes GUI issue
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
            self.dropdowny.text = "select column"
        elif column_name is None:  # Deselect
            # Reset column
            self.current_job.y_column = (None, None)
            self.dropdowny.text = "select column"
        # If we are not deselecting, then update the job(s)
        elif self.deselecting == False:
            # This line might not make sense but it fixes a bug
            if self.current_job is not None:
                # If bulk checkbox is ticked
                if self.my_checkbox.active:
                    # Get all the jobs
                    jobs_to_try_update = list(self.fg1_scroll.grid_layout.children)
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

    def select_columnt(self, column_name):
        """called when column t is selected
        - checks if we should proceed
        - updates the current job
        - updates any other jobs if bulk update is on"""
        # These two statements prevent GUI related bugs
        # Dont run this code if we are deselecting and column_name isn't None
        if self.deselecting == False and column_name == self.wait_until:
            self.wait_until = "none"
            # Reset column
            self.current_job.t_column = (None, None)
            self.dropdownt.text = "select column"
        elif column_name is None:  # Deselect
            # Reset column
            self.current_job.t_column = (None, None)
            self.dropdownt.text = "select column"
        # If we are not deselecting, then update the job(s)
        elif self.deselecting == False:
            # This line might not make sense but it fixes a bug
            if self.current_job is not None:
                # If bulk checkbox is ticked
                if self.my_checkbox.active:
                    # Get all the jobs
                    jobs_to_try_update = list(self.fg1_scroll.grid_layout.children)
                else:
                    # Just get the current job
                    jobs_to_try_update = [self.current_job]
                # Update all these jobs
                for job in jobs_to_try_update:
                    # Update the job attribute
                    if column_name in job.header:
                        col_num = job.header.index(column_name)
                        job.t_column = (col_num, column_name)
            # Update the dropdowns
            self.update_drop_downs()
        # Fixes GUI issue
        if column_name is None:
            self.deselecting = False

    def select_columntf(self, column_name):
        """called when column tf is selected
        - checks if we should proceed
        - updates the current job
        - updates any other jobs if bulk update is on"""
        # These two statements prevent GUI related bugs
        # Dont run this code if we are deselecting and column_name isn't None
        if self.deselecting == False and column_name == self.wait_until:
            self.wait_until = "none"
            # Reset column
            self.current_job.tf_column = (None, None)
            self.dropdowntf.text = "select column"
        elif column_name is None:  # Deselect
            # Reset column
            self.current_job.tf_column = (None, None)
            self.dropdowntf.text = "select column"
        # If we are not deselecting, then update the job(s)
        elif self.deselecting == False:
            # This line might not make sense but it fixes a bug
            if self.current_job is not None:
                # If bulk checkbox is ticked
                if self.my_checkbox.active:
                    # Get all the jobs
                    jobs_to_try_update = list(self.fg1_scroll.grid_layout.children)
                else:
                    # Just get the current job
                    jobs_to_try_update = [self.current_job]
                # Update all these jobs
                for job in jobs_to_try_update:
                    # Update the job attribute
                    if column_name in job.header:
                        col_num = job.header.index(column_name)
                        job.tf_column = (col_num, column_name)
            # Update the dropdowns
            self.update_drop_downs()
        # Fixes GUI issue
        if column_name is None:
            self.deselecting = False

    def select_columnxf(self, column_name):
        """called when column xf is selected
        - checks if we should proceed
        - updates the current job
        - updates any other jobs if bulk update is on"""
        # These two statements prevent GUI related bugs
        # Dont run this code if we are deselecting and column_name isn't None
        if self.deselecting == False and column_name == self.wait_until:
            self.wait_until = "none"
            # Reset column
            self.current_job.xf_column = (None, None)
            self.dropdownxf.text = "select column"
        elif column_name is None:  # Deselect
            # Reset column
            self.current_job.xf_column = (None, None)
            self.dropdownxf.text = "select column"
        # If we are not deselecting, then update the job(s)
        elif self.deselecting == False:
            # This line might not make sense but it fixes a bug
            if self.current_job is not None:
                # If bulk checkbox is ticked
                if self.my_checkbox.active:
                    # Get all the jobs
                    jobs_to_try_update = list(self.fg1_scroll.grid_layout.children)
                else:
                    # Just get the current job
                    jobs_to_try_update = [self.current_job]
                # Update all these jobs
                for job in jobs_to_try_update:
                    # Update the job attribute
                    if column_name in job.header:
                        col_num = job.header.index(column_name)
                        job.xf_column = (col_num, column_name)
            # Update the dropdowns
            self.update_drop_downs()
        # Fixes GUI issue
        if column_name is None:
            self.deselecting = False

    def select_columnyf(self, column_name):
        """called when column yf is selected
        - checks if we should proceed
        - updates the current job
        - updates any other jobs if bulk update is on"""
        # These two statements prevent GUI related bugs
        # Dont run this code if we are deselecting and column_name isn't None
        if self.deselecting == False and column_name == self.wait_until:
            self.wait_until = "none"
            # Reset column
            self.current_job.yf_column = (None, None)
            self.dropdownyf.text = "select column"
        elif column_name is None:  # Deselect
            # Reset column
            self.current_job.yf_column = (None, None)
            self.dropdownyf.text = "select column"
        # If we are not deselecting, then update the job(s)
        elif self.deselecting == False:
            # This line might not make sense but it fixes a bug
            if self.current_job is not None:
                # If bulk checkbox is ticked
                if self.my_checkbox.active:
                    # Get all the jobs
                    jobs_to_try_update = list(self.fg1_scroll.grid_layout.children)
                else:
                    # Just get the current job
                    jobs_to_try_update = [self.current_job]
                # Update all these jobs
                for job in jobs_to_try_update:
                    # Update the job attribute
                    if column_name in job.header:
                        col_num = job.header.index(column_name)
                        job.yf_column = (col_num, column_name)
            # Update the dropdowns
            self.update_drop_downs()
        # Fixes GUI issue
        if column_name is None:
            self.deselecting = False

    def select_columndfx(self, column_name):
        """called when column dfx is selected
        - checks if we should proceed
        - updates the current job
        - updates any other jobs if bulk update is on"""
        # These two statements prevent GUI related bugs
        # Dont run this code if we are deselecting and column_name isn't None
        if self.deselecting == False and column_name == self.wait_until:
            self.wait_until = "none"
            # Reset column
            self.current_job.dfx_column = (None, None)
            self.dropdowndfx.text = "select column"
        elif column_name is None:  # Deselect
            # Reset column
            self.current_job.dfx_column = (None, None)
            self.dropdowndfx.text = "select column"
        # If we are not deselecting, then update the job(s)
        elif self.deselecting == False:
            # This line might not make sense but it fixes a bug
            if self.current_job is not None:
                # If bulk checkbox is ticked
                if self.my_checkbox.active:
                    # Get all the jobs
                    jobs_to_try_update = list(self.fg1_scroll.grid_layout.children)
                else:
                    # Just get the current job
                    jobs_to_try_update = [self.current_job]
                # Update all these jobs
                for job in jobs_to_try_update:
                    # Update the job attribute
                    if column_name in job.header:
                        col_num = job.header.index(column_name)
                        job.dfx_column = (col_num, column_name)
            # Update the dropdowns
            self.update_drop_downs()
        # Fixes GUI issue
        if column_name is None:
            self.deselecting = False

    def select_columndfy(self, column_name):
        """called when column dfy is selected
        - checks if we should proceed
        - updates the current job
        - updates any other jobs if bulk update is on"""
        # These two statements prevent GUI related bugs
        # Dont run this code if we are deselecting and column_name isn't None
        if self.deselecting == False and column_name == self.wait_until:
            self.wait_until = "none"
            # Reset column
            self.current_job.dfy_column = (None, None)
            self.dropdowndfy.text = "select column"
        elif column_name is None:  # Deselect
            # Reset column
            self.current_job.dfy_column = (None, None)
            self.dropdowndfy.text = "select column"
        # If we are not deselecting, then update the job(s)
        elif self.deselecting == False:
            # This line might not make sense but it fixes a bug
            if self.current_job is not None:
                # If bulk checkbox is ticked
                if self.my_checkbox.active:
                    # Get all the jobs
                    jobs_to_try_update = list(self.fg1_scroll.grid_layout.children)
                else:
                    # Just get the current job
                    jobs_to_try_update = [self.current_job]
                # Update all these jobs
                for job in jobs_to_try_update:
                    # Update the job attribute
                    if column_name in job.header:
                        col_num = job.header.index(column_name)
                        job.dfy_column = (col_num, column_name)
            # Update the dropdowns
            self.update_drop_downs()
        # Fixes GUI issue
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
        # If all selections are real selection
        all_files_exist = all([os.path.exists(f_l) for f_l in selection])
        if all_files_exist:
            # For each selection
            for file_loc in selection:
                # If is is a genuine selection of valid type
                if is_csv_xml(file_loc):
                    # If it doesn't already exist
                    if self.non_duplicate(file_loc):
                        # Create a new baby on the job list
                        new_box = FG1JobListBox(file_location=file_loc, fg1_window=self)
                        self.fg1_scroll.grid_layout.add_widget(new_box)
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
        if duplicate or invalid_type or not all_files_exist:
            # Make an error string depending on the combination of errors
            error_string = ""
            if duplicate:
                # Update error string
                error_string += "File duplicate(s)  "
            if invalid_type:
                # Update error string
                error_string += "Incorrect file type(s)  "
            if not all_files_exist:
                # Update error string
                error_string += "File(s) no longer exist"
            # Update location label to show the error
            self.location_label.text = error_string

    def non_duplicate(self, file_loc):
        """takes a location of a file
        returns True if the file is not a current job"""
        duplicate = False
        # For all jobs on job list
        for job in self.fg1_scroll.grid_layout.children:
            # If this job is the same
            if job.file_location == file_loc:
                duplicate = True
        return not duplicate

    def update_fields(self):
        """updates the text inputs and the the "location label"
        new values are determined by the current job"""
        # If a job is currently selected
        if self.current_job is not None:
            # Set labels and input and dropdowns to the job
            self.location_label.text = str(self.current_job.file_location)
            self.name_input.text = str(self.current_job.name)
            self.update_drop_downs()
        # If NO job is currently selected
        else:
            # Reset labels and input and dropdowns
            self.location_label.text = "No file(s) selected"
            self.name_input.text = ""
            self.update_drop_downs()

    def update_job_selected(self):
        """updates every job's is_selected boolean, which affects it visually"""
        # For each job
        for job in self.fg1_scroll.grid_layout.children:
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
        if len(self.fg1_scroll.grid_layout.children) > 0:
            # Make pop up - asks if you are sure you want to exit
            popup = BackPopup(self.clear_jobs, "FG1")
            # Open it
            popup.open()
        # If there are not jobs
        else:
            # Make pop up - asks if you are sure you want to exit
            popup = BackPopup(self.clear_jobs, "FG1")
            # THEN IMMEDIATELY CLOSE IT
            popup.on_answer("yes")

    def clear_jobs(self):
        """simply empties the job list
        - this has to be a while loop, because the list changes size while looping"""
        # While there are still jobs
        while len(self.fg1_scroll.grid_layout.children) != 0:
            # Remove the first job using on_x_btn
            self.fg1_scroll.on_x_btn(self.fg1_scroll.grid_layout.children[0])

    def _on_file_drop(self, file_path, x, y):
        """called when a file is dropped on this screen
        - sends the file path to the selected method"""
        self.selected([file_path])


class FG1ScrollView(ScrollView):
    """scrolling widget in FG1"""

    def __init__(self, **kwargs):
        """init method for the scrolling widget in FG1"""
        # Call ScrollView init method
        super(FG1ScrollView, self).__init__(**kwargs)

    def on_x_btn(self, box):
        """called when an x button on a box is pressed or using clear_jobs
        - disables the layouts because there is nothing selected now
        - removes the jobs
        - updates visuals"""
        # Disabled layouts
        self.fg1_window.param_grid_layout.disabled = True
        self.fg1_window.name_grid_layout.disabled = True
        # Remove that job
        self.grid_layout.remove_widget(box)
        # Update current job to none
        self.fg1_window.current_job = None
        # Update visual stuff
        self.fg1_window.update_fields()
        self.fg1_window.update_job_selected()


class FG1JobListBox(Button):
    """job widget on the FG1ScrollView widget"""

    def __init__(self, file_location, fg1_window, **kwargs):
        """init method for the job widgets on the scrolling widget in FG1"""
        # Save the fg1_window as a reference
        self.fg1_window = fg1_window
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
        # Set columns
        self.set_columns()
        # This job should be selected at creation!
        self.is_selected = True

    def on_press(self):
        """called when the job box is pressed
        - sets this job to be current
        - enables layouts
        - updates visuals
        - scrolls textboxes back to the start"""
        # Temporarily uncheck mycheckbox (stops unwanted updating of fields)
        checkstate = self.fg1_window.my_checkbox.active and True
        self.fg1_window.my_checkbox.active = False
        # This is now the current job
        self.fg1_window.current_job = self
        # Enable layouts
        self.fg1_window.param_grid_layout.disabled = False
        self.fg1_window.name_grid_layout.disabled = False
        # Update the visuals
        self.fg1_window.update_fields()
        self.fg1_window.update_job_selected()
        # Reset texbox positions
        self.fg1_window.name_input.scroll_x = 0
        # Return checkbox to previous state
        self.fg1_window.my_checkbox.active = checkstate

    def update_is_selected(self):
        """update the is_selected attribute, which affects visuals"""
        # If this job is selected
        if self.fg1_window.current_job == self:
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
        if all([col in unlabelled_header for col in self.app.COL_NAMES]):
            # Auto select them all
            self.x_column = (
                unlabelled_header.index(self.app.AUTO_COL_NAMES["x_pos"]),
                self.header[unlabelled_header.index(self.app.AUTO_COL_NAMES["x_pos"])],
            )
            self.y_column = (
                unlabelled_header.index(self.app.AUTO_COL_NAMES["y_pos"]),
                self.header[unlabelled_header.index(self.app.AUTO_COL_NAMES["y_pos"])],
            )
            self.t_column = (
                unlabelled_header.index(self.app.AUTO_COL_NAMES["time"]),
                self.header[unlabelled_header.index(self.app.AUTO_COL_NAMES["time"])],
            )
            self.tf_column = (
                unlabelled_header.index(self.app.AUTO_COL_NAMES["t_for"]),
                self.header[unlabelled_header.index(self.app.AUTO_COL_NAMES["t_for"])],
            )
            self.xf_column = (
                unlabelled_header.index(self.app.AUTO_COL_NAMES["x_for"]),
                self.header[unlabelled_header.index(self.app.AUTO_COL_NAMES["x_for"])],
            )
            self.yf_column = (
                unlabelled_header.index(self.app.AUTO_COL_NAMES["y_for"]),
                self.header[unlabelled_header.index(self.app.AUTO_COL_NAMES["y_for"])],
            )
            self.dfx_column = (
                unlabelled_header.index(self.app.AUTO_COL_NAMES["dfx"]),
                self.header[unlabelled_header.index(self.app.AUTO_COL_NAMES["dfx"])],
            )
            self.dfy_column = (
                unlabelled_header.index(self.app.AUTO_COL_NAMES["dfy"]),
                self.header[unlabelled_header.index(self.app.AUTO_COL_NAMES["dfy"])],
            )
            # Set values accordingly
            (
                self.x_vals,
                self.y_vals,
                self.t_vals,
                self.tf_vals,
                self.xf_vals,
                self.yf_vals,
                self.dfx_vals,
                self.dfx_vals,
            ) = self.column_values()
        else:
            # Just do empty ones, so the user can select manually
            self.x_column = (None, None)
            self.y_column = (None, None)
            self.t_column = (None, None)
            self.tf_column = (None, None)
            self.xf_column = (None, None)
            self.yf_column = (None, None)
            self.dfx_column = (None, None)
            self.dfy_column = (None, None)
            self.x_vals = []
            self.y_vals = []
            self.t_vals = []
            self.tf_vals = []
            self.xf_vals = []
            self.yf_vals = []
            self.dfx_vals = []
            self.dfx_vals = []

    def column_values(self):
        """read the file and returns a value list for each column"""
        # Set empty lists
        (
            x_col_list,
            y_col_list,
            t_col_list,
            tf_col_list,
            xf_col_list,
            yf_col_list,
            dfx_col_list,
            dfy_col_list,
        ) = ([], [], [], [], [], [], [], [])
        # If a csv file
        if self.file_location[-4:] == ".csv":
            # If this file exists
            if os.path.exists(self.file_location):
                # Read the csv file and extract the values
                encoding = detect_encoding(self.file_location)
                with open(self.file_location, "r", encoding=encoding) as csv_file:
                    reader = csv_reader(csv_file)
                    next(reader)  # Skip header row
                    # Read the rows
                    for row in reader:
                        x_col_list.append(row[self.x_column[0]])
                        y_col_list.append(row[self.y_column[0]])
                        t_col_list.append(row[self.t_column[0]])
                        tf_col_list.append(row[self.tf_column[0]])
                        xf_col_list.append(row[self.xf_column[0]])
                        yf_col_list.append(row[self.yf_column[0]])
                        dfx_col_list.append(row[self.dfx_column[0]])
                        dfy_col_list.append(row[self.dfy_column[0]])
        # If an xml file
        elif self.file_location[-4:] == ".xml":
            # If this file exists
            if os.path.exists(self.file_location):
                # Read the xml file and extract the values
                tree = et.parse(self.file_location)
                root = tree.getroot()
                # Read the 'rows'
                for detection in root.findall(".//detection"):
                    x_col_list.append(detection.get(self.x_column[1]))
                    y_col_list.append(detection.get(self.y_column[1]))
                    t_col_list.append(detection.get(self.t_column[1]))
                    tf_col_list.append(detection.get(self.tf_column[1]))
                    xf_col_list.append(detection.get(self.xf_column[1]))
                    yf_col_list.append(detection.get(self.yf_column[1]))
                    dfx_col_list.append(detection.get(self.dfx_column[1]))
                    dfy_col_list.append(detection.get(self.dfy_column[1]))
        # Save col values as attributes :)
        self.x_vals = x_col_list[:]
        self.y_vals = y_col_list[:]
        self.t_vals = t_col_list[:]
        self.tf_vals = tf_col_list[:]
        self.xf_vals = xf_col_list[:]
        self.yf_vals = yf_col_list[:]
        self.dfx_vals = dfx_col_list[:]
        self.dfy_vals = dfy_col_list[:]
        return (
            x_col_list,
            y_col_list,
            t_col_list,
            tf_col_list,
            xf_col_list,
            yf_col_list,
            dfx_col_list,
            dfy_col_list,
        )

    def on_open_btn(self, file_or_folder):
        """Called by button on job box
        - opens the file/folder associated with the job"""
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
