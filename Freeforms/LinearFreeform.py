#!C:\Program Files\Python36\python.exe
# LinearFreeform.py   Oliver Spires   5/10/18
# This program takes an XYZ freeform profile from a .csv, and generates GCODE to cut a straight-line toolpath which
# follows that profile.
# TODOne: this code is still unmodified from its inspiration, RadialToolpath.py
# TODOne: Only the X=5.0000 is showing up. troubleshoot.
# Edit 11/5-11/6/2018: Code didn't work on second run of target part. Edited to repair.

# Import Modules:
from typing import List, Any
import numpy as np
import tkinter
from tkinter import filedialog
# import matplotlib.pyplot as plt
from datetime import datetime as dt
import csv
# import copy
import sys
import random

# Set up variables, in mm
cut_spacing = .005
grating_DoC = .005
tangent_arc_radius = 60
half_diameter = 5
feed_rate = 800
tool_radius = .097621
bar_length = 60
now = dt.now()
in_out_length = .05
l_junk = 0
r_junk = 0
totes_junk = -0.84609787
debug = True
ranFin = ['Done.','Donezo.','Fin.','Finite Incantatum.','The End.']


# Define Functions
def radius_calc(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> tuple:
    ma = (y2 - y1) / (x2 - x1)
    mb = (y3 - y2) / (x3 - x2)
    if ma == 0 or mb == ma:
        radius = 'inf'
        y_center = 'inf'
    else:
        x_center = (ma * mb * (y1 - y3) + mb * (x1 + x2) - ma * (x2 + x3)) / (2 * (mb - ma))
        y_center = -(1 / ma) * (x_center - (x1 + x2) / 2) + (y1 + y2) / 2
        radius = np.sqrt(np.square(x1 - x_center) + np.square(y1 - y_center))
    return radius, y_center


def tool_offset_calc(slope, t_radius):
    angle = np.arctan(slope)
    x_offset = t_radius * np.tan(angle) / np.sqrt(np.square(np.tan(angle)) + 1)
    y_offset = np.sqrt(np.square(t_radius) - np.square(x_offset))
    offsets = (x_offset, y_offset)
    return offsets


def surf_offset_calc(row_func, x_row_func, x_index_func, left_junk_data, right_junk_data, local_x_func, part_radius):
    point_radius_func = np.sqrt(np.square(row_func[0]) + np.square(x_row_func[int(x_index_func)]))
    if (row_func[int(x_index_func)] == left_junk_data
        or row_func[int(x_index_func)] == right_junk_data) \
            and point_radius_func >= part_radius:
        local_slope_func = 0
        local_radius_func: List[Any] = ['inf', 'inf']
    elif (x_index_func == 1
          and row_func[int(x_index_func)] != left_junk_data) \
            or (row_func[int(x_index_func) - 1] == left_junk_data
                and point_radius_func >= part_radius * .9
                and row_func[int(x_index_func)] != left_junk_data):
        local_slope_func = (row_func[int(x_index_func) + 1] - row_func[int(x_index_func)]) / local_x_func
        local_radius_func: List[Any] = ['inf', 'inf']
    elif (row_func[int(x_index_func)] == row_func[-1]
          and row_func[int(x_index_func)] != right_junk_data) \
            or (row_func[int(x_index_func) + 1] == right_junk_data
                and point_radius_func >= part_radius * .9
                and row_func[int(x_index_func)] != left_junk_data):
        local_slope_func = (row_func[int(x_index_func)] - row_func[int(x_index_func) - 1]) / local_x_func
        local_radius_func: List[Any] = ['inf', 'inf']
    else:
        local_slope_func = (row_func[int(x_index_func) + 1] - row_func[int(x_index_func) - 1]) / (2 * local_x_func)
        local_radius_func = list(radius_calc(-local_x_func, row_func[int(x_index_func) - 1], 0,
                                             row_func[int(x_index_func)], local_x_func,
                                             row_func[int(x_index_func) + 1]))
    (local_x_offset_func, local_y_offset_func) = tool_offset_calc(local_slope_func, tool_radius)
    return local_slope_func, local_radius_func[0], -local_x_offset_func + x_row_func[
        int(x_index_func)], -local_y_offset_func + row_func[int(x_index_func)]


# Import the file
root = tkinter.Tk()
xyz_filename = filedialog.askopenfilename(initialdir="/", title="Select surface XYZ .csv file", filetypes=(
    ("XYZ .CSV Files", "*.csv"), ("all files", "*.*")))
xyz_path = xyz_filename.split("/")[0:-1]  # Take the path from the RTZ file
xyz_path = '/'.join(xyz_path)  # Rejoin it into a single string
surf = []
surf_row = []

minimum_radius = 10000
with open(xyz_filename, newline='') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',', quotechar='|')
    for row in csv_reader:
        for col in row:
            if col!='':
                surf_row.append(float(col))
        surf.append(surf_row)
        surf_row = []
    # print(surf[0][0:10])
    # print(surf[1][0:10])
x_resolution = surf[0][2] - surf[0][1]
y_resolution = surf[2][0] - surf[1][0]
surf = np.rot90(surf)
root.destroy()
surf_slope = [[0 for x in range(np.size(surf, 1))] for y in range(np.size(surf, 0))]
surf_y_index = np.linspace(0, np.size(surf, 0) - 1, np.size(surf, 0))
surf_x_index = np.linspace(0, np.size(surf, 1) - 1, np.size(surf, 1))
junk_rows = []

for y_index in surf_y_index[:-1]:
    # Progress bar:
    percent = float(y_index) / surf_y_index[-1]
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\rProcessing slopes and offsets:   [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()
    if surf[int(y_index)][1] == totes_junk:
        junk_rows.append(y_index)
        continue
    for x_index in surf_x_index[1:]:
        surf_slope[int(y_index)][int(x_index)] = surf_offset_calc(surf[int(y_index)], surf[-1], x_index, l_junk, r_junk,
                                                                  x_resolution, half_diameter)
        # print(surf_slope[int(y_index)][int(x_index)])
        if surf_slope[int(y_index)][int(x_index)][1] != 'inf':
            minimum_radius = np.min((surf_slope[int(y_index)][int(x_index)][1], minimum_radius))

surf = np.delete(surf, np.array(junk_rows), 0)
surf_y_index = np.linspace(0, np.size(surf, 0) - 1, np.size(surf, 0))
introOutro = np.zeros((4, np.size(surf, 1)))
print('\n')
if debug:
    in_out_choice = np.zeros((2, np.size(surf, 1)))

for y_index in surf_y_index[:-1]:
    # Progress bar:
    percent = float(y_index) / surf_y_index[-1]
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\rProcessing in/out coordinates:   [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()

    for x_index in surf_x_index[1:]:
        point_radius = np.sqrt(np.square(surf[int(y_index)][0]) + np.square(surf[-1][int(x_index)]))
        if (point_radius < half_diameter * .9 or point_radius > half_diameter * 1.1) and y_index != surf_y_index[-2]:
            continue
        # Tangent lead-in and lead-out points calculation:
        if y_index == 1 and surf[0][int(x_index)] != 0:
            # index 0:1 Out, index 2:3 In
            #     print(surf_slope[int(r_index)][int(a_index)])
            #     print(a_index)
            introOutro[0][int(x_index)] = (surf_slope[int(y_index)][int(x_index)][2] -
                                           surf_slope[int(y_index - 1)][int(x_index)][2]) / \
                                           x_resolution * -in_out_length + surf_slope[int(y_index - 1)][int(x_index)][2]
            introOutro[1][int(x_index)] = (surf_slope[int(y_index)][int(x_index)][3] -
                                           surf_slope[int(y_index - 1)][int(x_index)][3]) / \
                                           y_resolution * -in_out_length + surf_slope[int(y_index - 1)][int(x_index)][3]
            if debug:
                in_out_choice[1][int(x_index)] = 1
        elif y_index == surf_y_index[-2] and surf[int(y_index)][int(x_index)] != 0:
            introOutro[2][int(x_index)] = (surf_slope[int(y_index)][int(x_index)][2] -
                                           surf_slope[int(y_index - 1)][int(x_index)][2]) / \
                                           x_resolution * in_out_length + surf_slope[int(y_index)][int(x_index)][2]
            introOutro[3][int(x_index)] = (surf_slope[int(y_index)][int(x_index)][3] -
                                           surf_slope[int(y_index - 1)][int(x_index)][3]) / \
                                           y_resolution * in_out_length + surf_slope[int(y_index)][int(x_index)][3]
            if debug:
                in_out_choice[0][int(x_index)] = 2
        elif surf[int(y_index)][int(x_index)] != 0 and surf[int(y_index) - 1][int(x_index)] == 0:
            if surf[int(y_index) - 1][int(x_index)] == 0 and surf[int(y_index) + 1][int(x_index)] == 0:
                x_out_point = x_in_point = surf_slope[int(y_index)][int(x_index)][2]
                z_out_point = z_in_point = surf_slope[int(y_index)][int(x_index)][3]
                introOutro[0][int(x_index)] = introOutro[2][int(x_index)] = x_out_point
                introOutro[1][int(x_index)] = introOutro[3][int(x_index)] = z_out_point
                if debug:
                    in_out_choice[0][int(x_index)] = in_out_choice[1][int(x_index)] = 3
            else:
                x_out_point = (surf_slope[int(y_index) + 1][int(x_index)][2] -
                               surf_slope[int(y_index)][int(x_index)][2]) / \
                               y_resolution * -in_out_length + surf_slope[int(y_index)][int(x_index)][2]
                z_out_point = (surf_slope[int(y_index) + 1][int(x_index)][3] -
                               surf_slope[int(y_index)][int(x_index)][3]) / \
                               y_resolution * -in_out_length + surf_slope[int(y_index)][int(x_index)][3]
                introOutro[0][int(x_index)] = x_out_point
                introOutro[1][int(x_index)] = z_out_point
                if debug:
                    in_out_choice[1][int(x_index)] = 4
        elif surf[int(y_index)][int(x_index)] != 0 and surf[int(y_index) + 1][int(x_index)] == 0:
            x_in_point = surf_slope[int(y_index)][int(x_index)][2] + (surf_slope[int(y_index)][int(x_index)][2] -
                         surf_slope[int(y_index) - 1][int(x_index)][2]) / y_resolution * in_out_length
            z_in_point = surf_slope[int(y_index)][int(x_index)][3] + (surf_slope[int(y_index)][int(x_index)][3] -
                         surf_slope[int(y_index) - 1][int(x_index)][3]) / y_resolution * in_out_length
            introOutro[2][int(x_index)] = x_in_point
            introOutro[3][int(x_index)] = z_in_point
            if debug:
                in_out_choice[0][int(x_index)] = 5

# print(surf_slope[1][0])

# For calculation of whether the tool will clear or not: compare required X offset for coordinate (based on local slope)
# to arclength and neighboring X offsets

print('\nMaximum tool radius:             {:.4f}mm'.format(minimum_radius))

# Surface finish estimation
outerEdgeRadius = surf[-2][0]
innerEdgeRadius = surf[0][0]
outerEdgeArc = x_resolution
innerEdgeArc = x_resolution
inE = innerEdgeArc / 2
outE = outerEdgeArc / 2

practicalInnerSurF = 12.4109 + 4.0529 / innerEdgeArc + .2317 * innerEdgeArc ** 2 / (8 * tool_radius)
practicalOuterSurF = 12.4109 + 4.0529 / outerEdgeArc + .2317 * outerEdgeArc ** 2 / (8 * tool_radius)
innerEdgeSurfaceFinish = np.sqrt((1 / innerEdgeArc) * np.square(tool_radius) *
                                 ((-inE * np.sqrt(1 - (np.square(inE) / np.square(tool_radius))) +
                                   tool_radius * np.arcsin(-inE / tool_radius)) -
                                  (inE * np.sqrt(1 - (np.square(inE) / np.square(tool_radius))) +
                                   tool_radius * np.arcsin(inE / tool_radius)) +
                                  (inE - np.power(inE, 3) / (3 * np.square(tool_radius))) -
                                  (-inE - np.power(-inE, 3) / (3 * np.square(tool_radius))) + 2 * inE))
outerEdgeSurfaceFinish = np.sqrt((1 / outerEdgeArc) * np.square(tool_radius) *
                                 ((-outE * np.sqrt(1 - (np.square(outE) / np.square(tool_radius))) +
                                   tool_radius * np.arcsin(-outE / tool_radius)) -
                                  (outE * np.sqrt(1 - (np.square(outE) / np.square(tool_radius))) +
                                   tool_radius * np.arcsin(outE / tool_radius)) +
                                  (outE - np.power(outE, 3) / (3 * np.square(tool_radius))) -
                                  (-outE - np.power(-outE, 3) / (3 * np.square(tool_radius))) + 2 * outE))
print('Predicted inner surface finish: ', innerEdgeSurfaceFinish * 10 ** 6, 'nmRMS')
print('Predicted outer surface finish: ', outerEdgeSurfaceFinish * 10 ** 6, 'nmRMS')
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

ncmainoutfile = xyz_filename + ' Blazed Grating Main.nc'
ncchildfile = xyz_filename + ' Blazed Grating Child.nc'

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
profile_index = np.linspace(np.size(surf, 0) - 1, 0, np.size(surf, 0))  # reverse-order the indices
# print(profile_index)
cutting_blocks = ''  # Clear the cutting blocks and set it as a string so we can append the toolpath code
child_cutting = ''
# TODOne: nest this inside an angle loop

child_out = open(ncchildfile, 'w+')
child_header = '( ' + ncchildfile + ') \n( Called by ' + ncmainoutfile + ' ) \n( on: ' + str(now)[
                                                                                         :19] + ' ) \n\n( LOOPING SETUP ) \n#547 = #547 - #542 \nG52 Z[#547] \n\n( CUTTING BLOCKS ) \n'
child_out.writelines(child_header)
for x_index in surf_x_index[1:]:
    # Progress bar:
    percent = float(x_index) / surf_x_index[-1]
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\rProcessing GCODE Output:         [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()
    child_cutting = ''

    for index in profile_index:
        if surf[int(index)][int(x_index)] == 0 or index == profile_index[0]:
            continue
        elif surf[int(index)][int(x_index)] != 0 and index == 0:
            child_cutting = ' \n'.join([child_cutting,
                                        'C0 X{:.10f} Y{:.10f} Z{:.10f} (Outro)'.format(
                                            introOutro[0][int(x_index)],
                                            -surf[int(index)][0] - in_out_length,
                                            introOutro[1][int(x_index)])
                                        ])
            if debug:
                child_cutting = ' '.join([child_cutting, '{:1f}'.format(in_out_choice[1][int(x_index)])])
        elif surf[int(index)][int(x_index)] != 0 and surf[int(index) - 1][int(x_index)] == 0 and \
                surf[int(index) + 1][int(x_index)] == 0:
            child_cutting = ' \n'.join([child_cutting,
                                        'C0 X{:.10f} Y{:.10f} Z{:.10f} \n/M26 \n'
                                        'C0 X{:.10f} Y{:.10f} Z{:.10f} (Intro)\n'
                                        'C0 X{:.10f} Y{:.10f} Z{:.10f} \n'
                                        'C0 X{:.10f} Y{:.10f} Z{:.10f} (Outro)'.format(
                                            introOutro[2][int(x_index)],
                                            -surf[int(index)][0] + in_out_length,
                                            introOutro[3][int(x_index)] + 10,

                                            introOutro[2][int(x_index)],
                                            -surf[int(index)][0] + in_out_length,
                                            introOutro[3][int(x_index)],

                                            surf_slope[int(index)][int(x_index)][2],
                                            -surf[int(index)][0],
                                            surf_slope[int(index)][int(x_index)][3],

                                            introOutro[0][int(x_index)],
                                            -surf[int(index)][0] - in_out_length,
                                            introOutro[1][int(x_index)])
                                        ])
            if debug:
                child_cutting = ' '.join([child_cutting, '{:1f} {:1f}'.format(in_out_choice[0][int(x_index)],
                                                                              in_out_choice[1][int(x_index)])])
        elif surf[int(index)][int(x_index)] != 0 and ((surf[int(index) - 1][int(x_index)] == 0 and index - 1 == 0) or (surf[int(index) - 1][int(x_index)] == 0 and surf[int(index) - 2][int(x_index)] == 0)):
            child_cutting = ' \n'.join([child_cutting,
                                        'C0 X{:.10f} Y{:.10f} Z{:.10f} (Outro)'.format(
                                            introOutro[0][int(x_index)],
                                            -surf[int(index)][0] - in_out_length,
                                            introOutro[1][int(x_index)])
                                        ])
            if debug:
                child_cutting = ' '.join([child_cutting, '{:1f}'.format(in_out_choice[1][int(x_index)])])
        elif index == profile_index[1]:
            child_cutting = ' \n'.join([child_cutting,
                                        'Y{:.10f} \nZ{:.10f} \n/M26 \nC0 X{:.10f} Y{:.10f} Z{:.10f} (Intro)'.format(
                                            -surf[int(index)][0] + in_out_length,
                                            introOutro[3][int(x_index)],
                                            introOutro[2][int(x_index)],
                                            -surf[int(index)][0] + in_out_length,
                                            introOutro[3][int(x_index)])
                                        ])
            if debug:
                child_cutting = ' '.join([child_cutting, '{:1f}'.format(in_out_choice[0][int(x_index)])])
        elif surf[int(index)][int(x_index)] != 0 and surf[int(index) + 1][int(x_index)] == 0:   # Test this elif stmt 11-5-18
            child_cutting = ' \n'.join([child_cutting,
                                        'Y{:.10f} \nZ{:.10f} \n/M26 \nC0 X{:.10f} Y{:.10f} Z{:.10f} (Intro)'.format(
                                            -surf[int(index)][0] + in_out_length,
                                            introOutro[3][int(x_index)],
                                            introOutro[2][int(x_index)],
                                            -surf[int(index)][0] + in_out_length,
                                            introOutro[3][int(x_index)])
                                        ])
            if debug:
                child_cutting = ' '.join([child_cutting, '{:1f}'.format(in_out_choice[0][int(x_index)])])

        else:
            child_cutting = ' \n'.join([child_cutting,
                                        'C0 X{:.10f} Y{:.10f} Z{:.10f}'.format(
                                            surf_slope[int(index)][int(x_index)][2],
                                            -surf[int(index - 1)][0],
                                            surf_slope[int(index)][int(x_index)][3])
                                        ])

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
        '/M29 \nZ{:.10f} \n'.format(introOutro[1][int(x_index)] + 2,)
    ])

    child_out.writelines(child_cutting)  # writing out to the file after every X saves a TON of time!!!
# print(cutting_blocks)


child_footer = '\n ( CLOSEOUT BLOCKS ) \n#506 = #506 + 1\nM99 \n'

child_text = [child_header, child_cutting, child_footer]
main_text = [header_blocks, cutting_blocks, closeout_blocks]

main_out = open(ncmainoutfile, 'w+')  # designate the output file
print("\nWriting Main File...")
main_out.writelines(main_text)
print("Done with Main File. Writing Child File...")
child_out.writelines(child_footer)
main_out.close()
child_out.close()

random.shuffle(ranFin)
print(ranFin[0])
