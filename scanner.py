# {{ CityScope Python Scanner }}
# Copyright (C) {{ 2018 }}  {{ Ariel Noyman }}

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# "@context": "https://github.com/CityScope/", "@type": "Person", "address": {
# "@type": "75 Amherst St, Cambridge, MA 02139", "addressLocality":
# "Cambridge", "addressRegion": "MA",},
# "jobTitle": "Research Scientist", "name": "Ariel Noyman",
# "alumniOf": "MIT", "url": "http://arielnoyman.com",
# "https://www.linkedin.com/", "http://twitter.com/relno",
# https://github.com/RELNO]


##################################################

# CityScope Python Scanner
# Keystone, decode and send over UDP a 2d array
# of uniquely tagged LEGO array

##################################################

# raise SystemExit(0)

import cv2
import numpy as np
import modules

##################################################
# define the grid size
grid_dimensions_x = 6
grid_dimensions_y = 3


# load json file
array_of_tags_from_json = modules.parse_json_file('tags')
array_of_maps_form_json = modules.parse_json_file('map')
array_of_rotations_form_json = modules.parse_json_file('rotation')

# load the initial keystone data from file
keystone_points_array = np.loadtxt('DATA/keystone.txt', dtype=np.float32)

# define the video
video_capture = cv2.VideoCapture(0)

# get video resolution from webcam
video_resolution_x = int(video_capture.get(3))
video_resolution_y = int(video_capture.get(4))

# number of overall modules in the table x dimension
number_of_table_modules = 14

# scale of one module in actual pixel size over the x axis
one_module_scale = int(video_resolution_x/number_of_table_modules)

# define the size for each scanner
scanner_square_size = int(one_module_scale/2)

# define the video window
cv2.namedWindow('CityScopeScanner', cv2.WINDOW_NORMAL)
cv2.resizeWindow('CityScopeScanner', 1000, 1000)

# make the sliders GUI
modules.create_user_intreface(
    keystone_points_array, video_resolution_x, video_resolution_y)

# call colors dictionary
colors_from_dictionary = {
    # black
    0: (0, 0, 0),
    # white
    1: (255, 255, 255)
}

# create the location  array of scanners
array_of_scanner_points_locations = modules.get_scanner_pixel_coordinates(
    video_resolution_x, one_module_scale,  scanner_square_size)

# holder of old cell colors array to check for new scan
old_cell_colors_array = []

##################################################
###################MAIN LOOP######################
##################################################

# run the video loop forever
while(True):

    # get a new matrix transformation every frame
    keyStoneData = modules.keystone(
        video_resolution_x, video_resolution_y, modules.listen_to_slider_interaction())

    # zero an array to collect the scanners
    cell_Colors_Array = []

    # read video frames
    _, thisFrame = video_capture.read()

    # warp the video based on keystone info
    distortVid = cv2.warpPerspective(
        thisFrame, keyStoneData, (video_resolution_x, video_resolution_y))

    ##################################################

    # run through locations list and make scanners
    for this_scanner_location in array_of_scanner_points_locations:

        # set x and y from locations array
        x = this_scanner_location[0]
        y = this_scanner_location[1]

        # use this to control reduction of scanner size
        this_scanner_max_dimension = int(scanner_square_size/2)

        # set scanner crop box size and position
        # at x,y + crop box size
        this_scanner_size = distortVid[y:y + this_scanner_max_dimension,
                                       x:x + this_scanner_max_dimension]

        # draw rects with mean value of color
        mean_color = cv2.mean(this_scanner_size)

        # convert colors to rgb
        b, g, r, _ = np.uint8(mean_color)
        mean_color_RGB = np.uint8([[[b, g, r]]])

        # select the right color based on sample
        scannerCol = modules.select_color_by_mean_value(mean_color_RGB)

        # add colors to array for type analysis
        cell_Colors_Array.append(scannerCol)

        # get color from dict
        thisColor = colors_from_dictionary[scannerCol]

        # draw rects with frame colored by range result
        cv2.rectangle(distortVid, (x, y),
                      (x+this_scanner_max_dimension,
                       y+this_scanner_max_dimension),
                      thisColor, 3)

##################################################

    # reduce unnecessary scan analysis and sending by comparing
    # the list of scanned cells to an old one
    if cell_Colors_Array != old_cell_colors_array:

        # send array to check types
        types_list = modules.find_type_in_tags_array(
            cell_Colors_Array, array_of_tags_from_json,
            array_of_maps_form_json,
            array_of_rotations_form_json)

        # send using UDP
        modules.send_over_UDP(types_list)

        # match the two
        old_cell_colors_array = cell_Colors_Array
    else:
        pass

    # add type and pos text
    cv2.putText(distortVid, 'Types: ' + str(types_list),
                (50, 50), cv2.FONT_HERSHEY_DUPLEX,
                0.5, (0, 0, 0), 1)

    # draw the video to screen
    cv2.imshow("CityScopeScanner", distortVid)

    ##################################################
    #####################INTERACTION##################
    ##################################################

    # break video loop by pressing ESC
    key = cv2.waitKey(1)
    if chr(key & 255) == 'q':
        # break the loop
        break

    # # saves to file
    elif chr(key & 255) == 's':
        modules.save_keystone_to_file(modules.listen_to_slider_interaction())

# close opencv
video_capture.release()
cv2.destroyAllWindows()