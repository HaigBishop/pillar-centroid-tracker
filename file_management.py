"""
Module: All functions related to file management
Program: Pillar Centroid Tracker
Author: Haig Bishop (hbi34@uclive.ac.nz)
"""


# Import modules used for dealing with files
from datetime import datetime
import re
import csv
from cv2 import imread
import xml.etree.ElementTree as et
from chardet import detect
import os
import sys
import re

# Get the path of the application
# This is important for when using executable files
APPLICATION_PATH = os.path.abspath(".")


def natural_sort(file_list):
    """Takes a list of files and returns the sorted
    - the sorting treats numbers like a human does
    - e.g. 8,9,10,11 NOT 10,11,8,9"""

    def atoi(text):
        return int(text) if text.isdigit() else text

    def natural_keys(text):
        return [atoi(c) for c in re.split(r"(\d+)", text)]

    return sorted(file_list, key=natural_keys)


def resource_path(relative_path):
    """takes the relative path to a file/folder, returns the absolute path
    - works for pure python execution and for the executable file"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = APPLICATION_PATH
    # Join the application path to the "base path"
    new_path = os.path.join(base_path, relative_path)
    # if this file doesn't exist
    if not os.path.exists(new_path):
        # remove the resources folder part
        substring = "resources\\"
        str_list = new_path.split(substring)
        new_path = "".join(str_list)
    return new_path


def class_resource_path(self, relative_path):
    """takes the relative path to a file/folder, returns the absolute path
    - this function is the same as resource path, but it is
    for classes because class methods need the self parameter
    - works for pure python execution and for the executable file"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = APPLICATION_PATH
    # Join the application path to the "base path"
    new_path = os.path.join(base_path, relative_path)
    # if this file doesn't exist
    if not os.path.exists(new_path):
        # remove the resources folder part
        substring = "resources\\"
        str_list = new_path.split(substring)
        new_path = "".join(str_list)
    return new_path


def is_valid_folder(folder_loc):
    """takes a folder location
    - returns a boolean which is True if...
    - the folder exists
    - AND
    - the folder contains at least 2 images of the same type"""
    # If the folder doesn't exist
    if not os.path.isdir(folder_loc):
        valid_contents = False
    # If the folder exists
    else:
        # The valid file extensions
        valid_types = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp")
        type_counts = [0, 0, 0, 0, 0]
        # For each file
        for file in os.listdir(folder_loc):
            # Get the file type
            type_tag = file[file.rfind(".") :].lower()
            # If a valid type
            if type_tag in valid_types:
                # Count that file type
                type_counts[valid_types.index(type_tag)] += 1
        # If there are at least 2 image files of the same type
        valid_contents = any([count >= 2 for count in type_counts])
    return valid_contents


def num_valid_images(folder_loc):
    """takes a folder location
    - looks at how many images of the same type the folder contains
    - returns the count of most common type type"""
    # Check if the folder exists
    if not os.path.isdir(folder_loc):
        type_counts = 0
    else:
        # Valid file extensions
        valid_types = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp")
        type_counts = [0, 0, 0, 0, 0]
        # For each file
        for file in os.listdir(folder_loc):
            # Get the file type
            type_tag = file[file.rfind(".") :].lower()
            # If a valid type
            if type_tag in valid_types:
                # Count that file type
                type_counts[valid_types.index(type_tag)] += 1
    # Returns the highest count
    return max(type_counts)


def valid_image_dims(image_locations):
    """takes a list of image locations
    - checks if all images are the same dimensions
    - returns True if they are all the same"""
    # Get the first images dimensions
    first_image = imread(image_locations[0])
    if first_image is not None:
        first_height, first_width, _ = first_image.shape
        # Iterate over the rest of the images
        for image_location in image_locations[1:]:
            # Get its dimensions
            image = imread(image_location)
            height, width, _ = image.shape
            # If the dimensions don't match up
            if height != first_height or width != first_width:
                return False
        return True
    else:
        return False


def positions_in_image_dim(image_loc, pos_list):
    """takes an image and a posiiton list
    - checks if all positions are within the image dimensions
    - returns True if all within image"""
    # Get the first images dimensions
    image = imread(image_loc)
    height, width, _ = image.shape
    # For each position
    for pos in pos_list:
        x, y = pos
        # If it is not within the image dimensions
        if not (x <= width and y <= height and x >= 0 and y >= 0):
            return False
    return True


def images_from_folder(folder_location):
    """takes a folder location
    - returns the most common image type and the file
    locations of that type"""
    # Valid file extensions
    valid_types = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp")
    image_files = [[], [], [], [], [], []]
    type_counts = [0, 0, 0, 0, 0, 0]
    # For each file
    for file in os.listdir(folder_location):
        # Get the file type
        type_tag = file[file.rfind(".") :].lower()
        # If is a valid type
        if type_tag in valid_types:
            # +1 count for this type
            type_counts[valid_types.index(type_tag)] += 1
            # Add the list of file types
            image_files[valid_types.index(type_tag)].append(file)
    # Get the most numerous image type's index
    top_type_index = type_counts.index(max(type_counts))
    # Use the index to get the extension
    top_image_type = valid_types[top_type_index]
    # Use the index to get the list of files at that type
    top_image_files = image_files[top_type_index]
    # Sort the files (in order of name)
    top_image_files = natural_sort(top_image_files)
    # Join to the folder locations
    top_image_file_locs = [folder_location + "\\" + file for file in top_image_files]
    return top_image_file_locs, top_image_type


def is_csv_xml(file_loc):
    """takes a file
    - returns True is the file is csv or xml"""
    return file_loc[-4:] == ".csv" or file_loc[-4:] == ".xml"


def file_name(file_location):
    """takes a file location
    - gets the file name e.g. "folder/filename.txt" -> "filename"
    - removes date/time part
    - removes any spaces
    - returns to be a job name"""
    # Make all auto time extension patterns
    pattern_1 = r"_forces_\d{2}-\d{2}-\d{2}_\d{2}-\d{2}\.[a-zA-Z]{3,4}$"
    pattern_2 = r"_pos_\d{2}-\d{2}-\d{2}_\d{2}-\d{2}\.[a-zA-Z]{3,4}$"
    pattern_3 = r"_newpos_\d{2}-\d{2}-\d{2}_\d{2}-\d{2}\.[a-zA-Z]{3,4}$"
    # Check if the file matches any pattern
    date_end_1 = re.search(pattern_1, file_location)
    date_end_index_1 = -1 if date_end_1 is None else date_end_1.start()
    date_end_2 = re.search(pattern_2, file_location)
    date_end_index_2 = -1 if date_end_2 is None else date_end_2.start()
    date_end_3 = re.search(pattern_3, file_location)
    date_end_index_3 = -1 if date_end_3 is None else date_end_3.start()
    # Gets the largest index in the most complicated way
    # This is to remove any time extension part
    if date_end_index_1 < date_end_index_2 and date_end_index_3 < date_end_index_2:
        date_end = date_end_2
        date_end_index = date_end_index_2
    elif date_end_index_1 < date_end_index_3:
        date_end = date_end_3
        date_end_index = date_end_index_3
    else:
        date_end = date_end_1
        date_end_index = date_end_index_1
    # If filename ends with the date and time
    if date_end and date_end_index >= 3:
        # Remove that part ownwards
        file_location = file_location[:date_end_index]
        # Get the file name
        s = str(file_location).rfind("\\") + 1
        name = str(file_location)[s:]
    else:
        # Get the file name
        s = str(file_location).rfind("\\") + 1
        name = str(file_location)[s:-4]
    # Remove space characters
    name = name.replace(" ", "")
    return name


def folder_name(folder_location):
    """takes a folder location
    - gets the name of the folder
    - e.g. "folder1/folder/filename.txt" -> folder"""
    s = str(folder_location).rfind("\\") + 1
    folder_name = str(folder_location)[s:]
    # Remove space characters
    folder_name = folder_name.replace(" ", "")
    return folder_name


def file_header(file_location):
    """takes file location of csv or xml
    - returns the 'header'
    - this is the list of strings in the first row"""
    header = []

    if len(file_location) > 3:
        # If it is a .csv
        if str(file_location)[-4:] == ".csv":
            # If this file exists
            if os.path.exists(file_location):
                encoding = detect_encoding(file_location)
                # Read the CSV file and extract the header row
                with open(file_location, "r", encoding=encoding) as csv_file:
                    reader = csv.reader(csv_file)
                    header = next(reader)
                # Empty cells become 'NULL'
                header = ["NULL" if item == "" else item for item in header]
        # If it is a .xml
        elif str(file_location)[-4:] == ".xml":
            # If this file exists
            if os.path.exists(file_location):
                # Load the XML file
                tree = et.parse(file_location)
                root = tree.getroot()
                # Find the <particle> element
                particle_elem = root.find("particle")
                try:
                    # Get the names of the <detection> element attributes
                    detection_attrs = particle_elem.find("detection").attrib.keys()
                except AttributeError:
                    # No tracking data! - same as empty csv file
                    detection_attrs = []
                header = list(detection_attrs)
    # Label the headers (see function) before returning
    return label_columns(header)


def detect_encoding(file_location):
    """takes a file location
    - returns the type of encoding used for the file"""
    with open(file_location, "rb") as file:
        result = detect(file.read())
    return result["encoding"]


def write_pos_force_file(
    file_location,
    col_names,
    frame_nums,
    t_vals,
    x_vals,
    y_vals,
    xum_vals,
    yum_vals,
    force_total,
    force_x,
    force_y,
    delta_Fx,
    delta_Fy,
):
    """takes all the data needed to write a force file
    - writes a csv force file"""
    # Transpose the lists into rows
    rows = list(
        zip(
            frame_nums,
            t_vals,
            x_vals,
            y_vals,
            xum_vals,
            yum_vals,
            force_total,
            force_x,
            force_y,
            delta_Fx,
            delta_Fy,
        )
    )
    # Write the CSV file
    with open(
        file_location, "w", newline="", errors="replace", encoding="UTF-8"
    ) as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(col_names)  # Write the headers
        csv_writer.writerows(rows)  # Write the data


def write_pos_file(file_location, position_data):
    """takes a file location and posiiton data
    - writes a position csv file"""
    # Transpose the lists into rows
    frame_nums, x_vals, y_vals = position_data
    rows = list(zip(frame_nums, x_vals, y_vals))
    # Write the CSV file
    with open(
        file_location, "w", newline="", errors="replace", encoding="UTF-8"
    ) as csvfile:
        csv_writer = csv.writer(csvfile)
        headers = ["Frame number", "x Position [pixels]", "y Position [pixels]"]
        csv_writer.writerow(headers)  # Write the headers
        csv_writer.writerows(rows)  # Write the data


def rename_file_pos(folder_location, name, updated=False):
    """takes a folder and a name
    - returns a new filelocation name
    - includes the time
    - includes either a _pos_ or a _newpos_ tag"""
    # Format the date and time as text
    now = datetime.now()
    date_and_time = str(now.strftime("%d-%m-%y_%H-%M"))
    # If this is a new posiiton file, use the _newpos_ tag :)
    tag = "_newpos_" if updated else "_pos_"
    # Join everything together
    return str(folder_location) + "\\" + str(name) + tag + date_and_time + ".csv"


def rename_file_force(file_location, name):
    """takes a folder and a name
    - returns a new file location name
    - includes the time"""
    # Format the date and time as text
    now = datetime.now()
    date_and_time = str(now.strftime("%d-%m-%y_%H-%M"))
    s = str(file_location).rfind("\\") + 1
    # Join everything together
    return str(file_location)[:s] + str(name) + "_forces_" + date_and_time + ".csv"


def rename_file_graph(file_location, name, graph_num):
    """takes a folder a job name and a graph number
    - returns a new file location name
    - this doesn't inlcude the file extension
    - includes the time and graph number"""
    # Format the date and time as text
    now = datetime.now()
    date_and_time = str(now.strftime("%d-%m-%y_%H-%M"))
    # Find last slash
    s = str(file_location).rfind("\\") + 1
    folder = str(file_location)[:s]  # 'C:\Desktop\folder\'
    new_folder = folder + "plots\\"  # 'C:\Desktop\folder\plots\'
    # Check if the directory exists
    if not os.path.exists(new_folder):
        # If it doesn't exist, create it
        os.makedirs(new_folder)
    # Join everything together
    return new_folder + str(name) + "_graph_" + str(graph_num) + "_" + date_and_time


def label_columns(header):
    """takes a header and adds "labels" to them
    - e.g. Position X  ->  Position X [3]"""
    labelled_header = []
    i = 1
    # For each header
    for col_name in header:
        # Add the "label"
        labelled_header.append(col_name + " [" + str(i) + "]")
        i += 1
    return labelled_header


def unlabel_columns(header):
    """takes a header and removes the "labels" from them
    - e.g. Position X [3]  ->  Position X"""
    unlabelled_header = []
    i = 1
    # Index to remove
    e = -4
    # For each header
    for col_name in header:
        if i == 10:
            # Increase the index to remove
            e = -5
        # Remove the "label"
        unlabelled_header.append(col_name[0:e])
        i += 1
    return unlabelled_header
