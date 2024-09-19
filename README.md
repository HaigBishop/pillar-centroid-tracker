# Pillar Centroid Tracker (version 1.0.4)


## Badges


## Visuals


## Description:

This application provides semi-automated tracking of an elastomeric pillar across 
a sequence of images. The verified position data can then be used to calculate 
force values. The produced data can then be visualised as plots. This application 
is to be used alongside the elastomeric micropillar platform as described in:
    Tayagui et al., "An elastomeric micropillar platform for the study of protrusive 
    forces in hyphal invasion", Lab on a Chip, Vol. 17, No.21, pp. 3643-3653, 2017.


## Installation

- The .zip file can be extracted and the main python file pillar_centroid_tracker.py 
    can be executed. The program will run if the correct dependencies are installed.
    See below for the non-default Python dependencies.
- Alternatively, the .exe file can be executed. This does not require python to be
    installed on the machine, however the .exe file will only run on the Windows OS.
    Also, the .exe file is rather large due to the dependencies.


## Dependencies

- The application was written using Python 3.11.3
- The following Python packages are used by the application
    | PACKAGE NAME  | VERSION     | PURPOSE
    | Kivy          | 2.2.0       | GUI
    | opencv-python | 4.7.0.72    | Computer Vision
    | matplotlib    | 3.7.1       | Plot generation
    | imageio       | 2.30.0      | File Handling
    | pyler         | 2.1.0       | File Handling


## Usage

#### Track Pillar Position
1. select folders containing image sequences (or drag and drop)
   - the images are read in alphabetical order
   - the channel must be orientated vertically in the images
2. the app predicts the pillar position in the first frame
3. the user verifies the predicted position
    [see below for keyboard/mouse controls]
4. the app tracks the position across the sequence of images
(position files (.csv) are exported to the same directory as the images)

#### Verify Predicted Positions
1. select folders containing image sequences (or drag and drop)
2. select associated position file for each (or drag and drop)
    - files can be in .csv or .xml format
    - this can be adjusted at the bottom right of the file select window
3. the user verifies the positions
    [see below for keyboard/mouse controls]

#### Calculate Forces
1. select a position file (or drag and drop)
    - files can be in .csv or .xml format
    - this can be adjusted at the bottom right of the file select window
2. select the x and y pixel position columns
3. adjust parameters needed for force calculation
    [see below for parameters]
(force files (.csv) are exported to the same directory as the position file)

#### Generate Plots
1. select a force file (or drag and drop)
    - files can be in .csv or .xml format
    - this can be adjusted at the bottom right of the file select window
2. select each column from the file, and press continue
3. use the arrows to preview the 8 graphs available
4. adjust titles, plot types, and the y-axis range for each plot
5. select the file types and plots to be exported
(plot files (.svg/.png) are exported to a sub-directory alongside the force file)

#### Keyboard Controls
Z  -  zoom into circle
X  -  hide centre cross
C  -  hide circle
A  -  toggle axis overlay
S  -  save current image    (.png file is exported to a sub-directory)
D  -  toggle auto-contrast
F  -  toggle bulk position adjustment of all following frames
←/↓/↑/→  -  move circle
Ctrl + ←/→  -  change frame
Ctrl + ↓/↑  -  change job

#### Mouse Controls
Left Mouse  -  move circle
Scroll Up  -  increase circle radius
Scroll Down  -  decrease circle radius

#### Force Calculation Parameters
Pillar Diameter
  -  The diameter of the micropillar
  -  Defaults of 7.3 µm and 5.4 µm
Pillar Height
  -  The height of the micropillar
  -  Default of 11.1 µm
Pillar Contact
  -  The height of contact on the micropillar
  -  Default of 5.55 µm (half way up the pillar)
Pixel Micron Ratio
  -  The number of pixels per micron in the data
  -  Calculate with: [number of pixels] / [distance in microns]
  -  Default of 10 pixels per micron
Young's Modulus (Default of 1.47)
  -  A value describing the material properties of the pillar
  -  Default of 5.55 (Young's Modulus of PDMS)
Poisson's Ratio (Default of 0.5)
  -  A value describing the material properties of the pillar
  -  Default of 0.5 (Poisson's Ratio of PDMS)
Frame Frequency
  -  The number of frames per second in the data
  -  Calculate with: [number of frames] / [number of seconds]
  -  Default of 0.13 fps

#### File Formats:
1. CSV files which contain position or force data can be read by this application 
    - Position files must contain at least 3 columns which are selected in the app
    - Force files must contain at least 8 columns which are selected in the app
    - CSV files should have a header row
2. XML files which contain position or force data can be read by this application 
    - XML files are not generated by the app, however it is able to read them
    - XML files have the same restrictions as CSV files (stated above)
    - XML files should be in the same format used by TrackMate
    - The format must contain a 'particle' element enclosed by another element
    - Within the 'particle' element there must be 'detection' elements 
    - The attributes of the 'detection' elements are read as columns
    - See an example of a minimal XML file below
        <Tracks from="TrackMate v3.4.2">
          <particle>
            <detection t="0" x="132" y="148" />
            <detection t="1" x="132" y="151" />
          </particle>
        </Tracks>


## Files and Development Descriptions

There are several Python files which make this program, which are each described.
There are also some images, fonts, a .kv file and a .txt file.
#### Main:
  -  pillar_centroid_tracker  -  the main file for this application
#### Tracking and force calculation modules:
  -  start_point_detector.py  -  detects the pillar position given one image
  -  pillar_tracker.py  -  predicts the pillar position given multiple images
  -  force_conversion.py  -  calculates force values given position data
#### Graphic User Interface (using Kivy)
  -  pct.kv  -  contains the GUI styling for the entire application
  -  ip1.py  -  contains the functionality for the image -> posiiton screen 1
  -  ip2.py  -  contains the functionality for the image -> posiiton screen 2
  -  ps1.py  -  contains the functionality for the screening positions screen 1
  -  ps2.py  -  contains the functionality for the screening positions screen 2
  -  pf1.py  -  contains the functionality for the position -> force screen 1
  -  fg1.py  -  contains the functionality for the force -> plot screen 1
  -  fg2.py  -  contains the functionality for the force -> plot screen 2
  -  layout_elements  -  contains misc GUI elements
  -  popup_elements  -  contains popup GUI elements
#### Other:
  -  file_management  -  contains code for dealing with files


## License

MIT License
(see LICENSE.md)


## How to Site PCT

DOI: https://doi.org/10.5281/zenodo.8042121

## Author and Acknowledgments

Please feel free to contact me if you have any questions, feedback, or requests
  -  Author:         Haig Bishop
  -  Email:          hbi34@uclive.ac.nz
  -  Organisation:   University of Canterbury, New Zealand

A big thank you to Ashley Garrill, Volker Nock, and Ayelen Tayagui at UC for supporting this project!
