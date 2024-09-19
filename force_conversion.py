"""
Module: The conversion of position data to force data
Program: Pillar Centroid Tracker
Author: Haig Bishop (hbi34@uclive.ac.nz)
"""

# Mathematical/graph imports
from math import pi, pow
import numpy as np
from statistics import mean


def force_convert_job(job):
    """takes a PF1 window job and processes the needed parameters for force conversion
    - returns the force converted values"""
    # Make all attributes floats
    job.floaterise()
    # Uses the fps to calculate the time values for each frame
    frame_nums = list(range(1, len(job.x_vals) + 1))
    t_vals = [(f - 1) / job.time_base for f in frame_nums]
    # Use the force convert function to get all force values
    return force_convert(
        frame_nums,
        job.pillar_diameter,
        job.pillar_height,
        job.pillar_contact,
        job.x_vals,
        job.y_vals,
        t_vals,
        job.pixel_micron_ratio,
        job.pdms_E,
        job.pdms_gama,
    )


def force_convert(
    frame_nums,
    pillar_diameter,
    pillar_height,
    pillar_contact,
    x_vals,
    y_vals,
    t_vals,
    pixel_micron_ratio,
    pdms_E,
    pdms_gama,
):
    """Takes all necessary values for force calculation
    - performs the force conversion
    - returns lists of the following...
        - frame numbers (frame_nums)
        - time values in seconds (t_vals)
        - force component in x-direction (force_x)
        - force component in y-direction (force_y)
        - total force (force_total)
        - average force component in x-direction (averageF_x)
        - average force component in y-direction (averageF_y)
        - total average force (averageF_total)
        - delta force in x-direction (delta_Fx)
        - delta force in y-direction (delta_Fy)
        - total delta force (delta_totalF)"""

    # Calculate moment of inertia
    pillar_I = pi * pow(pillar_diameter, 4) / 64
    # Calculate pillar area
    pillar_area = pi * pow(pillar_diameter, 2) / 4
    # Start Positions
    pillar_xstart = x_vals[0]
    pillar_ystart = y_vals[0]
    # Empty lists for displacement delta and forces
    delta_x, delta_y, delta_total, force_x, force_y, force_total = (
        [],
        [],
        [],
        [],
        [],
        [],
    )
    # Perfom displacement and force calculation across all elements
    for i in range(len(x_vals)):
        # Current pillar centre
        x_increment = x_vals[i]
        y_increment = y_vals[i]
        # Calculate deflections relative to initial pillar centre in um
        delta_x.append(pixel_micron_ratio * (x_increment - pillar_xstart))
        delta_y.append(pixel_micron_ratio * (y_increment - pillar_ystart))
        # Calculate total deflection relative to initial pillar centre in um
        delta_total.append(pow(pow(delta_x[i], 2) + pow(delta_y[i], 2), 0.5))
        # Calculate this for force calculations
        a = pow(pillar_contact, 3) / (3 * pdms_E * pillar_I)
        b = 20 * (1 + pdms_gama) * pillar_contact / (9 * pillar_area * pdms_E)
        c = (
            pow(pillar_contact, 2)
            * (pillar_height - pillar_contact)
            / (2 * pdms_E * pillar_I)
        )
        abc = a + b + c
        # Calculate force in each direction
        force_x.append(delta_x[i] / abc)
        force_y.append(delta_y[i] / abc)
        force_total.append(delta_total[i] / abc)

    # Get average abs values of force lists (non-zero elements only)
    all_are_zero = all([val == 0 for val in force_x])
    averageF_x = (
        0 if all_are_zero else mean(list(filter(lambda x: x != 0, map(abs, force_x))))
    )
    all_are_zero = all([val == 0 for val in force_y])
    averageF_y = (
        0 if all_are_zero else mean(list(filter(lambda x: x != 0, map(abs, force_y))))
    )
    all_are_zero = all([val == 0 for val in force_total])
    averageF_total = (
        0
        if all_are_zero
        else mean(list(filter(lambda x: x != 0, map(abs, force_total))))
    )
    # Get change of force between frames
    delta_totalF = np.concatenate(
        ([0], np.diff(force_total))
    )  # Subtract previous element from next list element and prepend 0 to match frames
    delta_Fx = np.concatenate(
        ([0], np.diff(list(map(abs, force_x))))
    )  # Subtract previous element from next list element and prepend 0 to match frames
    delta_Fy = np.concatenate(
        ([0], np.diff(list(map(abs, force_y))))
    )  # Subtract previous element from next list element and prepend 0 to match frames
    # Round numbers
    x_vals = [round(t) for t in x_vals]
    y_vals = [round(t) for t in y_vals]
    t_vals = [round(t, 2) for t in t_vals]
    force_x = [round(t, 1) for t in force_x]
    force_y = [round(t, 1) for t in force_y]
    force_total = [round(t, 1) for t in force_total]
    averageF_x = round(averageF_x, 1)
    averageF_y = round(averageF_y, 1)
    averageF_total = round(averageF_total, 1)
    delta_Fx = [round(t, 1) for t in delta_Fx]
    delta_Fy = [round(t, 1) for t in delta_Fy]
    delta_totalF = [round(t, 1) for t in delta_totalF]
    # Return the values!
    return (
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
    )
