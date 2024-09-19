"""
Module: Kivy popup widgets for the app
Program: Pillar Centroid Tracker
Author: Haig Bishop (hbi34@uclive.ac.nz)
"""

# Kivy imports
from kivy.app import App
from kivy.uix.popup import Popup

# Import local modules
from force_conversion import force_convert_job
from file_management import (
    write_pos_force_file,
    rename_file_force,
    write_pos_file,
    rename_file_pos,
)


class BackPopup(Popup):
    """A custom Popup object for going back a page"""

    def __init__(self, clear_jobs, screen, **kwargs):
        """init method for BackPopup"""
        # Save the screen, so we know what screen we are on
        self.screen = screen
        # Call Popup init method
        super(BackPopup, self).__init__(**kwargs)
        # Save the clear_jobs method for when user pressed 'yes'
        self.clear_jobs = clear_jobs

    def on_answer(self, answer):
        """called when user presses 'yes' or 'no'"""
        # If they said "yes go back"
        if answer == "yes":
            # Empty the job list
            self.clear_jobs()
            # Determine new screen on what the current screen is
            if self.screen == "FG2":
                new_screen = "FG1"
            elif self.screen == "IP2":
                new_screen = "IP1"
            elif self.screen == "PS2":
                new_screen = "PS1"
            else:
                new_screen = "main"
            # Change screen
            app = App.get_running_app()
            app.root.current = new_screen
            app.root.transition.direction = "right"
            # Close popup
            self.dismiss()
        # If they said "no cancel"
        else:
            # Close popup
            self.dismiss()


class ErrorPopup(Popup):
    """A custom Popup object for displaying an error screen
    - this is just for invalid data
    - the popup doesnt do anything, it just tells the user something"""

    def on_answer(self, answer):
        """called when user presses 'ok'"""
        if answer == "ok":
            # Close popup
            self.dismiss()


class TrackPopup(Popup):
    """A custom Popup object for continuing to the next page for the IP2 screen"""

    def __init__(
        self, old_clear_jobs, clear_jobs, old_scroll, ip2_window, new_window, **kwargs
    ):
        """init method for TrackPopup"""
        # Call Popup init method
        super(TrackPopup, self).__init__(**kwargs)
        # Save the clear_jobs method for when user pressed 'yes'
        # (there are actually 2 here for IP1 & IP2)
        self.old_clear_jobs = old_clear_jobs
        self.clear_jobs = clear_jobs
        # The old/current scrollview (so we can access jobs)
        self.old_scroll = old_scroll
        # Save a reference to the old/current window
        self.ip2_window = ip2_window
        # Save a reference to the next window
        self.new_window = new_window
        # Get app reference
        self.app = App.get_running_app()

    def on_answer(self, answer):
        """called when user presses 'yes' or 'no'
        - if 'yes', then it will trigger the tracking of the images"""
        # If they said "yes continue"
        if answer == "yes":
            #  trigger the tracking of the images
            # (this will start the loading screen + schedule the export to start)
            self.ip2_window.start_loading()
            self.dismiss()
        # If they said "no cancel"
        else:
            # Close popup
            self.dismiss()


class IP2SuccessPopup(Popup):
    """A custom Popup object for after tracking the posisition for the IP2 screen
    - user can either exit to main menu or continure to PS2"""

    def __init__(
        self,
        new_file_locs,
        folder_locs,
        position_datas,
        old_old_clear_jobs,
        old_clear_jobs,
        new_window,
        radii,
        **kwargs
    ):
        """init method for IP2SuccessPopup"""
        # Call Popup init method
        super(IP2SuccessPopup, self).__init__(**kwargs)
        # Take job data from the IP2 window
        self.new_file_locs = new_file_locs  # POSTIITON FILES
        self.folder_locs = folder_locs  # IMAGE FOLDERS
        self.position_datas = position_datas
        self.radii = radii
        # Save the clear_jobs method for when user pressed 'yes'
        # (there are actually 2 here for IP1 & IP2)
        self.old_old_clear_jobs = old_old_clear_jobs
        self.old_clear_jobs = old_clear_jobs
        # Save the next screen (PS2)
        self.new_window = new_window

    def on_answer(self, answer):
        '''called when user presses "exit" or "continue"'''
        # If user chose to exit to main menu
        if answer == "exit":
            # Change screen to main
            app = App.get_running_app()
            app.root.current = "main"
            app.root.transition.direction = "right"
            # Empty the old job lists
            self.old_old_clear_jobs()
            self.old_clear_jobs()
            # Close popup
            self.dismiss()
        # If user chose to continue to PS2
        else:
            # Add all new jobs to PS2
            self.new_window.import_jobs(
                self.folder_locs, self.new_file_locs, self.position_datas, self.radii
            )
            # Grab the last job added
            final_job = self.new_window.ps2_scroll.grid_layout.children[-1]
            # Change screen
            app = App.get_running_app()
            app.root.current = "PS2"
            app.root.transition.direction = "up"
            # Empty the old job lists
            self.old_old_clear_jobs()
            self.old_clear_jobs()
            # Close popup
            self.dismiss()
            # Set as current job
            self.new_window.current_job = final_job
            # Update everything visually
            self.new_window.update_job_selected()
            self.new_window.image_widget.update_image()
            self.new_window.update_fields()


class VerifyPopup(Popup):
    """A custom Popup object for continuing to the next page for the PS2 screen"""

    def __init__(self, old_clear_jobs, clear_jobs, old_scroll, new_window, **kwargs):
        """init method for VerifyPopup"""
        # Call Popup init method
        super(VerifyPopup, self).__init__(**kwargs)
        # Save the clear_jobs method for when user pressed 'yes'
        # (there are actually 2 here for PS1 & PS2)
        self.old_clear_jobs = old_clear_jobs
        self.clear_jobs = clear_jobs
        # The old/current scrollview (so we can access jobs)
        self.old_scroll = old_scroll
        # Save a reference to the next window
        self.new_window = new_window
        # Get app reference
        self.app = App.get_running_app()
        print("verify initialised")

    def on_answer(self, answer, do_all=False):
        """called when user presses 'yes' or 'no'
        - if 'yes', then it will write the pos files from PS2 again
        - will only write new pos files if they were updated or do_all=True"""
        # If they said "yes continue"
        if answer == "yes":
            new_file_locs = []
            # For each job
            for job in self.old_scroll.grid_layout.children:
                print("1 job", job.updated)
                # Write new file if any updates were made or if do_all is true
                # If the job was updated by the user or we want to do all
                if job.updated or do_all:
                    # Get new positions
                    position_data = job.position_data
                    # Get a file name/location to write a force file
                    new_file_loc = rename_file_pos(
                        job.folder_location, job.name, updated=True
                    )
                    print(new_file_loc)
                    new_file_locs.append(new_file_loc)
                    # Write that pos file
                    write_pos_file(new_file_loc, position_data)
                else:
                    # Get the old file location
                    new_file_locs.append(job.original_position_file_location)
            # Make second pop up - alerts of files saved
            popup = PS2SuccessPopup(
                new_file_locs, self.old_clear_jobs, self.clear_jobs, self.new_window
            )
            popup.success_label.text = (
                str(len(new_file_locs))
                + " Files saved successfully.\nCalculate Forces or exit?"
            )
            popup.open()
            self.clear_jobs()
            # Close popup
            self.dismiss()
        # If they said "no cancel"
        else:
            # Close popup
            self.dismiss()


class PS2SuccessPopup(Popup):
    """A custom Popup object for after verifying the positions on the PS2 screen
    - user can either exit to main menu or continure to PF1"""

    def __init__(
        self, new_file_locs, old_old_clear_jobs, old_clear_jobs, new_window, **kwargs
    ):
        """init method for PS2SuccessPopup"""
        # Call Popup init method
        super(PS2SuccessPopup, self).__init__(**kwargs)
        # Save the clear_jobs method for when user pressed 'yes'
        # (there are actually 2 here for IP1 & IP2)
        self.old_old_clear_jobs = old_old_clear_jobs
        self.old_clear_jobs = old_clear_jobs
        # Save the next screen (PF1)
        self.new_window = new_window
        # Take job data from the PS2 window
        self.new_file_locs = new_file_locs  # POSTIITON FILES

    def on_answer(self, answer):
        '''called when user presses "exit" or "continue"'''
        # If user chose to exit to main menu
        if answer == "exit":
            # Change screen to main
            app = App.get_running_app()
            app.root.current = "main"
            app.root.transition.direction = "right"
            # Close popup
            self.dismiss()
            # Empty the old job lists
            self.old_old_clear_jobs()
            self.old_clear_jobs()
        # If user chose to continue to PF1
        else:
            # Add all new jobs
            self.new_window.selected(self.new_file_locs)
            # Grab the last job added
            final_job = self.new_window.pf1_scroll.grid_layout.children[-1]
            # Change screen
            app = App.get_running_app()
            app.root.current = "PF1"
            app.root.transition.direction = "up"
            # Close popup
            self.dismiss()
            # Set as current job
            self.new_window.current_job = final_job
            # Update everything visually
            self.new_window.update_job_selected()


class ContinuePopup(Popup):
    """A custom Popup object for continuing to the next page for the PF1 window"""

    def __init__(self, clear_jobs, old_scroll, new_window, **kwargs):
        """init method for ContinuePopup"""
        # Call Popup init method
        super(ContinuePopup, self).__init__(**kwargs)
        # Save the clear_jobs method for when user pressed 'yes'
        self.clear_jobs = clear_jobs
        # The old/current scrollview (so we can access jobs)
        self.old_scroll = old_scroll
        # Save a reference to the next window
        self.new_window = new_window
        # Get app reference
        self.app = App.get_running_app()

    def on_answer(self, answer):
        """called when user presses 'yes' or 'no'
        - if 'yes', then it will calculate forces and write files"""
        # If they said "yes continue"
        if answer == "yes":
            new_file_locs = []
            # For each job
            for job in self.old_scroll.grid_layout.children:
                # Calculate forces
                (
                    frame_nums,
                    t_vals,
                    force_x,
                    force_y,
                    force_total,
                    averageF_x,
                    averageF_y,
                    averageF_total,
                    delta_Fx,
                    delta_Fy,
                    delta_totalF,
                ) = force_convert_job(job)
                # Get a file name/location to write a force file
                new_file_loc = rename_file_force(job.file_location, job.name)
                new_file_locs.append(new_file_loc)
                # Decide dp to round microns to
                if job.pixel_micron_ratio < 0.5:
                    # Round to 10 micron
                    dp = -1
                elif job.pixel_micron_ratio < 5.0:
                    # Round to 1 micron
                    dp = 0
                elif job.pixel_micron_ratio < 50.0:
                    # Round to 0.1 micron
                    dp = 1
                else:
                    # Round to 0.01 micron
                    dp = 2
                # Round position values to a particular decimal place
                xum_vals = [round(x / job.pixel_micron_ratio, 1) for x in job.x_vals]
                yum_vals = [round(y / job.pixel_micron_ratio, 1) for y in job.y_vals]
                # Write the position & force file
                write_pos_force_file(
                    new_file_loc,
                    self.app.COL_NAMES,
                    frame_nums,
                    t_vals,
                    job.x_vals,
                    job.y_vals,
                    xum_vals,
                    yum_vals,
                    force_total,
                    force_x,
                    force_y,
                    delta_Fx,
                    delta_Fy,
                )
            # Make pop up - alerts of files saved
            popup = PF1SuccessPopup(
                new_file_locs,
                self.new_window,
                self.new_window.manager.get_screen("FG2"),
            )
            popup.success_label.text = (
                str(len(new_file_locs))
                + " Files saved successfully.\nGenerate graphs or exit?"
            )
            popup.open()
            self.clear_jobs()
            # Close popup
            self.dismiss()
        # If they said "no cancel"
        else:
            # Close popup
            self.dismiss()


class FG2SuccessPopup(Popup):
    """A custom Popup object for after generating graphs for the FG2 screen
    - user can either exit to main menu or stay on FG2"""

    def __init__(self, new_file_locs, fg1_window, fg2_window, **kwargs):
        """init method for FG2SuccessPopup"""
        # Call Popup init method
        super(FG2SuccessPopup, self).__init__(**kwargs)
        # Save the clear_jobs method for when user pressed 'yes'
        self.new_file_locs = new_file_locs
        # Save the current and previous screens
        self.fg1_window = fg1_window
        self.fg2_window = fg2_window

    def on_answer(self, answer):
        """called when user presses 'exit' or 'stay'"""
        # If user chose to exit to main menu
        if answer == "exit":
            # Change screen to main
            app = App.get_running_app()
            app.root.current = "main"
            app.root.transition.direction = "right"
            # Close popup
            self.dismiss()
            # Empty the job list
            self.fg1_window.clear_jobs()
            self.fg2_window.clear_jobs()
        # If user chose to stay on FG2
        else:
            # Close popup
            self.dismiss()


class PF1SuccessPopup(Popup):
    """A custom Popup object for after generating graphs for the PF1 screen
    - user can either exit to main menu or stay on PF1"""

    def __init__(self, new_file_locs, fg1_window, fg2_window, **kwargs):
        """init method for PF1SuccessPopup"""
        # Call Popup init method
        super(PF1SuccessPopup, self).__init__(**kwargs)
        # Save the clear_jobs method for when user pressed 'yes'
        self.new_file_locs = new_file_locs
        # Save the current and previous screens
        self.fg1_window = fg1_window
        self.fg2_window = fg2_window

    def on_answer(self, answer):
        """called when user presses 'exit' or 'stay'"""
        # If user chose to exit to main menu
        if answer == "exit":
            # Change screen to main
            app = App.get_running_app()
            app.root.current = "main"
            app.root.transition.direction = "right"
            # Close popup
            self.dismiss()
            # Empty the job list
            self.fg1_window.clear_jobs()
            self.fg2_window.clear_jobs()
        # If user chose to stay on PF1
        else:
            # Add all new jobs
            self.fg1_window.selected(self.new_file_locs)
            # Grab the last job added
            final_job = self.fg1_window.fg1_scroll.grid_layout.children[-1]
            # Change screen
            app = App.get_running_app()
            app.root.current = "FG1"
            app.root.transition.direction = "up"
            # Close popup
            self.dismiss()
            # Set as current job
            self.fg1_window.current_job = final_job
            # Enable layouts
            self.fg1_window.param_grid_layout.disabled = False
            self.fg1_window.name_grid_layout.disabled = False
            # Update everything visually
            self.fg1_window.update_fields()
            self.fg1_window.update_job_selected()
