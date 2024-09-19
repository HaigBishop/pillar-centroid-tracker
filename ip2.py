"""
Module:  All classes related to Image -> Position Screen 2
Program: Pillar Centroid Tracker
Author: Haig Bishop (hbi34@uclive.ac.nz)
"""

# Import local modules
from popup_elements import BackPopup, ErrorPopup, TrackPopup, IP2SuccessPopup
from file_management import (
    images_from_folder,
    resource_path,
    write_pos_file,
    rename_file_pos,
)
from file_management import (
    is_valid_folder,
    images_from_folder,
    valid_image_dims,
    positions_in_image_dim,
)
from start_point_detector import start_point_detector
from pillar_tracker import pillar_tracker

# Kivy imports
from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock

# Import cv2 for computer vision
from cv2 import (
    imread,
    cvtColor,
    threshold,
    calcHist,
    flip,
    circle,
    convertScaleAbs,
    resize,
    bitwise_not,
    bitwise_or,
    imwrite,
    copyMakeBorder,
    INTER_LANCZOS4,
    THRESH_BINARY,
    BORDER_CONSTANT,
    COLOR_BGR2GRAY,
)

# Import numpy
import numpy as np

# Import modules for dealing with files
from os.path import getctime
from datetime import datetime
import os
import re
from subprocess import Popen as p_open

# Get the location of the overlay .png file
AXIS_OVERLAY_LOC = resource_path("resources\\axis_overlay.png")


class IP2Window(Screen):
    """position -> force screen"""

    def __init__(self, **kwargs):
        """init method for IP2"""
        # Call ScrollView init method
        super(IP2Window, self).__init__(**kwargs)
        # Set current job
        self.current_job = None
        # Get an (empty) IP1 window reference
        self.ip1_window = None
        # Get an (empty) PS1 window reference
        self.ps2_window = None
        # Save app as an attribute
        self.app = App.get_running_app()
        # Make the loading screen invisible
        Clock.schedule_once(self.end_loading, 0.01)

    def track(self):
        """called when track button is pressed
        - check the data
        - if there are no errors, make a continue popup"""
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
                # Get PS2_window
                self.ps2_window = self.manager.get_screen("PS2")
            if self.ip1_window == None:
                # Get IP1_window
                self.ip1_window = self.manager.get_screen("IP1")
            # Make pop up - asks if you are sure you want to continue
            popup = TrackPopup(
                self.ip1_window.clear_jobs,
                self.clear_jobs,
                self.ip2_scroll,
                self,
                self.ps2_window,
            )
            popup.open()

    def track_and_write(self, *args):
        """tracks the pillar across the image sequence and writes .csv files"""
        # Calc pos and write files
        new_file_locs = []
        folder_locs = []
        position_datas = []
        radii = []
        # For each job
        for job in self.ip2_scroll.grid_layout.children:
            # Predict positions across the sequence
            position_data = pillar_tracker(
                job.image_locations, job.start_point, job.radius
            )
            # Get a filename
            new_file_loc = rename_file_pos(job.folder_location, job.name)
            # Save on the list of files for later
            new_file_locs.append(new_file_loc)
            # Save on the list of folders for later
            folder_locs.append(job.folder_location)
            # Add the position data for later
            position_datas.append(position_data)
            # Add the radius to a list
            radii.append(job.radius)
            # Write a position .csv file with this data
            write_pos_file(new_file_loc, position_data)
        # Make pop up - alerts of files saved
        popup = IP2SuccessPopup(
            new_file_locs,
            folder_locs,
            position_datas,
            self.ip1_window.clear_jobs,
            self.clear_jobs,
            self.ps2_window,
            radii,
        )
        popup.success_label.text = (
            str(len(new_file_locs))
            + " Files saved successfully.\nScreen predicted positions or exit?"
        )
        popup.open()
        # Remove the loading screen
        self.end_loading()

    def check_data(self):
        """checks data before converting - returns list of errors
        - valid name
        - is folder
        - contains > 3 images of same type
        - images are the same dimensions
        - start_point is within the image shape"""
        # Make regular expression for job name
        name_regex = r"^[a-zA-Z0-9][a-zA-Z0-9[\]()_-]{0,30}$"
        name_list = []
        errors = []
        # For all jobs on job list
        for job in self.ip2_scroll.grid_layout.children:
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
            # Check if all images are the same (valid dimensions)
            elif not positions_in_image_dim(job.image_locations[0], [job.start_point]):
                # Invalid image contents (or folder doesn't exist)
                errors.append(" • position outside image (" + str(job.name) + ")\n")
            # Add this job's name to list (to check for duplicates)
            name_list.append(job.name)
        # Check for duplicate names
        if len(name_list) != len(set(name_list)):
            # Duplicate names
            errors.append(" • duplicate names\n")
        # Return the errors which have been found
        return list(set(errors))

    def copy_jobs(self, ip1_window):
        """copies each job in the FG1 window onto this window"""
        # For all jobs on job list
        for job in ip1_window.ip1_scroll.grid_layout.children:
            # Create a new baby on the job list
            new_box = IP2JobListBox(
                job_name=job.name, folder_location=job.folder_location, ip2_window=self
            )
            self.ip2_scroll.grid_layout.add_widget(new_box)
            # Find a start point in this image
            new_box.start_point, new_box.radius = start_point_detector(
                new_box.first_image_location
            )
            # Set as current job
            self.current_job = new_box
        # Update everything visually
        self.update_job_selected()
        self.image_widget.update_image()

    def start_loading(self, *args):
        """makes the loading screen visible"""
        # Add loading screen
        self.loading_layout.opacity = 1
        # Schedule the export to start
        Clock.schedule_once(self.track_and_write, 1)

    def end_loading(self, *args):
        """makes the loading screen invisible"""
        self.loading_layout.opacity = 0

    def update_job_selected(self):
        """updates every job's is_selected boolean
        - affects them visually"""
        for job in self.ip2_scroll.grid_layout.children:
            job.update_is_selected()

    def on_back_btn(self):
        """called by back btn
        - checks if there are an jobs
        - if any jobs it makes a popup"""
        # If there are any jobs
        if len(self.ip2_scroll.grid_layout.children) > 0:
            # Make pop up - asks if you are sure you want to exit
            popup = BackPopup(self.clear_jobs, "IP2")
            popup.open()
        # If there are no jobs
        else:
            # Make pop up
            popup = BackPopup(self.clear_jobs, "IP2")
            # Immediately close it (which triggers the app to go back)
            popup.on_answer("yes")

    def clear_jobs(self):
        """simply empties the job list
        - this has to be a while loop, because the list changes size while looping"""
        # While there are still jobs
        while len(self.ip2_scroll.grid_layout.children) != 0:
            # Remove the first job using on_x_btn
            self.ip2_scroll.on_x_btn(self.ip2_scroll.grid_layout.children[0])

    def toggle_save_opacity(self, *args):
        """toggles the opacity of the 'Saved Image' label"""
        self.saved_label.opacity = 0 if self.saved_label.opacity == 1 else 1


class IP2ScrollView(ScrollView):
    """scrolling widget in IP2"""

    def __init__(self, **kwargs):
        """init method for the scrolling widget in IP2"""
        # Call ScrollView init method
        super(IP2ScrollView, self).__init__(**kwargs)

    def on_x_btn(self, box):
        """called when an x button on a box is pressed or using clear_jobs
        - disables the layouts because there is nothing selected now
        - removes the jobs
        - updates visuals"""
        # Remove that job
        self.grid_layout.remove_widget(box)
        # Update current job to none
        self.ip2_window.current_job = None
        # Update visual stuff
        # Self.ip2_window.update_fields()
        self.ip2_window.update_job_selected()
        self.ip2_window.image_widget.update_image()


class IP2JobListBox(Button):
    """job widget on the IP2ScrollView widget"""

    def __init__(self, job_name, folder_location, ip2_window, **kwargs):
        """init method for the job widgets on the scrolling widget in IP2"""
        # Save the ip2_window as a reference
        self.ip2_window = ip2_window
        # Save file location
        self.folder_location = folder_location
        # Get the image locations and type
        self.image_locations, self.image_type = images_from_folder(folder_location)
        # Get the first image location
        self.first_image_location = self.image_locations[0]
        # Save app as an attribute
        self.app = App.get_running_app()
        # Call Button init method
        super().__init__(**kwargs)
        # Set the same as the file name (e.g. '...\folder\filename.txt'  -> 'filename')
        self.name = job_name
        # Grab the date of creation of the file
        if os.path.exists(folder_location):
            self.date = datetime.fromtimestamp(getctime(folder_location)).strftime(
                "%d/%m/%Y"
            )
        else:
            self.date = "File no longer exists"
        # This job should be selected at creation!
        self.is_selected = True
        # Calculate values to auto adjust contrast
        self.calculate_clarity()
        # Calculate the size of the axis overlay
        self.calculate_axis_scale()

    def on_press(self):
        """called when the job box is pressed"""
        # This is now the current job
        self.ip2_window.current_job = self
        # Update the visuals
        self.ip2_window.update_job_selected()
        self.ip2_window.image_widget.update_image()

    def update_is_selected(self):
        """update the is_selected attribute, which affects visuals"""
        # If this job is selected
        if self.ip2_window.current_job == self:
            # Remember that
            self.is_selected = True
        else:
            # Remember that
            self.is_selected = False

    def calculate_clarity(self):
        """called at the initialisation of the job box
        - calculates the optimal alpha and beta values
        - these are later applied to the images to adjust the contrast and brightness
        - optional histogram clipping"""
        # Read the first image
        image_loc = self.first_image_location
        image = imread(image_loc)
        # Convert to grayscale
        gray = cvtColor(image, COLOR_BGR2GRAY)
        # Set histogram clip percentage
        clip_hist_percent = 1
        # Calculate grayscale histogram
        hist = calcHist([gray], [0], None, [256], [0, 256])
        hist_size = len(hist)
        # Calculate cumulative distribution from the histogram
        accumulator = []
        accumulator.append(float(hist[0]))
        for index in range(1, hist_size):
            accumulator.append(accumulator[index - 1] + float(hist[index]))
        # Locate points to clip
        maximum = accumulator[-1]
        clip_hist_percent *= maximum / 100.0
        clip_hist_percent /= 2.0
        # Locate left cut
        minimum_gray = 0
        while accumulator[minimum_gray] < clip_hist_percent:
            minimum_gray += 1
        # Locate right cut
        maximum_gray = hist_size - 1
        while (
            accumulator[maximum_gray] >= (maximum - clip_hist_percent)
            and maximum_gray > 10
        ):
            maximum_gray -= 1
        # Calculate alpha and beta values
        self.alpha = 255 / (maximum_gray - minimum_gray)
        self.beta = -minimum_gray * self.alpha

    def calculate_axis_scale(self):
        """called at the initialisation of the job box
        - calculates the optimal scale for the axis overlay"""
        # Read the first image
        image_loc = self.first_image_location
        image = imread(image_loc)
        # Get the smallest side
        min_image_side = min([image.shape[0], image.shape[1]])
        # Just divide that by 10
        self.axis_pixel_size = int(min_image_side / 10)

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


class StartPointImage(Image):
    """The widget which holds the image"""

    def __init__(self, **kwargs):
        """init method for the image widget in IP2"""
        # Call Image init method
        super(StartPointImage, self).__init__(**kwargs)
        # Set default states for the folowing options
        self.x_down = False  # (toggle circle centre)
        self.c_down = False  # (toggle circle outside)
        self.clarity_on = False  # (toggle auto contrast)
        self.axis_on = False  # (toggle axis)
        # Set attributes for zooming
        self.zoomed = False
        self.crop_bbox = None  # Box pixel box that is zoomed in on

    def on_touch_move(self, touch):
        """called when there is a 'touch movement'
        - this includes things like click/drags and swipes"""
        # If the touch is within the image
        if self.pos_in_image(touch.pos) and not self.zoomed:
            # Update the circle position
            self.update_pos(touch.pos, touch_pos=True)
        # You have to return this because it is a Kivy method
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        """this is called by all mouse up things. (e.g. left, right, middle scroll)"""
        # If it is a button (Kivy thing) and the touch is within the image
        if "button" in touch.profile and self.pos_in_image(touch.pos):
            # If a left click
            if touch.button == "left":
                # Update the circle position
                self.update_pos(touch.pos, touch_pos=True)
            else:
                # Get the radius
                radius = self.ip2_window.current_job.radius
                # Get the shape of the image
                image_shape = tuple(
                    imread(self.ip2_window.current_job.first_image_location).shape[0:2]
                )
                # True if the shortest image dimension is smaller than 6x the radius
                too_big = radius > min(image_shape) / 6
                # True if the radius is less than 8
                too_small = radius < 8
                # If a scroll up + not too big
                if touch.button == "scrollup" and not too_big:
                    # Increase radius
                    self.ip2_window.current_job.radius += 1
                # If a scroll down + not too small
                if touch.button == "scrolldown" and not too_small:
                    # Increase radius
                    self.ip2_window.current_job.radius -= 1
            # Update the image
            self.update_image()
        # You have to return this because it is a Kivy method
        return super().on_touch_down(touch)

    def pos_in_image(self, pos):
        """takes a position and returns True if it is within the image dimensions"""
        # Unzip pos
        x, y = pos
        # Get image dimensions etc
        norm_image_x = (self.width - self.norm_image_size[0]) / 2
        norm_image_y = (self.height - self.norm_image_size[1]) / 2
        norm_image_x2 = norm_image_x + self.norm_image_size[0]
        norm_image_y2 = norm_image_y + self.norm_image_size[1]
        # True if the pos in in the image
        is_in_image = (
            x >= norm_image_x
            and x <= norm_image_x2
            and y >= norm_image_y
            and y <= norm_image_y2
        )
        # If was within the image
        return is_in_image

    def update_pos(self, pos, touch_pos=False):
        """Takes a posiiton and updates the position of the pillar circle
        - if touch_pos is True, then pos is in reference to the entire app!
        - if touch_pos is TFalse, then pos is in reference to the image"""
        # If a touch pos
        if touch_pos:
            # Change pos to be in reference with the image
            # If the pos is in the image
            if self.pos_in_image(pos):
                # Correct pos in regards to image widget
                norm_image_x = (self.width - self.norm_image_size[0]) / 2
                norm_image_y = (self.height - self.norm_image_size[1]) / 2
                x, y = pos[0] - norm_image_x, pos[1] - norm_image_y
                # Correct pos in regards to texture pixel grid!
                x, y = int((x / self.norm_image_size[0]) * self.texture_size[0]), int(
                    (y / self.norm_image_size[1]) * self.texture_size[1]
                )
                # Flip y coord!
                y = int((y - self.texture_size[1]) * -1)
                # If zoomed, correct the coords further
                if self.zoomed:
                    x, y = x + self.crop_bbox[0], y + self.crop_bbox[1]
                pos = (x, y)
            # If pos is not in the image
            else:
                return None
        # Update job pos value
        self.ip2_window.current_job.start_point = pos
        # Update image
        self.update_image()

    def on_key_down(self, key, modifiers):
        """called when a key is pressed down
        - there are many results depending on the key"""
        # Is True if an arrow key
        is_arrow_key = key == "down" or key == "up" or key == "left" or key == "right"
        # If there a current job
        if self.ip2_window.current_job is not None:
            # If the 'z' key is pressed down
            if key == "z" and self.zoomed == False:
                # Zoom in
                self.zoomed = True
                self.update_image()
            # If the 'x' key is pressed down
            elif key == "x":
                # Toggles centre of circle
                self.x_down = True
                self.update_image()
            # If the 'c' key is pressed down
            elif key == "c":
                # Toggles outside of circle
                self.c_down = True
                self.update_image()
            # If the 'ctrl' key is not pressed down and an arrow key is pressed
            elif not "ctrl" in modifiers and is_arrow_key:
                # Get the start position
                x, y = self.ip2_window.current_job.start_point
                # If the 'down' key is pressed down
                if key == "down":
                    # Move pos down 1
                    y += 1
                # If the 'up' key is pressed down
                elif key == "up":
                    # Move pos up 1
                    y -= 1
                # If the 'left' key is pressed down
                elif key == "left":
                    # Move pos left 1
                    x -= 1
                # If the 'right' key is pressed down
                elif key == "right":
                    # Move pos right 1
                    x += 1
                self.update_pos((x, y))
            # If the 'ctrl' key is pressed down and an arrow key is pressed
            elif "ctrl" in modifiers and is_arrow_key:
                # If the 'down' key is pressed down
                if key == "down":
                    # Move down job
                    self.change_job(direction="down")
                # If the 'up' key is pressed down
                elif key == "up":
                    # Move up job
                    self.change_job(direction="up")
        # You have to return this because it is a Kivy method
        return True

    def on_key_up(self, key):
        """called when a key is released up
        - there are many results depending on the key"""
        if not self.ip2_window.current_job is None:
            # If the 'z' key is released (and currently zoomed)
            if key == "z" and self.zoomed == True:
                # Stop zooming
                self.zoomed = False
                self.update_image()
                self.crop_bbox = None
            # If the 'x' key is released
            elif key == "x":
                # Toggles centre of circle
                self.x_down = False
                self.update_image()
            # If the 'c' key is released
            elif key == "c":
                # Toggles outside of circle
                self.c_down = False
                self.update_image()
            # If the 's' key is released
            elif key == "s":
                # Calling update_image with save_image=True updates then write the image as a .png
                self.update_image(save_image=True)
                # Make the 'saved image' label visible
                self.ip2_window.toggle_save_opacity()
                # Schedule opacity to be reset in 1 second
                Clock.schedule_once(self.ip2_window.toggle_save_opacity, 1)
            # If the 'd' key is released
            elif key == "d":
                # Toggles the auto contrast
                self.clarity_on = not self.clarity_on
                self.update_image()
            # If the 'a' key is released
            elif key == "a":
                # Toggles the axis overlay
                self.axis_on = not self.axis_on
                self.update_image()
        # You have to return this because it is a Kivy method
        return True

    def update_image(self, save_image=False):
        """updates the current image on the screen
        - factors include:
            - current job (and its first image)
            - contrast toggle
            - axis toggle
            - centre toggle
            - circle toggle
            - zoom toggle
            - position
        - if save_image=True the funciton will write the image"""
        # If there is no current job
        if self.ip2_window.current_job is None:
            # Display no texture
            self.texture = None
        else:
            # Get the current job's first image
            image_loc = self.ip2_window.current_job.first_image_location
            self.image = imread(image_loc)
            # Adjust contrast if turned on
            self.check_clarity()
            # Add axis if turned on
            self.check_axis()
            # Add circle centre & outside if turned on
            self.draw_point()
            # Zoom image if turned on
            self.check_zoom()
            # If saving the image
            if save_image:
                # Write the image as a .png
                self.write_image(image_loc)
            # Flip the image for Kivy
            self.image = flip(self.image, 0)
            # Convert the image to a format useable for Kivy
            self.kivify_images()
            # Add this as the current texture
            self.texture = self.kivy_image

    def write_image(self, image_loc):
        """takes an image location and writes self.image to that location
        - formats the location to be in a subfolder 'captures'
        - formats the file name to include the time
        - saves as the same file type"""
        # Find indicies for the last slash and the last dot
        slash_index = max([image_loc.rfind("\\"), image_loc.rfind("/")])
        dot_index = image_loc.rfind(".")
        # Get the folder location
        folder = image_loc[: slash_index + 1]  # 'C:/Desktop/folder/'
        # Add the captures subfolder
        new_folder = folder + "captures/"  # 'C:/Desktop/folder/captures/'
        # Get the file name
        filename = image_loc[slash_index + 1 : dot_index]  # 'filename'
        # Format the date and time as text
        now = datetime.now()
        date_and_time = str(now.strftime("%d-%m-%y_%H-%M-%S"))
        date_extension = "_" + date_and_time
        # Get the image extension
        extension = image_loc[dot_index:]  #'.jpg'
        # Check if the directory exists
        if not os.path.exists(new_folder):
            # If it doesn't exist, create it
            os.makedirs(new_folder)
        # Combine all and write
        imwrite(
            new_folder + filename + "_capture" + date_extension + extension, self.image
        )

    def draw_point(self):
        """draw the circle on the image
        - but only if they are enabled"""
        centre = self.ip2_window.current_job.start_point
        radius = self.ip2_window.current_job.radius
        # If the x button is not down
        if not self.x_down:
            # If zoomed in the radius is 0
            point_radius = 0 if self.zoomed else 2
            # Draw centre point
            circle(self.image, centre, point_radius, (0, 0, 255), 1)
        # If the c button is not down
        if not self.c_down:
            # Draw circle outline
            circle(self.image, centre, radius, (0, 0, 255), 1)

    def check_clarity(self):
        """adjust the brightness and contrast of the image
        - but only if it is currently enabled"""
        # If this option is on
        if self.clarity_on:
            # Use the pre calculated alpha & beta values
            alpha = self.ip2_window.current_job.alpha
            beta = self.ip2_window.current_job.beta
            # Update the image
            self.image = convertScaleAbs(self.image, alpha=alpha, beta=beta)

    def check_zoom(self):
        """adjust the zoom of the image
        - but only if it is currently enabled"""
        # If zoom option is on
        if self.zoomed:
            # Use pos and size for calculations
            centre = self.ip2_window.current_job.start_point
            radius = self.ip2_window.current_job.radius
            # Make an extra gap
            extra_room = int(radius * 1.0)
            # Get zoom area
            x1, x2 = centre[0] - radius - extra_room, centre[0] + radius + extra_room
            y1, y2 = centre[1] - radius - extra_room, centre[1] + radius + extra_room
            # Give black border
            border_size = radius * 2
            self.image = copyMakeBorder(
                self.image,
                top=border_size,
                bottom=border_size,
                left=border_size,
                right=border_size,
                borderType=BORDER_CONSTANT,
                value=(0, 0, 0),
            )
            # Crop that
            self.image = self.image[
                y1 + border_size : y2 + border_size, x1 + border_size : x2 + border_size
            ]
            # Save the crop positions for later if needed
            self.crop_bbox = x1, y1, x2, y2

    def check_axis(self):
        """add the axis overlay
        - but only if it is currently enabled"""
        # If axis overlay option is on and not zoomed in
        if self.axis_on and not self.zoomed:
            # Use the pre calculated overlay size
            axis_pixel_size = self.ip2_window.current_job.axis_pixel_size
            # Read the overlay image
            overlay = imread(AXIS_OVERLAY_LOC, 0)
            # Calculate the positions
            y_pos = int(axis_pixel_size / 2)
            x_pos = self.image.shape[0] - axis_pixel_size - y_pos
            # Resize overlay to fit on the image
            resized_overlay = resize(
                overlay,
                (axis_pixel_size, axis_pixel_size),
                interpolation=INTER_LANCZOS4,
            )
            # Create a mask by thresholding the binary image
            _, mask = threshold(resized_overlay, 5, 255, THRESH_BINARY)
            # Invert the mask
            mask_inv = bitwise_not(mask)
            # Extract the region of interest (ROI) from the grayscale image
            roi = self.image[
                x_pos : x_pos + axis_pixel_size, y_pos : y_pos + axis_pixel_size
            ]
            # Apply the mask to the ROI
            roi_masked = bitwise_or(roi, roi, mask=mask_inv)
            # Make all black pixels white
            height, width, _ = roi_masked.shape
            for i in range(height):
                for j in range(width):
                    if roi_masked[i, j].sum() == 0:
                        roi_masked[i, j] = [255, 255, 255]
            # Place the result back into the grayscale image
            self.image[
                x_pos : x_pos + axis_pixel_size, y_pos : y_pos + axis_pixel_size
            ] = roi_masked

    def kivify_images(self):
        """uses self.image to make self.kivy_image
        - self.image is a np array
        - self.kivy_image is a kivy compatible texture"""
        # If there is an image
        if isinstance(self.image, np.ndarray):
            # Make kivy version
            self.kivy_image = Texture.create(
                size=(self.image.shape[1], self.image.shape[0]), colorfmt="bgr"
            )
            # If zoomed in
            if self.zoomed:
                # Set magnification resampling method to preserve detail (the default is linear)
                self.kivy_image.mag_filter = "nearest"
            self.kivy_image.blit_buffer(
                self.image.tobytes(), colorfmt="bgr", bufferfmt="ubyte"
            )

    def change_job(self, direction="down"):
        """called by pressing Ctrl + down/up key
        - changes the current job (goes up or down)"""
        # For all jobs on job list
        for job_index in range(len(self.ip2_window.ip2_scroll.grid_layout.children)):
            job = self.ip2_window.ip2_scroll.grid_layout.children[job_index]
            # If current job
            if job is self.ip2_window.current_job:
                # If changing up (increase index) and the current job is >= the number of jobs
                if (
                    direction == "up"
                    and len(self.ip2_window.ip2_scroll.grid_layout.children)
                    > job_index + 1
                ):
                    # Move up one job
                    self.ip2_window.current_job = (
                        self.ip2_window.ip2_scroll.grid_layout.children[job_index + 1]
                    )
                    # Update everything visually
                    self.ip2_window.update_job_selected()
                    self.ip2_window.image_widget.update_image()
                    break  # Don't need to keep looping
                # If changing down (decrease index) and the current job is > 0
                if direction == "down" and job_index > 0:
                    # Move down one job
                    self.ip2_window.current_job = (
                        self.ip2_window.ip2_scroll.grid_layout.children[job_index - 1]
                    )
                    # Update everything visually
                    self.ip2_window.update_job_selected()
                    self.ip2_window.image_widget.update_image()
                    break  # Don't need to keep looping
