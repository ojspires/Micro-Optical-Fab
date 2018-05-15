# LinearFreeform.py   Oliver Spires   5/10/18
# This program takes an XYZ freeform profile from a .csv, and generates GCODE to cut a straight-line toolpath which
# follows that profile.
# TODO: this code is still unmodified from its inspiration, RadialToolpath.py

import numpy as np
import tkinter
from tkinter import filedialog
# import matplotlib.pyplot as plt
from datetime import datetime as dt
import csv
import copy
import sys


# Set up variables, in mm
cut_spacing = .0015
grating_DoC = .001
tangent_arc_radius = 60
half_diameter = 5
feed_rate = 2000
tool_radius = .05
bar_length = 60
now = dt.now()
in_out_length = .05


def radius_calc(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> tuple:
    ma = (y2-y1)/(x2-x1)
    mb = (y3-y2)/(x3-x2)
    if ma == 0 or mb == ma:
        radius = 'inf'
        y_center = 'inf'
    else:
        x_center = (ma * mb * (y1 - y3) + mb * (x1 + x2) - ma * (x2 + x3))/(2 * (mb - ma))
        y_center = -(1 / ma) * (x_center - (x1 + x2) / 2) + (y1 + y2) / 2
        radius = np.sqrt(np.square(x1 - x_center) + np.square(y1 - y_center))
    return radius, y_center


def tool_offset_calc(slope, t_radius):
    angle = np.arctan(slope)
    x_offset = t_radius * np.tan(angle) / np.sqrt(np.square(np.tan(angle)) + 1)
    y_offset = np.sqrt(np.square(t_radius) - np.square(x_offset))
    offsets = (x_offset, y_offset)
    return offsets


# Import the file
root = tkinter.Tk()
rtzfilename = filedialog.askopenfilename(initialdir="/", title="Select surface R-theta-Z .csv file", filetypes=(
    ("R-theta-Z .CSV Files", "*.csv"), ("all files", "*.*")))
rtzpath = rtzfilename.split("/")[0:-1]  # Take the path from the RTZ file
rtzpath = '/'.join(rtzpath)  # Rejoin it into a single string
surf = []
surfrow = []

minimum_radius = 10000
with open(rtzfilename, newline='') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in csvreader:
        for col in row:
            surfrow.append(float(col))
        surf.append(surfrow)
        surfrow = []
    # print(surf[0][0:10])
    # print(surf[1][0:10])
angular_resolution = surf[0][2] - surf[0][1]
radius_resolution = surf[2][0] - surf[1][0]
surf_slope = copy.deepcopy(surf)
surf_radius_index = np.linspace(0, np.size(surf, 0) - 1, np.size(surf, 0))
surf_angle_index = np.linspace(0, np.size(surf, 1) - 1, np.size(surf, 1))
introOutro = np.zeros((4, np.size(surf, 1)))
for r_index in surf_radius_index[1:]:
    # Progress bar:
    percent = float(r_index) / surf_radius_index[-1]
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\rProcessing slopes and offsets:   [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()
    # print(r_index)
    # print(surf_slope[int(r_index)][1])
    local_x = float(np.radians(angular_resolution) * surf[int(r_index)][0])
    local_slope = (surf[int(r_index)][2] - surf[int(r_index)][-1]) / (2 * local_x)
    # print(local_slope)
    local_radius = list(radius_calc(-local_x, surf[int(r_index)][-1], 0, surf[int(r_index)][1], local_x, surf[int(r_index)][2]))
    if local_radius[0] != 'inf':
        if local_radius[1] < surf[int(r_index)][1]:
            local_radius[0] = 'inf'
        else:
            minimum_radius = np.min((local_radius[0], minimum_radius))
    (local_x_offset, local_y_offset) = tool_offset_calc(local_slope, tool_radius)
    # if np.abs(local_x_offset) > local_x:  # pushover attempt
    #     local_x_offset = np.sign(local_x_offset) * local_x
    #     local_y_offset = np.sqrt(np.square(tool_radius) - np.square(local_x))
    # print(local_x_offset)
    # print(local_y_offset)
    surf_slope[int(r_index)][1] = [local_slope, local_radius[0], local_x_offset, local_y_offset + surf[int(r_index)][1]]
    # print(surf_slope[int(r_index)][1])
    # print(surf[int(r_index)][1])
    # print(surf[int(r_index)][-2])
    local_slope = (surf[int(r_index)][1] - surf[int(r_index)][-2]) / (2 * local_x)
    local_radius = list(radius_calc(-local_x, surf[int(r_index)][-2], 0, surf[int(r_index)][-1], local_x, surf[int(r_index)][1]))
    if local_radius[0] != 'inf':
        if local_radius[1] < surf[int(r_index)][1]:
            local_radius[0] = 'inf'
        else:
            minimum_radius = np.min((local_radius[0], minimum_radius))
    (local_x_offset, local_y_offset) = tool_offset_calc(local_slope, tool_radius)
    # if np.abs(local_x_offset) > local_x:  # pushover attempt
    #     local_x_offset = np.sign(local_x_offset) * local_x
    #     local_y_offset = np.sqrt(np.square(tool_radius) - np.square(local_x))
    surf_slope[int(r_index)][-1] = [local_slope, local_radius[0], local_x_offset, local_y_offset + surf[int(r_index)][-1]]
    for a_index in surf_angle_index[2:-1]:
        # print(surf[0][int(a_index)])
        local_slope = (surf[int(r_index)][int(a_index) + 1] - surf[int(r_index)][int(a_index) - 1]) / (2 * local_x)
        local_radius = list(radius_calc(-local_x, surf[int(r_index)][int(a_index) - 1], 0, surf[int(r_index)][int(a_index)], local_x, surf[int(r_index)][int(a_index) + 1]))
        if local_radius[0] != 'inf':
            if local_radius[1] < surf[int(r_index)][1]:
                local_radius[0] = 'inf'
            else:
                minimum_radius = np.min((local_radius[0], minimum_radius))
        (local_x_offset, local_y_offset) = tool_offset_calc(local_slope, tool_radius)
        # if np.abs(local_x_offset) > local_x:  # pushover attempt
        #     local_x_offset = np.sign(local_x_offset) * local_x
        #     local_y_offset = np.sqrt(np.square(tool_radius) - np.square(local_x))
        surf_slope[int(r_index)][int(a_index)] = [local_slope, local_radius[0], local_x_offset, local_y_offset + surf[int(r_index)][int(a_index)]]

        # print(surf_slope[int(r_index)][int(a_index)])
    # print(surf_slope[int(r_index)][0:10])
    # print(surf_slope[int(r_index)][-10:-1])
    for a_index in surf_angle_index[1:]:
        # Tangent lead-in and lead-out points calculation:
        if r_index == 2:
            # index 0:1 Out, index 2:3 In
            #     print(surf_slope[int(r_index)][int(a_index)])
            #     print(a_index)
            x_out_point = (surf_slope[int(r_index)][int(a_index)][2] - surf_slope[int(r_index-1)][int(a_index)][2]) / radius_resolution * -in_out_length + surf_slope[int(r_index-1)][int(a_index)][2]
            z_out_point = (surf_slope[int(r_index)][int(a_index)][3] - surf_slope[int(r_index-1)][int(a_index)][3]) / radius_resolution * -in_out_length + surf_slope[int(r_index-1)][int(a_index)][3]
            introOutro[0][int(a_index)] = x_out_point
            introOutro[1][int(a_index)] = z_out_point
        if r_index == surf_radius_index[-1]:
            x_in_point = (surf_slope[int(r_index)][int(a_index)][2] - surf_slope[int(r_index-1)][int(a_index)][2]) / radius_resolution * in_out_length + surf_slope[int(r_index)][int(a_index)][2]
            z_in_point = (surf_slope[int(r_index)][int(a_index)][3] - surf_slope[int(r_index-1)][int(a_index)][3]) / radius_resolution * in_out_length + surf_slope[int(r_index)][int(a_index)][3]
            introOutro[2][int(a_index)] = x_in_point
            introOutro[3][int(a_index)] = z_in_point
root.destroy()
# print(surf_slope[1][0])

# For calculation of whether the tool will clear or not: compare required X offset for coordinate (based on local slope)
# to arclength and neighboring X offsets

print('\nMinimum tool radius:             {:.4f}'.format(minimum_radius))

# Surface finish estimation
outerEdgeRadius = surf[-1][0]
innerEdgeRadius = surf[1][0]
outerEdgeArc = np.deg2rad(angular_resolution) * outerEdgeRadius
innerEdgeArc = np.deg2rad(angular_resolution) * innerEdgeRadius
inE = innerEdgeArc / 2
outE = outerEdgeArc / 2

practicalInnerSurF = 12.4109 + 4.0529/innerEdgeArc + .2317*innerEdgeArc**2/(8*tool_radius)
practicalOuterSurF = 12.4109 + 4.0529/outerEdgeArc + .2317*outerEdgeArc**2/(8*tool_radius)
innerEdgeSurfaceFinish = np.sqrt((1 / innerEdgeArc) * np.square(tool_radius) * ((-inE * np.sqrt(1 - (np.square(inE) / np.square(tool_radius))) + tool_radius * np.arcsin(-inE / tool_radius)) - (inE * np.sqrt(1 - (np.square(inE) / np.square(tool_radius))) + tool_radius * np.arcsin(inE / tool_radius)) + (inE - np.power(inE, 3)/(3 * np.square(tool_radius))) - (-inE - np.power(-inE, 3)/(3 * np.square(tool_radius))) + 2 * inE))
outerEdgeSurfaceFinish = np.sqrt((1 / outerEdgeArc) * np.square(tool_radius) * ((-outE * np.sqrt(1 - (np.square(outE) / np.square(tool_radius))) + tool_radius * np.arcsin(-outE / tool_radius)) - (outE * np.sqrt(1 - (np.square(outE) / np.square(tool_radius))) + tool_radius * np.arcsin(outE / tool_radius)) + (outE - np.power(outE, 3)/(3 * np.square(tool_radius))) - (-outE - np.power(-outE, 3)/(3 * np.square(tool_radius))) + 2 * outE))
print('Predicted inner surface finish: ', innerEdgeSurfaceFinish * 10**6, 'nmRMS')
print('Predicted outer surface finish: ', outerEdgeSurfaceFinish * 10**6, 'nmRMS')
print('Practical inner surface finish: ', practicalInnerSurF, 'nmRMS')
print('Practical outer surface finish: ', practicalOuterSurF, 'nmRMS')

# TODOne:     * resample for higher angular resolution if finish too high * done in NanoCAM 3D to 1440 points
# TODO:     * push toolpath over to fit in valley if tool_radius > minimum_radius   * implemented. Test failed and commented
# TODOne:     * find point tangent to each start coordinate   * implemented.
# TODOne:     * find point tangent to each end coordinate     * implemented.
# TODOne:     * toolpath code *implemented. test next.
# todone:         * edit variables to match this file rather than source file
# todone:         * replace scoop stuff with tangents, surface offsets, and reset path
# TODOne:     * add total progress bar
# TODOne:     * speed up GCODE generation
# TODO:     * check that angle (C coordinate) doesn't need to be reversed
# TODOne:     * fix incorrect slope in C = 0 column


"""
Tool Path Code Section
"""


ncmainoutfile = rtzfilename + ' Blazed Grating Main.nc'
ncchildfile = rtzfilename + ' Blazed Grating Child.nc'

header_blocks = '( File generated by RadialToolpath.py by Oliver Spires / ojspires@email.arizona.edu / 850-240-1897 ) \n( on: ' \
                + str(now)[:19] + \
                '. This script assumes a half-radius tool, calibrated in in position T0101.) ' \
                ' \n#541 = 2              ( Number of loops )' \
                ' \n#542 = 0.01           ( DoC )' \
                ' \n#543 = 1000           ( Feed )' \
                ' \n#506 = 0              ( Loop Counter )' \
                ' \n#547 = 0              ( Cut offset Var )' \
                ' \n \nG71 G01 G18 G40 G63 G90 G94 G54 \nT0101 \nG53 Z-180 F[#543]' \
                ' \nY0 \nM80 \nC0 \n\n( CUTTING BLOCKS ) \n' \
                ' \nM98(' + ncchildfile.split('/')[-1] + ')L#541 \n'
closeout_blocks = '\n( CLOSEOUT BLOCKS ) \nM79 \nM29 \nG52 \nG53 Z-180 F[#543] \nT0000 \nM30 \n'
# plt.plot(profile_x[1:], profile_z[1:])
# plt.show()
# print(np.size(profile_x))     # Show the size of the profile lists
profile_index = np.linspace(np.size(surf, 0) + 1, 1, np.size(surf, 0) + 1)  # reverse-order the indices
# print(profile_index)
cutting_blocks = ''  # Clear the cutting blocks and set it as a string so we can append the toolpath code
child_cutting = ''
# TODOne: nest this inside an angle loop

child_out = open(ncchildfile, 'w+')
child_header = '( ' + ncchildfile + ') \n( Called by ' + ncmainoutfile + ' ) \n( on: ' + str(now)[:19] + ' ) \n\n( LOOPING SETUP ) \n#547 = #547 - #542 \nG52 Z[#547] \n\n( CUTTING BLOCKS ) \n'
child_out.writelines(child_header)
for a_index in surf_angle_index[1:]:
    # Progress bar:
    percent = float(a_index) / surf_angle_index[-1]
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\rProcessing GCODE Output:         [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()
    child_cutting = ''

    for index in profile_index:

        # cutting_blocks = cutting_blocks + 'X' + str(profile_x[int(index)]) + ' Z' + str(profile_z[int(index)]) + ' \n'  # test
        if index == 1:  # index = 1 is the last one due to the [:-1] when setting profile_index
            # outro     TODOne: add Y and C coords    *implemented; test next
            # child_cutting = child_cutting + 'C{:.10f}'.format(surf[0][int(a_index)]) + \  # old formatting. reformatted to try to improve speed.
            #     ' X{:.10f}'.format(introOutro[2][int(a_index)]) + \
            #     ' Y{:.10f}'.format(surf[1][0] - in_out_length) + \
            #     ' Z{:.10f}'.format(introOutro[3][int(a_index)]) + ' \n'
            child_cutting = ' \n'.join([child_cutting,
                                        'C{:.10f} X{:.10f} Y{:.10f} Z{:.10f} (Outro)'.format(
                                            surf[0][int(a_index)],
                                            introOutro[0][int(a_index)],
                                            surf[1][0] - in_out_length,
                                            introOutro[1][int(a_index)])
                                        ])
            # print(str(index) + ' outro')
        elif index == profile_index[0]:
            # intro     TODOne: add Y and C coords    *implemented; test next
            # child_cutting = child_cutting + 'C{:.10f}'.format(surf[0][int(a_index)]) + \    # old formatting. reformatted to try to improve speed.
            #     ' X{:.10f}'.format(introOutro[2][int(a_index)]) + \
            #     ' Y{:.10f}'.format(surf[-1][0] + in_out_length) + \
            #     ' Z{:.10f}'.format(introOutro[3][int(a_index)]) + ' \n'
            child_cutting = ' \n'.join([child_cutting,
                                        'C{:.10f} X{:.10f} Y{:.10f} Z{:.10f} (Intro)'.format(
                                            surf[0][int(a_index)],
                                            introOutro[2][int(a_index)],
                                            surf[-1][0] + in_out_length,
                                            introOutro[3][int(a_index)])
                                        ])
            # print(str(index) + ' intro')
        else:
            # main path     TODOne: add Y coords and change source variable(s).   *implemented. test next.
            # child_cutting = child_cutting + 'C{:.10f}'.format(surf[0][int(a_index)]) + \    # old formatting. reformatted to try to improve speed.
            #     ' X{:.10f}'.format(surf_slope[int(index - 1)][int(a_index)][2]) + \
            #     ' Y{:.10f}'.format(surf[int(index - 1)][0]) + \
            #     ' Z{:.10f}'.format(surf_slope[int(index - 1)][int(a_index)][3]) + ' \n'
            child_cutting = ' \n'.join([child_cutting,
                                        'C{:.10f} X{:.10f} Y{:.10f} Z{:.10f}'.format(
                                            surf[0][int(a_index)],
                                            surf_slope[int(index - 1)][int(a_index)][2],
                                            surf[int(index - 1)][0],
                                            surf_slope[int(index - 1)][int(a_index)][3])
                                        ])
            # print(str(index) + ' surface')
        # start_x = profile_x[int(index)]  # Starting x coord     # TODOne: i don't think the rest of this loop's contents are necessary
        #    print(str(index))
        #    print(str(start_x) + ' ' + str(end_x))
        # start_z = profile_z[int(index)]  # Starting z coord
        #    print(str(start_z) + ' ' + str(end_z))
        # d = np.sqrt(np.square(end_x - start_x) + np.square(end_z - start_z))  # calculate the length of the segment
        # steps = int(np.ceil(d / cut_spacing))  # make the step size at most *cut_spacing* wide
        # path_x = np.linspace(start_x, end_x, steps)[:-1]  # do [:-1] to avoid duplicate coordinates at start/end points
        # path_z = np.linspace(start_z, end_z, steps)[:-1]

        # cutting_blocks = cutting_blocks + 'G52 X{:.10f}'.format(half_diameter - path_x[int(path)]) +\
        #                  ' Z{:.10f}'.format(path_z[int(path)]) + ' \n'  # Append the G52 offset for this pass. X is shifted by the half-diameter
        # cutting_blocks = cutting_blocks + 'G01 X0 Y{:.10f}'.format(scoop_y[0]) + ' \nM26 \nM98(' + ncchildfile.split('/')[-1] + ') \nM29 \n'
        # print(cutting_blocks[-1])

    child_cutting = ' \n'.join([
        child_cutting,
        '/M29 \nZ{:.10f} \nY{:.10f} \nZ{:.10f} \n/M26 \n'.format(
            introOutro[1][int(a_index)] + 2,
            surf[-1][0] + in_out_length,
            introOutro[3][int(a_index)])
    ])

    child_out.writelines(child_cutting)     # writing out to the file after every angle saves a TON of time!!!
# print(cutting_blocks)


child_footer = '\n ( CLOSEOUT BLOCKS ) \n#506 = #506 + 1\nM99 \n'

child_text = [child_header, child_cutting, child_footer]
main_text = [header_blocks, cutting_blocks, closeout_blocks]

main_out = open(ncmainoutfile, 'w+')  # designate the output file

main_out.writelines(main_text)
child_out.writelines(child_footer)
main_out.close()
child_out.close()
