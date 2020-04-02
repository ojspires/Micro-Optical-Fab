# PartContact.py    Oliver Spires   2/5/2020    University of Arizona
# Refs.:    http://math.stmarys-ca.edu/wp-content/uploads/2017/07/Kelly-Lynch.pdf
# Version 0.5: Working output to a test file. Not formatted for program generation yet.
# TODO for next revision: Speed up. see https://pybit.es/faster-python.html, https://wiki.python.org/moin/PythonSpeed/PerformanceTips
# TODO for next revision: Address some of the other TODOs
# TODO for next revision: Output with headers to either main/child .nc files, or monolithic file
# TODO for next revision: ensure that the part continues spinning near x = 0


# Outline:
# Surface Analysis
#  X, Z initial positions, C direction
#  X, C positions, non-plane feature within cutting width of tool (plus ?50% margin)?
#   If True:    max(feature_Z, plane_Z):
#       if 2 or more features, flag to check for collision
#       feature_Z: use C and X to calculate distance to vertex (d2v = r)
#       use r to get z from asph or sph equations
#       find local X slope and Y slope (Y slope for tool suitability checking)(Maybe this should be done in FreeformDefinition.py, before this script starts churning)
#           store max slope to report later
#       use slope to position tool
#       revert to initial set (inverse) feedrate
#       if flagged, check for collision and adjust offset to make tool tangent to both surface features if necessary (set a limit to the X adjustment to avoid criss-crossing toolpath lines)
#           store width of tangent points to report later
#   If False:   plane_Z, no delta_X
#       speed up if 360 degrees without delta_x PV change > ?0.000005    (this will speed up rotationally-symmetric portions of the part)
#           TO CONSIDER: how to trim this array? it will shrink in size as x->0 during constant arc cutting, and I still want to keep a P-V of the past 360 degrees worth of delta_X
#   progress indicator
# Toolpath build
#   Intro
#   Outro
#   Open output file ane write intro
#   Format body array during write out
#       progress indicator
#   place outro and close
# Report width of errors, max slope
# TODO: calculate the minimum diameter for the flat
# TODO: move the sag to the clipboard, for use in the flat definition

# Import:
import progressbar
import numpy as np
import tkinter
from tkinter import filedialog
import matplotlib.pyplot as plt
import sys
from Freeforms.FreeformDefinition import define_freeform
from Freeforms.FreeformDefinition import asphere_slope
from Freeforms.FreeformDefinition import asphere_sag
from Freeforms.FreeformDefinition import asphere_max_slope
from Freeforms.FreeformDefinition import check_cartesian_input
from Freeforms.CuttingDefinition import cut_def
import logging
import time
import os
# import getpass

# Initialize:
rot_string = outputFile = ''  # TODO: this can prob be deleted, i'm using mainfilename
introString = outroString = mainfilename = loopVariables = ''
edgeSag = cutDiameter = errorWidth = maxSlope = 0
toolRadiusSearchMargin = 1.5
# logger = logging.getLogger(__name__)
twoFeatures = planeFound = multiPass = False
testRun = True
machineName = 'Moore Nanotech 350FG'

# Setup:
max_part_slope = 0
logging.basicConfig(filename='Freeform Cutting Log.txt', filemode='w', level=logging.DEBUG)
# logger.setLevel('INFO')    # 'INFO' 'DEBUG' 'WARNING' 'ERROR'
logging.debug('Gathering features and arrays.')
arrayParameters = (features, arrays, all_array_coords) = define_freeform([], True)
logging.debug('Gathered. Gathering cutting parameters.')
cutParameters = (rotation, offset, tool_num, tool_radius, step_over, angular_sampling, step_ang, parking, mist_num, inverse_feed, total_doc, pass_doc) = cut_def()
mainfilename = tkinter.filedialog.asksaveasfilename(initialdir="G:\\My Drive\\Work", title="Select Output Location & Filename:", filetypes=[("G-code Files", ".nc")]).split('.nc')[0] + '.nc'
# mainfilename = mainfilename.split('.nc')[0] + '.nc'
semifilename = mainfilename.split('.nc')[0] + '_SF.nc'
finishfilename = mainfilename.split('.nc')[0] + '_FC.nc'
logging.debug('Gathered. Took filenames to potentially save to.')
if total_doc > pass_doc:
    multiPass = True
    loops = int(np.ceil(total_doc / pass_doc))
    loopVariables = '#599 = ' + str(loops) + '     ( Finish Cut Loops ) \n#589 = 0     ( Reinitialize Loop Counter ) \n'  # TODO: Enable semifinish cuts
logging.info(('Filename & Directory: ' + mainfilename))
logging.debug(('Feature Parameters: ' + str(arrayParameters)))
logging.debug(('Cutting Parameters: ' + str(cutParameters)))

for feature in features:
    if 'plane' in feature:
        logging.debug(('Plane diameter: ' + str(feature[1]) + '. This will be used to find the initial X position.'))
        planeFound = True
        cutDiameter = feature[1]
        edgeSag = feature[2]
    # TODOne: find max slope for each non-plane feature
    elif 'asphere' in feature:
        all_asph_constants = [0, 0, 0]  # Flesh out the aspheric constants list. The constants captured with define_freeform() are the evens starting with 4.
        for even in feature[4]:
            all_asph_constants.append(float(even))
            all_asph_constants.append(0)
        maxSlopeDetails = asphere_max_slope(feature[3], feature[6], feature[7], all_asph_constants)    # TODOne: feature[4] is the even aspheres starting with #4. The input needs to be from 1 to whatever.
        max_part_slope = max(max_part_slope, abs(maxSlopeDetails[1]))
        # print(maxSlopeDetails)
        print('Max Slope in ' + feature[0] + ' surface: ' + str(np.rad2deg(maxSlopeDetails[1]).__round__(2)) + '\u00b0 at x = ' + str(maxSlopeDetails[0].__round__(3)))
    else:   # This assumes only 'sphere', 'asphere', 'plane' surface types in FreeformDefinition.py
        maxSlopeDetails = asphere_max_slope(0, 1 / feature[1], feature[2] / 2, [])
        max_part_slope = max(max_part_slope, abs(maxSlopeDetails[1]))
        # print(maxSlopeDetails)
        print('Max Slope in ' + feature[0] + ' surface: ' + str(np.rad2deg(maxSlopeDetails[1]).__round__(2)) + '\u00b0 at x = ' + str(maxSlopeDetails[0].__round__(3)) + ' (edge).')
if planeFound:
    if rotation == 'CW':
        logging.debug('CW: C coordinates should increase. X coordinates should decrease towards zero for Edge -> Center cuts.')
        initialX = cutDiameter / 2
        rot_string = 'CW: Top of Design Currently = Top of Part'
    elif rotation == 'CCW':
        logging.debug('CCW: C coordinates should decrease. X coordinates should increase towards zero for Edge -> Center cuts.')
        initialX = -cutDiameter / 2
        rot_string = 'CCW: Top of Design Currently = Bottom of Part'
else:
    logging.critical('No planes found. Program has no starting point. Re-enter surface data, including a plane to define the diameter.')
    try:
        print(initialX)
    except ValueError:
        raise ValueError('No overall part diameter specified.')

# File Header
headerText = '(((          ' + mainfilename + '          )))\n( Generated ' + str(time.asctime()) + ' by ' + os.getlogin() + ' for ' + machineName + '. )\n( Features: ' + str(features) + ' )\n( Arrays: ' + str(arrays) + \
             ' )\n\n( ~~~ Clear Variables ~~~ )\n#500 = 500 \nWHILE [#500LT600] DO 1 \n#500 = #500 + 1 \n#[#500] = 0 \nEND1 \n#500 = 0 \n\n' \
             '( ~~~~~~~~~~~~~~~~ CAUTION ~~~~~~~~~~~~~~~~~ )\n( ~ Turn on OPTION STOP on first setup run ~ )\n( ~~~~~~~~~~~~~~~ /CAUTION/ ~~~~~~~~~~~~~~~~ )\n\n( BLOCK DELETE can be used to remain in Spindle mode for alignment/zeroing )\n\n'
# Let #500-549 be standard variables, #550-599 be variables that regulate and change within loops
variablesText = '( Set up Variables: )\n' + loopVariables + \
                '#510 = ' + str(mist_num) + '        ( Mist Number )\n#520 = ' + str(parking) + '    ( Z Parking Position )\n#530 = ' + str(inverse_feed) + '     ( Inverse Feedrate (seconds per line) )\n#531 = 200       ( Linear Feedrate Fast )\n#532 = 20        ( Linear Feedrate Approaching Spindle )\n'
leadInOutText = 'G53 Z[#520]F[#531]   ( Move fast to Parking Position ) \n'
leadInText = '/M80                  ( Home C Axis (Optional: omit with BLOCK DELETE) )\n' + \
             offset + '                   ( Fixture Offset )\n' + \
             tool_num + '                 ( Tool Offset )\n/C0F[#531]            ( Move to C0. ' + rot_string + \
             ' )\nM01                   ( Optional Stop: check clearance of X,Y,B-axes before turning off OPTION STOP )\nY0B0F[#531]           ( Zero Y and B for this Tool Offset )\nX' + \
             str(initialX) + '                 ( Fast move to initial X position )\nZ' + str(edgeSag + 2) + '            ( Fast move to 2mm above the part )\n'
logging.debug('Display the prepared header data:\n' + headerText + variablesText + leadInOutText + leadInText)


def array_topo(angle: float, radius: float, surf_features: list, surf_arrays: list, surf_array_coords: list, tool_r: float):
    rangle = np.deg2rad(angle)
    diamond_x = radius * np.cos(rangle)
    diamond_y = radius * np.sin(rangle)
    array_under_consideration = 0
    ignore_features = []
    distances = []
    if surf_arrays.__len__() > 0:
        for array in surf_arrays:
            feature_half_diameter = surf_features[array[0]][2] / 2
            feature_centers = surf_array_coords[array_under_consideration]
            center_index = 0
            for center in feature_centers:
                distance = ((diamond_x - center[0]) * (diamond_x - center[0]) + (diamond_y - center[1]) * (diamond_y - center[1])) ** .5
                # print(str(center) + ' Distance: ' + str(distance) + ' feature radius: ' + str(feature_half_diameter))
                if distance < feature_half_diameter + tool_r / 2:       # tool_r / 2 will allow up to 30 degrees of slope on a freeform surface (max slope for traversing the steepest edge of a sphere. I'm considering the clearance angle of the tools for this limit that I'm putting in place.)
                    logging.debug('Accepted: Array #' + str(array_under_consideration) + ' Center #' + str(center_index) + ' Distance: ' + str(distance) + ' diameter: ' + str(surf_features[array[0]][2]))
                    distances.append(['array', array_under_consideration, center_index, distance])
                else:
                    logging.debug('Rejected: Array #' + str(array_under_consideration) + ' Center #' + str(center_index) + ' Distance: ' + str(distance) + ' diameter: ' + str(surf_features[array[0]][2]) + ' tool center (x, y: mm): %s,%s', diamond_x, diamond_y)        # TODO: simplify strings like this: print( {or loggging.debug(} 'plah %s blah %s', var1, var2)
                center_index += 1
            ignore_features.append(array[0])
            array_under_consideration += 1
    feature_under_consideration = 0
    # print('Surf Features: ', surf_features)
    # print('Ignored Features: ', ignore_features)
    for surf_feature in surf_features:
        # print('Surf Feature: ', surf_feature)
        if feature_under_consideration in ignore_features:
            feature_under_consideration += 1
            continue
        elif 'plane' in surf_feature:
            distances.append(['feature', feature_under_consideration, [0, 0], 0])
            feature_under_consideration += 1
            continue
        else:
            center = [0, 0]
            if 'asphere' in surf_feature:
                center = surf_feature[5]
            elif 'sphere' in surf_feature:
                center = surf_feature[3]
            distance = ((diamond_x - center[0]) * (diamond_x - center[0]) + (diamond_y - center[1]) * (diamond_y - center[1])) ** .5
            if distance + tool_r < surf_feature[2] / 2:
                logging.debug('Feature #' + str(feature_under_consideration) + ' Center: ' + str(center) + ' Distance: ' + str(distance) + ' diameter: ' + str(surf_feature[2]))
                distances.append(['feature', feature_under_consideration, center, distance])
        # print('Distances returned from array_topo: ', distances)
        feature_under_consideration += 1
    return distances


# TODOne: debug array_topo()
# TODOne: function to determine height(s) at a given location. If array_topo() returns multiple results, interrogate all returns. If it returns one, interrogate it and 'plane'. Else: use 'plane' z.


def heights(angle: float, radius: float, surf_features: list, surf_arrays: list, surf_array_coords: list, tool_r: float):
    distances = array_topo(angle, radius, surf_features, surf_arrays, surf_array_coords, tool_r)
    # print('Distances: ', distances)
    height = slope = 0
    hs = []
    if distances.__len__() == 0:
        for surf_feature in surf_features:
            if 'plane' in surf_feature:
                height = surf_feature[-1]
                hs.append(height)
    for distance in distances:
        # print('Distance: ', distance)
        if 'array' in distance:
            # print('Feature: ', surf_features[distance[1]], ' Array: ' + str(distance[1]) + ' Index: ' + str(distance[2]) + ' Center: ' + str(surf_array_coords[distance[1]][distance[2]]) + ' at distance: ' + str(distance[-1]))
            if 'sphere' in surf_features[distance[1]]:
                surf_conic = 0
                surf_terms = []
                surf_curv = 1 / surf_features[distance[1]][1]
            elif 'asphere' in surf_features[distance[1]]:
                surf_conic = surf_features[distance[1]][3]
                surf_terms = [0, 0, 0]  # Flesh out the aspheric constants list. The constants captured with define_freeform() are the evens starting with 4.
                for surf_even in surf_features[distance[1]][4]:
                    surf_terms.append(float(surf_even))
                    surf_terms.append(0)
                surf_curv = surf_features[distance[1]][6]
            # slope = np.rad2deg(asphere_slope(surf_conic, surf_curv, distance[-1], surf_terms))
            # print('Slope at this point (degrees): ' + str(slope))
            height = asphere_sag(surf_conic, surf_curv, distance[-1], surf_terms)   # Added this line to enable output of height data
            # print('Sag at this point (mm): ' + str(height))
            hs.append(height)
        elif 'feature' in distance:
            # print(distance)
            # print(surf_features)
            # input('Pausing to show distance and surf_features: ')
            if 'sphere' in surf_features[distance[1]]:
                surf_conic = 0
                surf_terms = []
                surf_curv = 1 / surf_features[distance[1]][1]
                height = asphere_sag(surf_conic, surf_curv, distance[-1], surf_terms)  # Added this line to enable output of height data
            elif 'asphere' in surf_features[distance[1]]:
                surf_conic = surf_features[distance[1]][3]
                surf_terms = [0, 0,
                              0]  # Flesh out the aspheric constants list. The constants captured with define_freeform() are the evens starting with 4.
                for surf_even in surf_features[distance[1]][4]:
                    surf_terms.append(float(surf_even))
                    surf_terms.append(0)
                surf_curv = surf_features[distance[1]][6]
                height = asphere_sag(surf_conic, surf_curv, distance[-1], surf_terms)  # Added this line to enable output of height data
            elif 'plane' in surf_features[distance[1]]:
                height = surf_features[distance[1]][2]

            # print('Sag at this point (mm): ' + str(height))
            hs.append(height)
    # TODOne: insert code to match up slopes between the tool and the 3D surface. If multiple surfaces are in the variable distances, choose the higher one (for CX) or lower one (for CV)
    # TODOne: Differentiate slope signs. Currrently both the left and right features will have the same sign on their slopes    --Irrelevant. brute-force tool-surface mating used instead of slope matching. 100nm X resolution is good enough for now.
    # TODOne: set a finer x sampling resolution for small tool radii

    # if hs.__len__() > 1:
    #     print(hs)
    height = max(hs)
    return height

# use max_part_slope as input, in radians and tool_radius in mm
def tool_edge(max_part_slope_for_tool: float, tool_r: float):
    limit = (tool_r * np.sin(np.arctan(max_part_slope_for_tool))).round(4)
    print(limit)
    if tool_r < 0.3:
        resolution = 0.00001
    else:
        resolution = 0.0001
    tool_xes = np.arange(-limit, limit, resolution)
    tool_slopes = np.arccos(tool_xes / tool_r)
    tool_zees = tool_r * (1 - np.sin(tool_slopes))
    return tool_xes, tool_slopes, tool_zees


def local_profile(tool_x: float, part_theta: float, x_variation: list, surf_features: list, surf_arrays: list, surf_array_coords: list, tool_r: float):     # x_variation should be pulled from the returned tool_xes list
    zees = []
    for x in x_variation:
        if tool_x + x < 0:
            z = heights(part_theta + 180, abs(tool_x + x), surf_features, surf_arrays, surf_array_coords, tool_r)
        else:
            z = heights(part_theta, tool_x + x, surf_features, surf_arrays, surf_array_coords, tool_r)
        zees.append(z)
    return zees


print('Point Height at zero deg. and Initial X position: ', heights(0, initialX, features, arrays, all_array_coords, tool_radius))
# Test block for height calculation function
while testRun:
    # print(max_part_slope)
    [t_x, t_s, t_z] = tool_edge(max_part_slope, tool_radius)
    # print(t_x, t_x, t_z)
    try:
        x_test = input('Enter the x position to test (type "exit" to end test): ')
        if x_test == 'exit':
            testRun = False
            continue
        x_test = abs(float(x_test))
    except ValueError:
        try:
            print('Invalid x input. Entered: ', + x_test)
        except TypeError:
            print('Invalid Input. Reenter.')
    try:
        ang_test = input('Enter the theta position to test (type "exit" to end test): ')
        if ang_test == 'exit':
            testRun = False
            continue
        ang_test = float(ang_test)
    except ValueError:
        try:
            print('Invalid theta input. Entered: ' + ang_test)
        except TypeError:
            print('Invalid input. Reenter.')
    print('Point Height(s), Slope(s) at entered position: ', heights(ang_test, x_test, features, arrays, all_array_coords, tool_radius))
    profile_z = local_profile(x_test, ang_test, t_x, features, arrays, all_array_coords, tool_radius)
    # plt.plot(t_x, t_z, t_x, profile_z)
    z_adjust = min(t_z - profile_z)
    print(z_adjust)
    plt.plot(t_x, profile_z, t_x, t_z - z_adjust)
    plt.show()
    # TODOne: distances is not working for arrays. Parameters that break this test: sphere R-20 D5, 3x3x4mm array centered, test point 5.5mm, 0deg.

"""
END PART CONTACT CALCULATION SECTION

BEGIN TOOLPATH CALCULATION SECTION
"""
"""
                0           1       2       3               4           5                  
cutParameters:  rotation, offset, tool_num, tool_radius, step_over, angular_sampling, 
                 6           7       8       9               10          11   
                step_ang, parking, mist_num, inverse_feed, total_doc, pass_doc
initialX
parking
rotation
step_over
step_ang
"""
if rotation == 'CCW':
    initialX = -initialX
    step_ang = -step_ang
elif rotation == 'CW':
    step_over = -step_over
x_actual = initialX
c_actual = float(0)
[t_x, t_s, t_z] = tool_edge(max_part_slope, tool_radius)
# outputBuffer = ''
testfile = 'test.txt'
outfile = testfile
out = open(outfile, mode='w+')
out.write('( Begin Coordinates ) \n')
while x_actual >= 0:
    # Intervals:
    if angular_sampling == 'CR':
        approx_points_per_rot = int(2 * np.pi / (step_ang / (abs(x_actual) - abs(step_over) / 2)))
        ang_step_per_point = np.rad2deg(step_ang / x_actual)
    elif angular_sampling == 'CA':
        approx_points_per_rot = int(360 / abs(step_ang))
        ang_step_per_point = step_ang
    x_step_per_point = step_over / max(1, approx_points_per_rot)

    # Actual height:
    profile_z = local_profile(x_actual, c_actual, t_x, features, arrays, all_array_coords, tool_radius)
    # plt.plot(t_x, t_z, t_x, profile_z)
    z_adjust = min(t_z - profile_z)
    # print(z_adjust)
    # plt.plot(t_x, profile_z, t_x, t_z - z_adjust)
    # plt.show()
    z_actual = -z_adjust

    # Output:
    out_line = 'C{:.7} X{:.9} Z{:.9} \n'.format(np.mod(c_actual, 360), x_actual, z_actual)
    # if out_line.__len__() < 34:
    print('{:.2%}'.format((initialX - x_actual) / initialX))
    # print(out_line)
    out.write(out_line)

    # Prep for next:
    x_actual = x_actual + x_step_per_point
    c_actual = c_actual + ang_step_per_point

out.write('G94 \n Z{:-.3} F20 \n'.format(parking))
out.close()

