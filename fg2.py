"""
Module:  All classes related to Force to Graph Screen 2
Program: Pillar Centroid Tracker
Author: Haig Bishop (hbi34@uclive.ac.nz)
"""

# Import local modules
from popup_elements import BackPopup, ErrorPopup, FG2SuccessPopup
from file_management import rename_file_graph

# Kivy imports
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.graphics.texture import Texture
from kivy.clock import Clock

# Import modules used for dealing with files
from os.path import getctime
from datetime import datetime
import re
import os
from subprocess import Popen as p_open

# Import modules for dealing with images and graphs
from PIL import Image as PilImage
import numpy as np
import imageio
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO

# Set the plot font to Arial and turn off debug logging
matplotlib.use("Agg")
plt.rcParams["font.family"] = "Arial"
plt.set_loglevel("error")


class FG2Window(Screen):
    """2nd force->graph screen"""

    def __init__(self, **kwargs):
        """init method for FG2"""
        # Call init method
        super(FG2Window, self).__init__(**kwargs)
        # Set current job
        self.current_job = None
        # Save app as an attribute
        self.app = App.get_running_app()

    def start_loading(self):
        """makes the loading screen visible"""
        self.loading_layout.opacity = 1

    def end_loading(self):
        """makes the loading screen invisible"""
        self.loading_layout.opacity = 0

    def export(self):
        """called by pressing the Export button
        - starts the loading screen
        - schedules the export method to be called"""
        # Set up the loading screen
        self.start_loading()
        # Schedule the export to start
        Clock.schedule_once(self.export_graphs, 0.01)

    def export_graphs(self, _):
        """called when Export Graphs button is pressed"""
        # Check the names
        errors = self.check_data()
        # If there are errors
        if errors != []:
            # Make pop up - alerts of invalid data
            popup = ErrorPopup()
            popup.error_label.text = "Invalid Data:\n" + "".join(errors)
            popup.open()
        # If there are no errors
        else:
            # For each job
            for job in self.fg2_scroll.grid_layout.children:
                # Set this job as the current job
                self.current_job = job
                # Get dpi to use (inches are set in place)
                plot_dpi = 300
                # If this graph is ticked
                if job.making_t_for_graph:
                    # Generate a file name for the graph
                    new_file_loc = rename_file_graph(
                        job.file_location, job.name, graph_num=1
                    )
                    # Export this plot
                    self.graph_widget.current_graph = 1
                    self.graph_widget.export_current_plot(
                        plot_dpi=plot_dpi,
                        new_file_loc=new_file_loc,
                        svg=job.making_svg_graph,
                        png=job.making_png_graph,
                    )
                # If this graph is ticked
                if job.making_xy_for_graph:
                    # Generate a file name for the graph
                    new_file_loc = rename_file_graph(
                        job.file_location, job.name, graph_num=2
                    )
                    # Export this plot
                    self.graph_widget.current_graph = 2
                    self.graph_widget.export_current_plot(
                        plot_dpi=plot_dpi,
                        new_file_loc=new_file_loc,
                        svg=job.making_svg_graph,
                        png=job.making_png_graph,
                    )
                # If this graph is ticked
                if job.making_x_for_graph:
                    # Generate a file name for the graph
                    new_file_loc = rename_file_graph(
                        job.file_location, job.name, graph_num=3
                    )
                    # Export this plot
                    self.graph_widget.current_graph = 3
                    self.graph_widget.export_current_plot(
                        plot_dpi=plot_dpi,
                        new_file_loc=new_file_loc,
                        svg=job.making_svg_graph,
                        png=job.making_png_graph,
                    )
                # If this graph is ticked
                if job.making_y_for_graph:
                    # Generate a file name for the graph
                    new_file_loc = rename_file_graph(
                        job.file_location, job.name, graph_num=4
                    )
                    # Export this plot
                    self.graph_widget.current_graph = 4
                    self.graph_widget.export_current_plot(
                        plot_dpi=plot_dpi,
                        new_file_loc=new_file_loc,
                        svg=job.making_svg_graph,
                        png=job.making_png_graph,
                    )
                # If this graph is ticked
                if job.making_x_pos_graph:
                    # Generate a file name for the graph
                    new_file_loc = rename_file_graph(
                        job.file_location, job.name, graph_num=5
                    )
                    # Export this plot
                    self.graph_widget.current_graph = 5
                    self.graph_widget.export_current_plot(
                        plot_dpi=plot_dpi,
                        new_file_loc=new_file_loc,
                        svg=job.making_svg_graph,
                        png=job.making_png_graph,
                    )
                # If this graph is ticked
                if job.making_y_pos_graph:
                    # Generate a file name for the graph
                    new_file_loc = rename_file_graph(
                        job.file_location, job.name, graph_num=6
                    )
                    # Export this plot
                    self.graph_widget.current_graph = 6
                    self.graph_widget.export_current_plot(
                        plot_dpi=plot_dpi,
                        new_file_loc=new_file_loc,
                        svg=job.making_svg_graph,
                        png=job.making_png_graph,
                    )
                # If this graph is ticked
                if job.making_dfx_graph:
                    # Generate a file name for the graph
                    new_file_loc = rename_file_graph(
                        job.file_location, job.name, graph_num=7
                    )
                    # Export this plot
                    self.graph_widget.current_graph = 7
                    self.graph_widget.export_current_plot(
                        plot_dpi=plot_dpi,
                        new_file_loc=new_file_loc,
                        svg=job.making_svg_graph,
                        png=job.making_png_graph,
                    )
                # If this graph is ticked
                if job.making_dfy_graph:
                    # Generate a file name for the graph
                    new_file_loc = rename_file_graph(
                        job.file_location, job.name, graph_num=8
                    )
                    # Export this plot
                    self.graph_widget.current_graph = 8
                    self.graph_widget.export_current_plot(
                        plot_dpi=plot_dpi,
                        new_file_loc=new_file_loc,
                        svg=job.making_svg_graph,
                        png=job.making_png_graph,
                    )
            # Remove the loading screen
            self.end_loading()
            # Make pop up - alerts of files saved
            popup = FG2SuccessPopup(
                None,
                self.manager.get_screen("FG1"),
                self.manager.get_screen("FG2"),
            )
            popup.success_label.text = (
                "files saved successfully.\nGenerate more graphs or exit?"
            )
            popup.succ_gen_button.text = "Back to generate graphs"
            popup.open()

    def check_data(self):
        """checks job names before exporting graphs
        - returns list of any errors"""
        # Make regular expression for job name
        name_regex = r"^[a-zA-Z0-9][a-zA-Z0-9[\]()_-]{0,30}$"
        name_list = []
        errors = []
        # For all jobs on job list
        for job in self.fg2_scroll.grid_layout.children:
            # Check for invalid name
            if not re.match(name_regex, job.name):
                # Invalid name
                errors.append(" • invalid name (" + str(job.name) + ")\n")
            # Add this job's name to list (to check for duplicates)
            name_list.append(job.name)
        # Check for duplicate names
        if len(name_list) != len(set(name_list)):
            # Duplicate names
            errors.append(" • duplicate names\n")
        # Return the errors which have been found
        return list(set(errors))

    def copy_jobs(self, fg1_window):
        """copies each job in the FG1 window onto this window"""
        # For all jobs on job list
        for job in fg1_window.fg1_scroll.grid_layout.children:
            # Create a new baby on the job list
            new_box = FG2JobListBox(
                col_vals=job.column_values(),
                job_name=job.name,
                file_location=job.file_location,
                fg2_window=self,
            )
            self.fg2_scroll.grid_layout.add_widget(new_box)
            # Set as current job
            self.current_job = new_box
            # Enable layouts
            self.param_grid_layout.disabled = False
            self.name_grid_layout.disabled = False
        # Update everything visually
        self.update_fields()
        self.update_job_selected()
        self.loading_layout.opacity = 0

    def select_plot_type(self, plot_type):
        """called when plot_type is selected
        - updates the job(s) plot types
        - if the bulk checkbox is ticked it updates all jobs"""
        # Although this seems unecessary, it fixes a bug
        if self.current_job is not None:
            # If bulk checkbox is ticked
            if self.my_checkbox.active:
                # Select all jobs
                jobs_to_try_update = list(self.fg2_scroll.grid_layout.children)
            else:
                # Select 1 job
                jobs_to_try_update = [self.current_job]
            # Update all these jobs
            for job in jobs_to_try_update:
                # Update the job attribute
                job.plot_type = plot_type
        # Update the graph widget
        self.graph_widget.update_widget()

    def update_fields(self):
        """updates the text inputs and the the 'location label'
        (new values are determined by the current job)"""
        # If there is a current job
        if self.current_job is not None:
            # Set the location label and name input
            self.location_label.text = str(self.current_job.file_location)
            self.name_input.text = str(self.current_job.name)
            # If this is the current graph
            if self.graph_widget.current_graph == 1:
                # Set the inputs to the stored values for that graph
                self.title_input.text = str(self.current_job.graph_1["title"])
                self.x_title_input.text = str(self.current_job.graph_1["x_title"])
                self.y_title_input.text = str(self.current_job.graph_1["y_title"])
                self.y_axis_min_input.text = str(self.current_job.graph_1["y_min"])
                self.y_axis_max_input.text = str(self.current_job.graph_1["y_max"])
            # If this is the current graph
            if self.graph_widget.current_graph == 2:
                # Set the inputs to the stored values for that graph
                self.title_input.text = str(self.current_job.graph_2["title"])
                self.x_title_input.text = str(self.current_job.graph_2["x_title"])
                self.y_title_input.text = str(self.current_job.graph_2["y_title"])
                self.y_axis_min_input.text = str(self.current_job.graph_2["y_min"])
                self.y_axis_max_input.text = str(self.current_job.graph_2["y_max"])
            # If this is the current graph
            if self.graph_widget.current_graph == 3:
                # Set the inputs to the stored values for that graph
                self.title_input.text = str(self.current_job.graph_3["title"])
                self.x_title_input.text = str(self.current_job.graph_3["x_title"])
                self.y_title_input.text = str(self.current_job.graph_3["y_title"])
                self.y_axis_min_input.text = str(self.current_job.graph_3["y_min"])
                self.y_axis_max_input.text = str(self.current_job.graph_3["y_max"])
            # If this is the current graph
            if self.graph_widget.current_graph == 4:
                # Set the inputs to the stored values for that graph
                self.title_input.text = str(self.current_job.graph_4["title"])
                self.x_title_input.text = str(self.current_job.graph_4["x_title"])
                self.y_title_input.text = str(self.current_job.graph_4["y_title"])
                self.y_axis_min_input.text = str(self.current_job.graph_4["y_min"])
                self.y_axis_max_input.text = str(self.current_job.graph_4["y_max"])
            # If this is the current graph
            if self.graph_widget.current_graph == 5:
                # Set the inputs to the stored values for that graph
                self.title_input.text = str(self.current_job.graph_5["title"])
                self.x_title_input.text = str(self.current_job.graph_5["x_title"])
                self.y_title_input.text = str(self.current_job.graph_5["y_title"])
                self.y_axis_min_input.text = str(self.current_job.graph_5["y_min"])
                self.y_axis_max_input.text = str(self.current_job.graph_5["y_max"])
            # If this is the current graph
            if self.graph_widget.current_graph == 6:
                # Set the inputs to the stored values for that graph
                self.title_input.text = str(self.current_job.graph_6["title"])
                self.x_title_input.text = str(self.current_job.graph_6["x_title"])
                self.y_title_input.text = str(self.current_job.graph_6["y_title"])
                self.y_axis_min_input.text = str(self.current_job.graph_6["y_min"])
                self.y_axis_max_input.text = str(self.current_job.graph_6["y_max"])
            # If this is the current graph
            if self.graph_widget.current_graph == 7:
                # Set the inputs to the stored values for that graph
                self.title_input.text = str(self.current_job.graph_7["title"])
                self.x_title_input.text = str(self.current_job.graph_7["x_title"])
                self.y_title_input.text = str(self.current_job.graph_7["y_title"])
                self.y_axis_min_input.text = str(self.current_job.graph_7["y_min"])
                self.y_axis_max_input.text = str(self.current_job.graph_7["y_max"])
            # If this is the current graph
            if self.graph_widget.current_graph == 8:
                # Set the inputs to the stored values for that graph
                self.title_input.text = str(self.current_job.graph_8["title"])
                self.x_title_input.text = str(self.current_job.graph_8["x_title"])
                self.y_title_input.text = str(self.current_job.graph_8["y_title"])
                self.y_axis_min_input.text = str(self.current_job.graph_8["y_min"])
                self.y_axis_max_input.text = str(self.current_job.graph_8["y_max"])
            # Set the plot type
            self.dropdown_plot.text = self.current_job.plot_type
            # Set the plot checkboxes
            self.gt1_checkbox.state = (
                "down" if self.current_job.making_t_for_graph else "normal"
            )
            self.gt2_checkbox.state = (
                "down" if self.current_job.making_xy_for_graph else "normal"
            )
            self.gt3_checkbox.state = (
                "down" if self.current_job.making_x_pos_graph else "normal"
            )
            self.gt4_checkbox.state = (
                "down" if self.current_job.making_y_for_graph else "normal"
            )
            self.gt5_checkbox.state = (
                "down" if self.current_job.making_x_pos_graph else "normal"
            )
            self.gt6_checkbox.state = (
                "down" if self.current_job.making_y_pos_graph else "normal"
            )
            self.gt7_checkbox.state = (
                "down" if self.current_job.making_dfx_graph else "normal"
            )
            self.gt8_checkbox.state = (
                "down" if self.current_job.making_dfy_graph else "normal"
            )
            # Set the file export checkboxes
            self.svg_checkbox.state = (
                "down" if self.current_job.making_svg_graph else "normal"
            )
            self.png_checkbox.state = (
                "down" if self.current_job.making_png_graph else "normal"
            )
        else:
            # Set all as default/empty values
            self.location_label.text = "No file(s) selected"
            self.name_input.text = ""
            self.title_input.text = ""
            self.x_title_input.text = ""
            self.y_title_input.text = ""
            self.dropdown_plot.text = "Scatter"
            self.gt1_checkbox.state = "normal"
            self.gt2_checkbox.state = "normal"
            self.gt3_checkbox.state = "normal"
            self.gt4_checkbox.state = "normal"
            self.gt5_checkbox.state = "normal"
            self.gt6_checkbox.state = "normal"
            self.gt7_checkbox.state = "normal"
            self.gt8_checkbox.state = "normal"
            self.svg_checkbox.state = "normal"
            self.png_checkbox.state = "normal"
            self.y_axis_min_input.text = ""
            self.y_axis_max_input.text = ""

    def update_job_selected(self):
        """updates every job's is_selected boolean
        - affects them visually"""
        for job in self.fg2_scroll.grid_layout.children:
            job.update_is_selected()

    def on_name_text(self, text):
        """called when name text input is changed"""
        # If a job is selected
        if self.current_job is not None:
            # Update the job's name
            self.current_job.name = text

    def on_title_text(self, text):
        """called when title text input is changed"""
        # If a job is selected
        if self.current_job is not None:
            # If bulk checkbox is ticked
            if self.my_checkbox.active:
                # Update all jobs
                for job in self.fg2_scroll.grid_layout.children:
                    if self.graph_widget.current_graph == 1:
                        job.graph_1["title"] = text
                    if self.graph_widget.current_graph == 2:
                        job.graph_2["title"] = text
                    if self.graph_widget.current_graph == 3:
                        job.graph_3["title"] = text
                    if self.graph_widget.current_graph == 4:
                        job.graph_4["title"] = text
                    if self.graph_widget.current_graph == 5:
                        job.graph_5["title"] = text
                    if self.graph_widget.current_graph == 6:
                        job.graph_6["title"] = text
                    if self.graph_widget.current_graph == 7:
                        job.graph_7["title"] = text
                    if self.graph_widget.current_graph == 8:
                        job.graph_8["title"] = text
            else:
                # Upadte the job's title
                if self.graph_widget.current_graph == 1:
                    self.current_job.graph_1["title"] = text
                if self.graph_widget.current_graph == 2:
                    self.current_job.graph_2["title"] = text
                if self.graph_widget.current_graph == 3:
                    self.current_job.graph_3["title"] = text
                if self.graph_widget.current_graph == 4:
                    self.current_job.graph_4["title"] = text
                if self.graph_widget.current_graph == 5:
                    self.current_job.graph_5["title"] = text
                if self.graph_widget.current_graph == 6:
                    self.current_job.graph_6["title"] = text
                if self.graph_widget.current_graph == 7:
                    self.current_job.graph_7["title"] = text
                if self.graph_widget.current_graph == 8:
                    self.current_job.graph_8["title"] = text

    def on_x_title_text(self, text):
        """called when x_title text input is changed"""
        # If a job is selected
        if self.current_job is not None:
            # If bulk checkboc is ticked
            if self.my_checkbox.active:
                # Update all jobs
                for job in self.fg2_scroll.grid_layout.children:
                    if self.graph_widget.current_graph == 1:
                        job.graph_1["x_title"] = text
                    if self.graph_widget.current_graph == 2:
                        job.graph_2["x_title"] = text
                    if self.graph_widget.current_graph == 3:
                        job.graph_3["x_title"] = text
                    if self.graph_widget.current_graph == 4:
                        job.graph_4["x_title"] = text
                    if self.graph_widget.current_graph == 5:
                        job.graph_5["x_title"] = text
                    if self.graph_widget.current_graph == 6:
                        job.graph_6["x_title"] = text
                    if self.graph_widget.current_graph == 7:
                        job.graph_7["x_title"] = text
                    if self.graph_widget.current_graph == 8:
                        job.graph_8["x_title"] = text
            else:
                # Upadte the job's title
                if self.graph_widget.current_graph == 1:
                    self.current_job.graph_1["x_title"] = text
                if self.graph_widget.current_graph == 2:
                    self.current_job.graph_2["x_title"] = text
                if self.graph_widget.current_graph == 3:
                    self.current_job.graph_3["x_title"] = text
                if self.graph_widget.current_graph == 4:
                    self.current_job.graph_4["x_title"] = text
                if self.graph_widget.current_graph == 5:
                    self.current_job.graph_5["x_title"] = text
                if self.graph_widget.current_graph == 6:
                    self.current_job.graph_6["x_title"] = text
                if self.graph_widget.current_graph == 7:
                    self.current_job.graph_7["x_title"] = text
                if self.graph_widget.current_graph == 8:
                    self.current_job.graph_8["x_title"] = text

    def on_y_title_text(self, text):
        """called when y_title text input is changed"""
        # If a job is selected
        if self.current_job is not None:
            # If bulk checkboc is ticked
            if self.my_checkbox.active:
                # Update all jobs
                for job in self.fg2_scroll.grid_layout.children:
                    if self.graph_widget.current_graph == 1:
                        job.graph_1["y_title"] = text
                    if self.graph_widget.current_graph == 2:
                        job.graph_2["y_title"] = text
                    if self.graph_widget.current_graph == 3:
                        job.graph_3["y_title"] = text
                    if self.graph_widget.current_graph == 4:
                        job.graph_4["y_title"] = text
                    if self.graph_widget.current_graph == 5:
                        job.graph_5["y_title"] = text
                    if self.graph_widget.current_graph == 6:
                        job.graph_6["y_title"] = text
                    if self.graph_widget.current_graph == 7:
                        job.graph_7["y_title"] = text
                    if self.graph_widget.current_graph == 8:
                        job.graph_8["y_title"] = text
            else:
                # Upadte the job's title
                if self.graph_widget.current_graph == 1:
                    self.current_job.graph_1["y_title"] = text
                if self.graph_widget.current_graph == 2:
                    self.current_job.graph_2["y_title"] = text
                if self.graph_widget.current_graph == 3:
                    self.current_job.graph_3["y_title"] = text
                if self.graph_widget.current_graph == 4:
                    self.current_job.graph_4["y_title"] = text
                if self.graph_widget.current_graph == 5:
                    self.current_job.graph_5["y_title"] = text
                if self.graph_widget.current_graph == 6:
                    self.current_job.graph_6["y_title"] = text
                if self.graph_widget.current_graph == 7:
                    self.current_job.graph_7["y_title"] = text
                if self.graph_widget.current_graph == 8:
                    self.current_job.graph_8["y_title"] = text

    def on_y_min_text(self, text):
        """called when ymin input is changed"""
        # If a job is selected
        if self.current_job is not None:
            # Check if valid float
            try:
                # Try convert to float
                float(text)
            # If invalid, just use 0
            except ValueError:
                text = 0
            # If bulk checkboc is ticked
            if self.my_checkbox.active:
                # Update all jobs
                for job in self.pf1_scroll.grid_layout.children:
                    if self.graph_widget.current_graph == 1:
                        job.graph_1["y_min"] = float(text)
                    if self.graph_widget.current_graph == 2:
                        job.graph_2["y_min"] = float(text)
                    if self.graph_widget.current_graph == 3:
                        job.graph_3["y_min"] = float(text)
                    if self.graph_widget.current_graph == 4:
                        job.graph_4["y_min"] = float(text)
                    if self.graph_widget.current_graph == 5:
                        job.graph_5["y_min"] = float(text)
                    if self.graph_widget.current_graph == 6:
                        job.graph_6["y_min"] = float(text)
                    if self.graph_widget.current_graph == 7:
                        job.graph_7["y_min"] = float(text)
                    if self.graph_widget.current_graph == 8:
                        job.graph_8["y_min"] = float(text)
            else:
                # Upadte the job's title
                if self.graph_widget.current_graph == 1:
                    self.current_job.graph_1["y_min"] = float(text)
                if self.graph_widget.current_graph == 2:
                    self.current_job.graph_2["y_min"] = float(text)
                if self.graph_widget.current_graph == 3:
                    self.current_job.graph_3["y_min"] = float(text)
                if self.graph_widget.current_graph == 4:
                    self.current_job.graph_4["y_min"] = float(text)
                if self.graph_widget.current_graph == 5:
                    self.current_job.graph_5["y_min"] = float(text)
                if self.graph_widget.current_graph == 6:
                    self.current_job.graph_6["y_min"] = float(text)
                if self.graph_widget.current_graph == 7:
                    self.current_job.graph_7["y_min"] = float(text)
                if self.graph_widget.current_graph == 8:
                    self.current_job.graph_8["y_min"] = float(text)

    def on_y_max_text(self, text):
        """called when ymin input is changed"""
        # If a job is selected
        if self.current_job is not None:
            # Check if valid float
            try:
                # Try convert to float
                float(text)
            # If invalid, just use 0
            except ValueError:
                text = 0
            # If bulk checkboc is ticked
            if self.my_checkbox.active:
                # Update all jobs
                for job in self.pf1_scroll.grid_layout.children:
                    if self.graph_widget.current_graph == 1:
                        job.graph_1["y_max"] = float(text)
                    if self.graph_widget.current_graph == 2:
                        job.graph_2["y_max"] = float(text)
                    if self.graph_widget.current_graph == 3:
                        job.graph_3["y_max"] = float(text)
                    if self.graph_widget.current_graph == 4:
                        job.graph_4["y_max"] = float(text)
                    if self.graph_widget.current_graph == 5:
                        job.graph_5["y_max"] = float(text)
                    if self.graph_widget.current_graph == 6:
                        job.graph_6["y_max"] = float(text)
                    if self.graph_widget.current_graph == 7:
                        job.graph_7["y_max"] = float(text)
                    if self.graph_widget.current_graph == 8:
                        job.graph_8["y_max"] = float(text)
            else:
                # Upadte the job's title
                if self.graph_widget.current_graph == 1:
                    self.current_job.graph_1["y_max"] = float(text)
                if self.graph_widget.current_graph == 2:
                    self.current_job.graph_2["y_max"] = float(text)
                if self.graph_widget.current_graph == 3:
                    self.current_job.graph_3["y_max"] = float(text)
                if self.graph_widget.current_graph == 4:
                    self.current_job.graph_4["y_max"] = float(text)
                if self.graph_widget.current_graph == 5:
                    self.current_job.graph_5["y_max"] = float(text)
                if self.graph_widget.current_graph == 6:
                    self.current_job.graph_6["y_max"] = float(text)
                if self.graph_widget.current_graph == 7:
                    self.current_job.graph_7["y_max"] = float(text)
                if self.graph_widget.current_graph == 8:
                    self.current_job.graph_8["y_max"] = float(text)

    def on_gt1_checkbox(self):
        """called when check box 1 is changed"""
        # If bulk checkboc is ticked
        if self.my_checkbox.active:
            # Update all jobs
            for job in self.fg2_scroll.grid_layout.children:
                job.making_t_for_graph = self.gt1_checkbox.state == "down"
        # If a job is selected
        if self.current_job is not None:
            # Upadte the job's title
            self.current_job.making_t_for_graph = self.gt1_checkbox.state == "down"

    def on_gt2_checkbox(self):
        """called when check box 2 is changed"""
        # If bulk checkboc is ticked
        if self.my_checkbox.active:
            # Update all jobs
            for job in self.fg2_scroll.grid_layout.children:
                job.making_xy_for_graph = self.gt2_checkbox.state == "down"
        # If a job is selected
        if self.current_job is not None:
            # Upadte the job's title
            self.current_job.making_xy_for_graph = self.gt2_checkbox.state == "down"

    def on_gt3_checkbox(self):
        """called when check box 3 is changed"""
        # If bulk checkboc is ticked
        if self.my_checkbox.active:
            # Update all jobs
            for job in self.fg2_scroll.grid_layout.children:
                job.making_x_pos_graph = self.gt3_checkbox.state == "down"
        # If a job is selected
        if self.current_job is not None:
            # Upadte the job's title
            self.current_job.making_x_pos_graph = self.gt3_checkbox.state == "down"

    def on_gt4_checkbox(self):
        """called when check box 4 is changed"""
        # If bulk checkboc is ticked
        if self.my_checkbox.active:
            # Update all jobs
            for job in self.fg2_scroll.grid_layout.children:
                job.making_y_for_graph = self.gt4_checkbox.state == "down"
        # If a job is selected
        if self.current_job is not None:
            # Upadte the job's title
            self.current_job.making_y_for_graph = self.gt4_checkbox.state == "down"

    def on_gt5_checkbox(self):
        """called when check box 5 is changed"""
        # If bulk checkboc is ticked
        if self.my_checkbox.active:
            # Update all jobs
            for job in self.fg2_scroll.grid_layout.children:
                job.making_x_pos_graph = self.gt5_checkbox.state == "down"
        # If a job is selected
        if self.current_job is not None:
            # Upadte the job's title
            self.current_job.making_x_pos_graph = self.gt5_checkbox.state == "down"

    def on_gt6_checkbox(self):
        """called when check box 6 is changed"""
        # If bulk checkboc is ticked
        if self.my_checkbox.active:
            # Update all jobs
            for job in self.fg2_scroll.grid_layout.children:
                job.making_y_pos_graph = self.gt6_checkbox.state == "down"
        # If a job is selected
        if self.current_job is not None:
            # Upadte the job's title
            self.current_job.making_y_pos_graph = self.gt6_checkbox.state == "down"

    def on_gt7_checkbox(self):
        """called when check box 7 is changed"""
        # If bulk checkboc is ticked
        if self.my_checkbox.active:
            # Update all jobs
            for job in self.fg2_scroll.grid_layout.children:
                job.making_dfx_graph = self.gt7_checkbox.state == "down"
        # If a job is selected
        if self.current_job is not None:
            # Upadte the job's title
            self.current_job.making_dfx_graph = self.gt7_checkbox.state == "down"

    def on_gt8_checkbox(self):
        """called when check box 8 is changed"""
        # If bulk checkboc is ticked
        if self.my_checkbox.active:
            # Update all jobs
            for job in self.fg2_scroll.grid_layout.children:
                job.making_dfy_graph = self.gt8_checkbox.state == "down"
        # If a job is selected
        if self.current_job is not None:
            # Upadte the job's title
            self.current_job.making_dfy_graph = self.gt8_checkbox.state == "down"

    def on_svg_checkbox(self):
        """called when check box svg is changed"""
        # If bulk checkboc is ticked
        if self.my_checkbox.active:
            # Update all jobs
            for job in self.fg2_scroll.grid_layout.children:
                job.making_svg_graph = self.svg_checkbox.state == "down"
        # If a job is selected
        if self.current_job is not None:
            # Upadte the job's title
            self.current_job.making_svg_graph = self.svg_checkbox.state == "down"

    def on_png_checkbox(self):
        """called when check box png is changed"""
        # If bulk checkboc is ticked
        if self.my_checkbox.active:
            # Update all jobs
            for job in self.fg2_scroll.grid_layout.children:
                job.making_png_graph = self.png_checkbox.state == "down"
        # If a job is selected
        if self.current_job is not None:
            # Upadte the job's title
            self.current_job.making_png_graph = self.png_checkbox.state == "down"

    def on_back_btn(self):
        """called by back btn
        - checks if there are an jobs
        - if any jobs it makes a popup"""
        # If there are any jobs
        if len(self.fg2_scroll.grid_layout.children) > 0:
            # Make pop up - asks if you are sure you want to exit
            popup = BackPopup(self.clear_jobs, "FG2")
            popup.open()
        # If there are no jobs
        else:
            # Make pop up
            popup = BackPopup(self.clear_jobs, "FG2")
            # Immediately close it (which triggers the app to go back)
            popup.on_answer("yes")

    def clear_jobs(self):
        """simply empties the job list
        - this has to be a while loop, because the list changes size while looping"""
        # While there are still jobs
        while len(self.fg2_scroll.grid_layout.children) != 0:
            # Remove the first job using on_x_btn
            self.fg2_scroll.on_x_btn(self.fg2_scroll.grid_layout.children[0])
        # Reset the current graph and checkbox
        self.graph_widget.current_graph = 1
        self.graph_widget.graph_label.text = str(self.graph_widget.current_graph) + "/8"
        self.my_checkbox.active = False


class FG2ScrollView(ScrollView):
    """scrolling widget in FG2"""

    def __init__(self, **kwargs):
        """init method for the scrolling widget in FG1"""
        # Call ScrollView init method
        super(FG2ScrollView, self).__init__(**kwargs)

    def on_x_btn(self, box):
        """called when an x button on a box is pressed or using clear_jobs
        - disables the layouts because there is nothing selected now
        - removes the jobs
        - updates visuals"""
        # Disabled layouts
        self.fg2_window.param_grid_layout.disabled = True
        self.fg2_window.name_grid_layout.disabled = True
        # Remove that job
        self.grid_layout.remove_widget(box)
        # Update current job to none
        self.fg2_window.current_job = None
        # Update visual stuff
        self.fg2_window.update_fields()
        self.fg2_window.update_job_selected()
        self.fg2_window.graph_widget.update_widget()


class FG2JobListBox(Button):
    """job widget on the FG1ScrollView widget"""

    def __init__(self, col_vals, job_name, file_location, fg2_window, **kwargs):
        """init method for the job widgets on the scrolling widget in FG1"""
        # Save the fg2_window as a reference
        self.fg2_window = fg2_window
        # Save app as an attribute
        self.app = App.get_running_app()
        # Call Button init method
        super().__init__(**kwargs)
        # Save file location
        self.file_location = file_location
        # Set the job name
        self.name = job_name
        # Grab the date of creation of the file
        if os.path.exists(file_location):
            self.date = datetime.fromtimestamp(getctime(file_location)).strftime(
                "%d/%m/%Y"
            )
        else:
            self.date = "File no longer exists"
        # Add column vals
        (
            self.x_col,
            self.y_col,
            self.t_col,
            self.tf_col,
            self.xf_col,
            self.yf_col,
            self.dfx_col,
            self.dfy_col,
        ) = [[float(v) for v in l] for l in col_vals]
        # All the parameters
        self.graph_1 = {
            "title": self.app.DEFAULT_TITLES[("t", 1)],
            "x_title": self.app.DEFAULT_TITLES[("x_t", 1)],
            "y_title": self.app.DEFAULT_TITLES[("y_t", 1)],
            "y_min": min(self.tf_col),
            "y_max": max(self.tf_col),
        }
        self.graph_2 = {
            "title": self.app.DEFAULT_TITLES[("t", 2)],
            "x_title": self.app.DEFAULT_TITLES[("x_t", 2)],
            "y_title": self.app.DEFAULT_TITLES[("y_t", 2)],
            "y_min": min(self.xf_col + self.yf_col),
            "y_max": max(self.xf_col + self.yf_col),
        }
        self.graph_3 = {
            "title": self.app.DEFAULT_TITLES[("t", 3)],
            "x_title": self.app.DEFAULT_TITLES[("x_t", 3)],
            "y_title": self.app.DEFAULT_TITLES[("y_t", 3)],
            "y_min": min(self.xf_col + self.yf_col),
            "y_max": max(self.xf_col + self.yf_col),
        }
        self.graph_4 = {
            "title": self.app.DEFAULT_TITLES[("t", 4)],
            "x_title": self.app.DEFAULT_TITLES[("x_t", 4)],
            "y_title": self.app.DEFAULT_TITLES[("y_t", 4)],
            "y_min": min(self.xf_col + self.yf_col),
            "y_max": max(self.xf_col + self.yf_col),
        }
        self.graph_5 = {
            "title": self.app.DEFAULT_TITLES[("t", 5)],
            "x_title": self.app.DEFAULT_TITLES[("x_t", 5)],
            "y_title": self.app.DEFAULT_TITLES[("y_t", 5)],
            "y_min": min(self.x_col),
            "y_max": max(self.x_col),
        }
        self.graph_6 = {
            "title": self.app.DEFAULT_TITLES[("t", 6)],
            "x_title": self.app.DEFAULT_TITLES[("x_t", 6)],
            "y_title": self.app.DEFAULT_TITLES[("y_t", 6)],
            "y_min": min(self.y_col),
            "y_max": max(self.y_col),
        }
        self.graph_7 = {
            "title": self.app.DEFAULT_TITLES[("t", 7)],
            "x_title": self.app.DEFAULT_TITLES[("x_t", 7)],
            "y_title": self.app.DEFAULT_TITLES[("y_t", 7)],
            "y_min": min(self.dfx_col),
            "y_max": max(self.dfx_col),
        }
        self.graph_8 = {
            "title": self.app.DEFAULT_TITLES[("t", 8)],
            "x_title": self.app.DEFAULT_TITLES[("x_t", 8)],
            "y_title": self.app.DEFAULT_TITLES[("y_t", 8)],
            "y_min": min(self.dfy_col),
            "y_max": max(self.dfy_col),
        }
        # Set booleans for which graphs
        self.making_t_for_graph = True
        self.making_xy_for_graph = True
        self.making_x_for_graph = True
        self.making_y_for_graph = True
        self.making_x_pos_graph = True
        self.making_y_pos_graph = True
        self.making_dfx_graph = True
        self.making_dfy_graph = True
        # Set booleans for which file types
        self.making_svg_graph = True
        self.making_png_graph = False
        # Set the default plot type
        self.plot_type = "Scatter"
        # This job should be selected at creation
        self.is_selected = True

    def on_press(self):
        """called when the job box is pressed
        - sets this job to be current
        - enables layouts
        - updates visuals
        - scrolls textboxes back to the start"""
        # Temporarily uncheck mycheckbox (stops unwanted updating of fields)
        checkstate = self.fg2_window.my_checkbox.active and True
        self.fg2_window.my_checkbox.active = False
        # This is now the current job
        self.fg2_window.current_job = self
        # Enable layouts
        self.fg2_window.param_grid_layout.disabled = False
        self.fg2_window.name_grid_layout.disabled = False
        # Update the visuals
        self.fg2_window.update_fields()
        self.fg2_window.update_job_selected()
        self.fg2_window.graph_widget.update_widget()
        # Reset texbox positions
        self.fg2_window.name_input.scroll_x = 0
        # Return checkbox to previous state
        self.fg2_window.my_checkbox.active = checkstate

    def update_is_selected(self):
        """update the is_selected attribute, which affects visuals"""
        # If this job is selected
        if self.fg2_window.current_job == self:
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


class GraphWidget(Widget):
    """The widget which holds the graph image"""

    def __init__(self, **kwargs):
        """init method for the graph widget in FG2"""
        # Call Widget init method
        super(GraphWidget, self).__init__(**kwargs)
        # Set the current graph to the first one
        self.current_graph = 1
        # Initialise the plot
        self.create_plot()
        # Save app as an attribute
        self.app = App.get_running_app()

    def on_left_arrow_press(self):
        """called on the press of the left graph arrow"""
        # If not on graph 1
        if self.current_graph > 1:
            # Move to the next graph leftwards
            self.current_graph -= 1
            # Update the fields
            self.fg2_window.update_fields()
            # Update the graph
            self.update_widget()
            # Update the graph number
            self.graph_label.text = str(self.current_graph) + "/8"

    def on_right_arrow_press(self):
        """called on the press of the right graph arrow"""
        # If not on graph 8
        if self.current_graph < len(self.app.DEFAULT_TITLES) // 3:
            # Move to the next graph rightwards
            self.current_graph += 1
            # Update the fields
            self.fg2_window.update_fields()
            # Update the graph
            self.update_widget()
            # Update the graph number
            self.graph_label.text = str(self.current_graph) + "/8"

    def create_plot(self):
        """initialises the matplotlib plot"""
        self.fig, self.ax = plt.subplots(figsize=(6, 4.5))

    def update_widget(self, focus=None):
        """updates the graph widget
        - when called directly by a text input widget
        the widget's focus attribute is passed to this method
        - if the input is not in focus (the input is not selected)
        - this is because we don't want the graph to update until
        we have stopped typing"""
        # If there is a current job and the input is not in focus
        if self.fg2_window.current_job is not None and focus != True:
            # Update the plot
            self.update_plot()
            self.display_plot()

    def update_plot(self):
        """gets the current graph's features and updates the plot"""
        # Grab the current graph's features
        y_list2 = None  # There may or may not be a second list of data
        if self.current_graph == 1:
            x_list = [round(float(num), 2) for num in self.fg2_window.current_job.t_col]
            y_list = [
                round(float(num), 1) for num in self.fg2_window.current_job.tf_col
            ]
            x_label = self.fg2_window.current_job.graph_1["x_title"]
            y_label = self.fg2_window.current_job.graph_1["y_title"]
            title_label = self.fg2_window.current_job.graph_1["title"]
            y_min = self.fg2_window.current_job.graph_1["y_min"]
            y_max = self.fg2_window.current_job.graph_1["y_max"]
        elif self.current_graph == 2:
            x_list = [round(float(num), 2) for num in self.fg2_window.current_job.t_col]
            y_list = [
                round(float(num), 1) for num in self.fg2_window.current_job.xf_col
            ]
            y_list2 = [
                round(float(num), 1) for num in self.fg2_window.current_job.yf_col
            ]
            x_label = self.fg2_window.current_job.graph_2["x_title"]
            y_label = self.fg2_window.current_job.graph_2["y_title"]
            title_label = self.fg2_window.current_job.graph_2["title"]
            y_min = self.fg2_window.current_job.graph_2["y_min"]
            y_max = self.fg2_window.current_job.graph_2["y_max"]
        elif self.current_graph == 3:
            x_list = [round(float(num), 2) for num in self.fg2_window.current_job.t_col]
            y_list = [
                round(float(num), 1) for num in self.fg2_window.current_job.xf_col
            ]
            x_label = self.fg2_window.current_job.graph_3["x_title"]
            y_label = self.fg2_window.current_job.graph_3["y_title"]
            title_label = self.fg2_window.current_job.graph_3["title"]
            y_min = self.fg2_window.current_job.graph_3["y_min"]
            y_max = self.fg2_window.current_job.graph_3["y_max"]
        elif self.current_graph == 4:
            x_list = [round(float(num), 2) for num in self.fg2_window.current_job.t_col]
            y_list = [
                round(float(num), 1) for num in self.fg2_window.current_job.yf_col
            ]
            x_label = self.fg2_window.current_job.graph_4["x_title"]
            y_label = self.fg2_window.current_job.graph_4["y_title"]
            title_label = self.fg2_window.current_job.graph_4["title"]
            y_min = self.fg2_window.current_job.graph_4["y_min"]
            y_max = self.fg2_window.current_job.graph_4["y_max"]
        elif self.current_graph == 5:
            x_list = [round(float(num), 2) for num in self.fg2_window.current_job.t_col]
            y_list = [round(float(num), 2) for num in self.fg2_window.current_job.x_col]
            x_label = self.fg2_window.current_job.graph_5["x_title"]
            y_label = self.fg2_window.current_job.graph_5["y_title"]
            title_label = self.fg2_window.current_job.graph_5["title"]
            y_min = self.fg2_window.current_job.graph_5["y_min"]
            y_max = self.fg2_window.current_job.graph_5["y_max"]
        elif self.current_graph == 6:
            x_list = [round(float(num), 2) for num in self.fg2_window.current_job.t_col]
            y_list = [round(float(num), 2) for num in self.fg2_window.current_job.y_col]
            x_label = self.fg2_window.current_job.graph_6["x_title"]
            y_label = self.fg2_window.current_job.graph_6["y_title"]
            title_label = self.fg2_window.current_job.graph_6["title"]
            y_min = self.fg2_window.current_job.graph_6["y_min"]
            y_max = self.fg2_window.current_job.graph_6["y_max"]
        elif self.current_graph == 7:
            x_list = [round(float(num), 2) for num in self.fg2_window.current_job.t_col]
            y_list = [
                round(float(num), 1) for num in self.fg2_window.current_job.dfx_col
            ]
            x_label = self.fg2_window.current_job.graph_7["x_title"]
            y_label = self.fg2_window.current_job.graph_7["y_title"]
            title_label = self.fg2_window.current_job.graph_7["title"]
            y_min = self.fg2_window.current_job.graph_7["y_min"]
            y_max = self.fg2_window.current_job.graph_7["y_max"]
        elif self.current_graph == 8:
            x_list = [round(float(num), 2) for num in self.fg2_window.current_job.t_col]
            y_list = [
                round(float(num), 1) for num in self.fg2_window.current_job.dfy_col
            ]
            x_label = self.fg2_window.current_job.graph_8["x_title"]
            y_label = self.fg2_window.current_job.graph_8["y_title"]
            title_label = self.fg2_window.current_job.graph_8["title"]
            y_min = self.fg2_window.current_job.graph_8["y_min"]
            y_max = self.fg2_window.current_job.graph_8["y_max"]
        # Clear the plot
        plt.cla()
        # Set data ranges
        self.ax.set_ylim(
            [
                float(y_min) - 0.05 * (float(y_max) - float(y_min)),
                float(y_max) + 0.05 * (float(y_max) - float(y_min)),
            ]
        )
        # If line plot
        if self.fg2_window.current_job.plot_type == "Line":
            # If two lists of data points
            if y_list2 is not None:
                # Label the two lists
                self.ax.plot(x_list, y_list, label="x-direction", clip_on=False)
                self.ax.plot(x_list, y_list2, label="y-direction", clip_on=False)
                # Add the legend
                self.ax.legend()
            # If only one list of data points
            else:
                self.ax.plot(x_list, y_list)
        # If dot plot
        elif self.fg2_window.current_job.plot_type == "Scatter":
            # If two lists of data points
            if y_list2 is not None:
                # Label the two lists
                self.ax.scatter(x_list, y_list, label="x-direction")
                self.ax.scatter(x_list, y_list2, label="y-direction")
                # Add the legend
                self.ax.legend()
            # If only one list of data points
            else:
                self.ax.scatter(x_list, y_list)
        # If bar plot
        elif self.fg2_window.current_job.plot_type == "Bar":
            # If two lists of data points
            if y_list2 is not None:
                # Label the two lists
                self.ax.bar(x_list, y_list, label="x-direction")
                self.ax.bar(x_list, y_list2, label="y-direction")
                # Add the legend
                self.ax.legend()
            # If only one list of data points
            else:
                self.ax.bar(x_list, y_list)
        # Add labels to the x and y axis
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        # Add a title to the graph
        self.ax.set_title(title_label)

    def grab_figure(self, plot_dpi=150):
        """converts the plot into a png image
        - returns a np array containing the image"""
        # Convert the figure to a PNG image
        buf = BytesIO()
        self.fig.savefig(
            buf, format="png", facecolor="white", dpi=plot_dpi, bbox_inches="tight"
        )
        buf.seek(0)
        image_data = buf.read()
        # Close the buffer
        buf.close()
        # Use PIL to read the image data and convert it to a Kivy-compatible format
        pil_image = PilImage.open(BytesIO(image_data))
        # Convert the PIL image to a numpy array
        np_image = np.array(pil_image)
        return np_image

    def display_plot(self):
        """grad the png of the plot and display it as a Kivy texture"""
        # Get fig as numpy png
        np_image = self.grab_figure()
        # Flip upside down because Kivy uses a reversed y axis
        np_image = np.flipud(np_image)
        # Create a Kivy texture from the numpy array
        kivy_texture = Texture.create(
            size=(np_image.shape[1], np_image.shape[0]), colorfmt="rgba"
        )
        kivy_texture.blit_buffer(np_image.flatten(), colorfmt="rgba", bufferfmt="ubyte")
        # Update the Kivy Image widget to display the graph image
        self.image_widget.texture = kivy_texture

    def export_current_plot(self, plot_dpi, new_file_loc, svg, png):
        """takes a file location and file types
        - exports the current graph at that location in those file types"""
        # If exporting a png file
        if png:
            # Update the plot
            self.update_plot()
            # Get fig as numpy png
            np_image = self.grab_figure(plot_dpi=plot_dpi)
            # Export the graph image to the given filename
            imageio.imwrite(new_file_loc + ".png", np_image)
        # If exporting a svg file
        if svg:
            # Update the plot
            self.update_plot()
            # Save the fig as an svg file to the given filename
            self.fig.savefig(new_file_loc + ".svg", bbox_inches="tight", format="svg")
