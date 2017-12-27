# GratingFormatter.py   Oliver Spires   12/12/17
# This program takes a grating profile from NanoCAM, and generates GCODE to cut a straight-line square grating which
# follows that profile.

import numpy as np
import tkinter
from tkinter import filedialog
import matplotlib.pyplot as plt
from datetime import datetime as dt
import csv
import copy

now = dt.now()

# Set up variables, in mm
cut_spacing = .0015
grating_DoC = .001
tangent_arc_radius = 60
half_diameter = 5
feed_rate = 2000
tool_radius = 1.004


def radius_calc(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> list:
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
    print(surf[0][0:10])
angular_resolution = surf[0][2] - surf[0][1]
surf_slope = copy.deepcopy(surf)
surf_radius_index = np.linspace(0, np.size(surf, 0) - 1, np.size(surf, 0))
surf_angle_index = np.linspace(0, np.size(surf, 1) - 1, np.size(surf, 1))
for r_index in surf_radius_index[1:]:
    # print((r_index))
    # print(surf_slope[int(r_index)][1])
    local_x = float(np.radians(angular_resolution) * surf[int(r_index)][0])
    local_slope = (surf[int(r_index)][2] - surf[int(r_index)][-1]) / (2 * local_x)
    local_radius = list(radius_calc(-local_x, surf[int(r_index)][-1], 0, surf[int(r_index)][1], local_x, surf[int(r_index)][2]))
    if local_radius[0] != 'inf':
        if local_radius[1] < surf[int(r_index)][1]:
            local_radius[0] = 'inf'
        else:
            minimum_radius = np.min((local_radius[0], minimum_radius))
    (local_x_offset, local_y_offset) = tool_offset_calc(local_slope, tool_radius)
    # print(local_x_offset)
    # print(local_y_offset)
    surf_slope[int(r_index)][1] = [local_slope, local_radius[0], local_x_offset, local_y_offset]
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
    surf_slope[int(r_index)][-1] = [local_slope, local_radius[0], local_x_offset, local_y_offset]
    for a_index in surf_angle_index[2:-2]:
        # print(surf[0][int(a_index)])
        local_slope = (surf[int(r_index)][int(a_index) + 1] - surf[int(r_index)][int(a_index) - 1]) / (2 * local_x)
        local_radius = list(radius_calc(-local_x, surf[int(r_index)][int(a_index) - 1], 0, surf[int(r_index)][int(a_index)], local_x, surf[int(r_index)][int(a_index) + 1]))
        if local_radius[0] != 'inf':
            if local_radius[1] < surf[int(r_index)][1]:
                local_radius[0] = 'inf'
            else:
                minimum_radius = np.min((local_radius[0], minimum_radius))
        (local_x_offset, local_y_offset) = tool_offset_calc(local_slope, tool_radius)
        surf_slope[int(r_index)][int(a_index)] = [local_slope, local_radius[0], local_x_offset, local_y_offset]
root.destroy()

# For calculation of whether the tool will clear or not: compare required X offset for coordinate (based on local slope)
# to arclength and neighboring X offsets

print(minimum_radius)

# Surface finish estimation
outerEdgeRadius = surf[-1][0]
innerEdgeRadius = surf[1][0]
outerEdgeArc = np.deg2rad(angular_resolution) * outerEdgeRadius
innerEdgeArc = np.deg2rad(angular_resolution) * innerEdgeRadius
inE = innerEdgeArc / 2
outE = outerEdgeArc / 2

innerEdgeSurfaceFinish = np.sqrt((1 / innerEdgeArc) * np.square(tool_radius) * ((-inE * np.sqrt(1 - (np.square(inE) / np.square(tool_radius))) + tool_radius * np.arcsin(-inE / tool_radius)) - (inE * np.sqrt(1 - (np.square(inE) / np.square(tool_radius))) + tool_radius * np.arcsin(inE / tool_radius)) + (inE - np.power(inE, 3)/(3 * np.square(tool_radius))) - (-inE - np.power(-inE, 3)/(3 * np.square(tool_radius))) + 2 * inE))
outerEdgeSurfaceFinish = np.sqrt((1 / outerEdgeArc) * np.square(tool_radius) * ((-outE * np.sqrt(1 - (np.square(outE) / np.square(tool_radius))) + tool_radius * np.arcsin(-outE / tool_radius)) - (outE * np.sqrt(1 - (np.square(outE) / np.square(tool_radius))) + tool_radius * np.arcsin(outE / tool_radius)) + (outE - np.power(outE, 3)/(3 * np.square(tool_radius))) - (-outE - np.power(-outE, 3)/(3 * np.square(tool_radius))) + 2 * outE))
print('Predicted inner surface finish: ', innerEdgeSurfaceFinish * 10**6, 'nmRMS')
print('Predicted outer surface finish: ', outerEdgeSurfaceFinish * 10**6, 'nmRMS')

# TODO:     * resample for higher angular resolution if finish too high
#           * push toolpath over to fit in valley if tool_radius > minimum_radius

