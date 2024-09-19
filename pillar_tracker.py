"""
Module: The tracking of the pillar across the image sequence
Program: Pillar Centroid Tracker
Author: Haig Bishop (hbi34@uclive.ac.nz)
"""

# Import modules for math and computer vision
import numpy as np

# Import modules for math and computer vision
from cv2 import (
    imread,
    cvtColor,
    COLOR_BGR2GRAY,
    imread,
    cvtColor,
    calcHist,
    circle,
    convertScaleAbs,
    bitwise_and,
    subtract,
    COLOR_BGR2GRAY,
)
import math


def calculate_alpha_beta(image):
    """Takes an image
    - returns alpha and beta values to optimally fix contrast/brightness"""
    # Automatic brightness and contrast optimisation with optional histogram clipping
    gray = cvtColor(image, COLOR_BGR2GRAY)
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
        accumulator[maximum_gray] >= (maximum - clip_hist_percent) and maximum_gray > 10
    ):
        maximum_gray -= 1
    # Calculate alpha and beta values
    alpha = 255 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha
    return alpha, beta


def weighted_average_pos(image, start_pos):
    """Takes an image and a position on that image
    - calculates the average position of pixels on that image
    it is a weighted average by the brightness of the pixels
    - it also scale how far the position is from start_pos
    this depends on the average brightness of the image"""
    # Make empty array
    num_pixels = image.shape[0] * image.shape[1]
    # Convert to a grayscale matrix
    matrix = cvtColor(image, COLOR_BGR2GRAY)
    matrix = np.array(matrix)
    # Remove any grey pixels below 60 brightness
    matrix[matrix < 60] = 0
    # Calculate the weighted average position for each row and col
    weighted_rows, weighted_cols = np.indices(matrix.shape) * matrix
    sum_weighted_rows = np.sum(weighted_rows)
    sum_weighted_cols = np.sum(weighted_cols)
    total_sum = np.sum(matrix) if np.sum(matrix) > 1 else 1
    avg_weighted_row = sum_weighted_rows / total_sum
    avg_weighted_col = sum_weighted_cols / total_sum
    # This gives us the average position (weighted)
    average_pos = (avg_weighted_col, avg_weighted_row)
    # Scale depending on total brightness of the donut
    average_img_brightness_sq = (np.sum(matrix) / num_pixels) ** 2
    average_x = int(
        (average_pos[0] * average_img_brightness_sq + start_pos[0])
        / (1 + average_img_brightness_sq)
    )
    average_y = int(
        (average_pos[1] * average_img_brightness_sq + start_pos[1])
        / (1 + average_img_brightness_sq)
    )
    return (average_x, average_y)


def check_dist_prev(new_pos, prev_pos, radius):
    """Takes two positions (tracked one after the other) and a radius
    - if the distance between the two positions is greater than a quarter of the radius
    it will decrease than movement to a quarter of the radius
    - returns the new position"""
    distance = (
        (new_pos[0] - prev_pos[0]) ** 2 + (new_pos[1] - prev_pos[1]) ** 2
    ) ** 0.5
    new_x, new_y = new_pos
    if distance > radius / 4:
        # Shift to edge of the reasonable distance moved
        x1, y1 = prev_pos
        x2, y2 = new_pos
        # Calculate the vector components
        dx = x2 - x1
        dy = y2 - y1
        # Calculate the length of the vector
        distance = math.sqrt(dx**2 + dy**2)
        # Normalize the vector components
        dx_normalized = dx / distance
        dy_normalized = dy / distance
        # Move the point (x2, y2) along the normalized vector
        reasonable_distance = radius / 4
        new_x = int(x1 + dx_normalized * reasonable_distance)
        new_y = int(y1 + dy_normalized * reasonable_distance)
    return (new_x, new_y)


def predict_pos(img_substraction, inner_circle, outer_circle, prev_pos, pillar_radius):
    """takes an image, a donut shape on that image, the previous position and the pillar radius
    - blacks out pixels outside the donut
    - gets the average pixel position
    - scales the position back if it is too far
    - returns the position"""
    # Create a blank mask with the same dimensions as the image
    mask = np.zeros_like(img_substraction)
    # Draw a white outer circle on the mask
    centre = (outer_circle[0], outer_circle[1])
    radius = outer_circle[2]
    circle(mask, centre, radius, (255, 255, 255), -1)
    # Draw a black inner circle on the mask
    radius = inner_circle[2]
    circle(mask, centre, radius, (0, 0, 0), -1)
    # Apply the mask to the image to black out the pixels outsdie the white donut
    img_sub_donut = bitwise_and(img_substraction, mask)
    # Get the average pixel position, weighted by their brightness
    pos = weighted_average_pos(img_sub_donut, centre)
    # Make sure it didn't do too far from the previous position
    pos = check_dist_prev(pos, prev_pos, pillar_radius)
    return pos


def track_object(image_locs, crop_bbox, initial_circle):
    """takes an image sequence, the section of the images to look at,
    and the position of the pillar in the first frame.
        - returns a list of predicted bboxes for the pillar across the sequence"""
    # Get the crop box
    crop_x1, crop_y1, crop_x2, crop_y2 = crop_bbox
    # Get the initial circle (adjusted for crop)
    start_x, start_y, start_r = initial_circle
    start_x, start_y, start_r = start_x - crop_x1, start_y - crop_y1, start_r
    # Load the initial image
    first_image = imread(image_locs[0])  # Read as grayscale
    first_image = first_image[crop_y1:crop_y2, crop_x1:crop_x2]  # Crop image
    alpha, beta = calculate_alpha_beta(first_image)
    first_image = convertScaleAbs(first_image, alpha=alpha, beta=beta)
    # Initialize the list to store object positions
    predicted_circles = [(start_x, start_y, start_r)]
    prev_pos = (start_x, start_y)
    # Track the object across the sequence of images
    for image_loc in image_locs[1:]:
        current_image = imread(image_loc)  # Read
        current_image = current_image[crop_y1:crop_y2, crop_x1:crop_x2]  # Crop image
        current_image_copy = convertScaleAbs(
            current_image.copy(), alpha=alpha, beta=beta
        )
        img_substraction = subtract(current_image_copy, first_image)
        inner_circle = (start_x, start_y, int(start_r * 0.5))
        outer_circle = (start_x, start_y, int(start_r * 1.5))
        position_x, position_y = predict_pos(
            img_substraction, inner_circle, outer_circle, prev_pos, start_r
        )
        prev_pos = (position_x, position_y)
        circle = (position_x, position_y, start_r)
        # Store the updated object position
        predicted_circles.append(circle)
    return predicted_circles


def pillar_tracker(image_locs, start_point, radius):
    """takes a list of images, and the starting pillar position
    - returns the predicted pillar postion across the images"""
    # Set lists to be returned
    frame_nums = list(range(1, len(image_locs) + 1))
    x_vals, y_vals = [], []
    initial_circle = (start_point[0], start_point[1], radius)
    # Crop image
    x1, x2 = start_point[0] - 4 * radius, start_point[0] + 4 * radius
    y1, y2 = start_point[1] - 4 * radius, start_point[1] + 4 * radius
    crop_bbox = [x1, y1, x2, y2]
    # Track pillar! returns circles
    circles = track_object(image_locs, crop_bbox, initial_circle)
    # Shift positions for uncropped image
    new_circles = []
    for x, y, r in circles:
        new_circles.append((x + x1, y + y1, r))
        # Process the bboxes
    positions = []
    for circle in new_circles:
        # Convert bbox into circle
        centre = (circle[0], circle[1])
        positions.append(centre)
    # reshape them into the lists
    for x, y in positions:
        # Add to lists
        x_vals.append(x)
        y_vals.append(y)
    return (frame_nums, x_vals, y_vals)
