"""
Module: The detection of the pillar in one frame (likely the first frame)
Program: Pillar Centroid Tracker
Author: Haig Bishop (hbi34@uclive.ac.nz)
"""

# Import modules for math and computer vision
from cv2 import (
    imread,
    cvtColor,
    threshold,
    HoughCircles,
    getStructuringElement,
    morphologyEx,
    GaussianBlur,
    countNonZero,
    bitwise_not,
    connectedComponentsWithStats,
    convertScaleAbs,
    calcHist,
    CC_STAT_AREA,
    COLOR_BGR2GRAY,
    HOUGH_GRADIENT,
    THRESH_BINARY,
    THRESH_OTSU,
    MORPH_RECT,
    MORPH_CLOSE,
    MORPH_OPEN,
    getRotationMatrix2D,
    warpAffine,
)
import numpy as np
from sklearn.cluster import KMeans


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


def only_2_largest(img):
    """Takes a binary image
    - finds all white pixel clusters
    - removes all clusters except the 2 biggest
    - returns the resulting binary image"""
    # Find white pixel clusters
    _, labels, stats, _ = connectedComponentsWithStats(img, connectivity=8)
    # Get areas of white pixel clusters
    areas = stats[1:, CC_STAT_AREA]
    # Sort areas in descending order and get indices of two largest clusters
    max_area_idx = np.argsort(-areas)[:2]
    # Create black image with same dimensions as input image
    output_img = np.zeros_like(img)
    # Add two largest clusters to output image
    for idx in max_area_idx:
        output_img[labels == idx + 1] = 255
    return output_img


def rotate_image(image, angle):
    """Takes an image,  and an angle to rotate it by
    - finds all white pixel clusters
    - rotates the image by angle degrees
    - the image is the same dimensions
    - the parts where the image doesn't fill the new image become black
    - returns the rotated image"""
    if angle != 0:
        height, width = image.shape[:2]
        rotation_matrix = getRotationMatrix2D((width / 2, height / 2), angle, 1)
        image = warpAffine(image, rotation_matrix, (width, height))
    return image


def make_left_right_black(image):
    """takes an image (likely binary)
    - adds black vertical bars to the left and right 15% of the image
    - returns that image"""
    _, width = image.shape[:2]
    region_width = int(width * 0.15)
    image[:, :region_width] = 0  # Set left region to black
    image[:, -region_width:] = 0  # Set right region to black
    return image


def detect_channel_sides(img):
    """takes a image, finds x coords of the two channel sides
    - converts to binary
    - applies some morphology
    - inverts image if necessary
    - gets 3 version of the image rotates 2 degrees apart from each other
    - finds all vertical lines in the each image (morphology)
    - applys AND operation to all 3 resulting binary images
    - removes the left and right 15% of the resulting image
    - removes all white pixel clusters except 2 largest
    - finds the x coords of those two largest clusters
    - returns the two integers"""
    # Convert the image to grayscale
    gray_img = cvtColor(img, COLOR_BGR2GRAY)
    # Apply a threshold to the image (creates a binary image)
    _, binary_img = threshold(gray_img, 0, 255, THRESH_BINARY + THRESH_OTSU)
    # Create a 3x3 square structuring element
    kernel = getStructuringElement(MORPH_RECT, (5, 5))
    closed_img = morphologyEx(binary_img, MORPH_CLOSE, kernel)
    # Create a 3x3 square structuring element
    kernel = getStructuringElement(MORPH_RECT, (5, 5))
    # Apply a morphological operation to remove noise
    opened_img = morphologyEx(closed_img, MORPH_OPEN, kernel)
    # Get numbers of each pixel
    total_pixels = opened_img.shape[0] * opened_img.shape[1]
    white_pixels = countNonZero(opened_img)
    black_pixels = total_pixels - white_pixels
    if white_pixels > black_pixels:
        # Invert image
        opened_img = bitwise_not(opened_img)
    # Get 2 new images rotate 2 degrees either side
    opened_img_left = rotate_image(opened_img.copy(), -2)
    opened_img_right = rotate_image(opened_img.copy(), 2)
    # Attempt to get a good kernal height
    division_number = 20
    if opened_img.shape[0] / division_number < 16:
        line_height = 16
    else:
        line_height = int(opened_img.shape[0] / division_number)
    # Apply a morphological operation to find vertical lines (to each image)
    kernel = getStructuringElement(MORPH_RECT, (1, line_height))
    vert_lines_img1 = morphologyEx(opened_img_left, MORPH_OPEN, kernel, iterations=3)
    vert_lines_img2 = morphologyEx(opened_img, MORPH_OPEN, kernel, iterations=3)
    vert_lines_img3 = morphologyEx(opened_img_right, MORPH_OPEN, kernel, iterations=3)
    # Rotate the two back
    vert_lines_img1 = rotate_image(vert_lines_img1, 2)
    vert_lines_img3 = rotate_image(vert_lines_img3, -2)
    # Merge all three images
    vert_lines_img = (
        np.logical_or(
            np.logical_or(vert_lines_img1, vert_lines_img2), vert_lines_img3
        ).astype(np.uint8)
        * 255
    )
    # Remove left and right 15% of white pixels
    centre_img = make_left_right_black(vert_lines_img)
    # Remove all white pixel clusters except two largest
    two_largest_img = only_2_largest(centre_img)
    # Find the coordinates of the vertical lines
    coords = np.column_stack(np.where(two_largest_img > 0))
    x_coords = coords[:, 1]
    # Reshape data to have only one feature/column
    X = x_coords.reshape(-1, 1)
    # If we have any decent data (it isn't black)
    if len(X) > 1:
        # Use KMeans to find two center values to divide the lines into 2 groups
        k_means = KMeans(
            n_clusters=2,
            init="k-means++",
            n_init=5,
            max_iter=20,
            tol=0.5,
            algorithm="lloyd",
        )
        k_means.fit(X)
        center_values = k_means.cluster_centers_
        centroid_1, centroid_2 = int(center_values[0][0]), int(center_values[1][0])
    else:
        centroid_1, centroid_2 = int(gray_img.shape[1] * 0.1), int(
            gray_img.shape[1] * 0.9
        )
    return sorted((centroid_1, centroid_2))


def filter_circles_bbox(circles, bbox):
    """takes a list of circles (x, y, r) and a bounding box [x, y, x2, y2]'
    - returns a subset of the circles list
    - all circles must be positioned with centres inside of the bbox
    - the circle list is a weird shape (1, N, 3) because of Houghcircle"""
    # If there are any circles
    if circles is not None:
        # Get the x, y coordinates of the bounding box
        x1, y1, x2, y2 = bbox
        # Create a new array to store the circles that are within the bounding box
        new_circles = np.empty((0, 3), dtype=np.int32)
        # Iterate through all detected circles
        for circle in circles[0]:
            # Get the coordinates of the circle
            center_x, center_y, radius = circle[0], circle[1], circle[2]
            left_x, right_x = center_x - radius, center_x + radius
            bottom_y, top_y = center_y - radius, center_y + radius
            # Check if the center of the circle is within the bounding box
            if x1 < left_x and right_x < x2 and y1 < bottom_y and top_y < y2:
                # The center of the circle is inside the bounding box, keep it
                new_circles = np.vstack([new_circles, circle])
        # Reshape the array to shape (1, N, 3)
        circles = new_circles.reshape((1, new_circles.shape[0], new_circles.shape[1]))
        # If the circles are empty
        if circles.shape == (1, 0, 3):
            circles = None
    return circles


def get_best_circle(circles, expected_radius, expected_x):
    """takes a list of circles and an expected x pos and radius"""
    # This list will contain tuples like this:
    # (combined difference, circle, size difference, pos difference)
    master_list = []
    for x, y, r in circles:
        # Get their size difference
        size_difference = abs(r - expected_radius)
        # Get their position difference
        pos_difference = abs(x - expected_x)
        # Get combined score
        net_difference = size_difference + pos_difference
        # Add all to the list
        master_list.append((net_difference, (x, y, r), size_difference, pos_difference))
    # Get the circle with the lowest of both if possible
    circle = sorted(master_list)[0][1]
    return circle


def bounded_hough_circle(original_image, bbox, min_r, max_r):
    """takes an image, a bounding box, a min radius and a max radius
    - preforms hough transform iteratively until a circle is found
    - maximum # Iterations is 28
    - if no circles are found, an 'expected' circle is returned
    - each iteration the thresholds are decreased
    - the circles must be within the bbox
    - after Hough returns 1 or more circles, the 'best' one is picked"""
    # Blur the image
    blur_image = GaussianBlur(original_image, (9, 9), 0)
    # Convert the image to grayscale for processing
    gray_image = cvtColor(blur_image, COLOR_BGR2GRAY)
    # Define starting thresholds
    thres_1 = 150
    thres_2 = 120
    # The minimum distance between circles
    min_dist = 1
    # Define the expected circle in order to select the best one
    expected_radius = int((min_r + max_r) / 2)
    expected_x = int((bbox[0] + bbox[2]) / 2)
    # Loop until you find a circle or pass 28 iterations
    circles = None
    i = 0
    while circles is None and i < 28:
        i += 1
        # Attempt to detect circles in the grayscale image.
        circles = HoughCircles(
            gray_image,
            HOUGH_GRADIENT,
            2,
            min_dist,
            param1=thres_1,
            param2=thres_2,
            minRadius=min_r,
            maxRadius=max_r,
        )
        # Filter circles outside of bbox
        circles = filter_circles_bbox(circles, bbox)
        # Increase thresholds
        thres_1 = int(thres_1 * 0.9)
        thres_2 = int(thres_2 * 0.9)
    # Format circles (all ints and remvove packet)
    if not circles is None:
        # Remove packet shell thing
        circles = circles[0]
        circles = [(int(x), int(y), int(r)) for x, y, r in circles]
        # Find the circle with the most likely size
        if len(circles) > 1:
            circle = get_best_circle(circles, expected_radius, expected_x)
        else:
            circle = circles[0]
    else:
        # Make up circle of expected size and pos
        print("NO CIRCLE FOUND")
        circle = (expected_x, int(original_image.shape[0] / 2), expected_radius)
    return circle


def get_pillar_size_pos_range(sides, image_shape):
    """takes channel positions (x1, x2) and the shape of an image
    - returns the expected size and pos range for a pillar
    - uses image shape to determine min/max y coords
    - uses the channel sides variable to determine min/max x coords
    - uses the channel sides to determine min/max radii"""
    # Determine min/max x coords
    left_x, right_x = sides
    # Determine min/max y coords
    bottom_y, top_y = int(image_shape[0] * 0.1), int(image_shape[0] * 0.9)
    # Get the width of the channel
    channel_width = right_x - left_x
    # Find the expected size range of the pillar
    min_r = int(channel_width * 0.15 / 2)  # /2 to get radius
    max_r = int(channel_width * 1.15 / 2)  # /2 to get radius
    # Return the bbox and radius range
    return [left_x, bottom_y, right_x, top_y], min_r, max_r


def start_point_detector(image_loc, bbox=None):
    """takes an image location, and maybe a bounding box (x, y, x2, y2)"""
    # Get the original image
    original_image = imread(image_loc)
    # auto adjust contrast and brightness
    alpha, beta = calculate_alpha_beta(original_image)
    original_image = convertScaleAbs(original_image, alpha=alpha, beta=beta)
    # Predict sides of channel
    predicted_channel_sides = detect_channel_sides(original_image)
    # Use sides to predict position and size of pillar
    bbox, min_r, max_r = get_pillar_size_pos_range(
        predicted_channel_sides, original_image.shape
    )
    # Use hough circles
    circle = bounded_hough_circle(original_image, bbox, min_r=min_r, max_r=max_r)
    # Grab the pos
    pos = (int(circle[0]), int(circle[1]))
    radius = int(circle[2])
    return pos, radius
