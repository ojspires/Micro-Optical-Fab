# dt_nc_Viewer.py   Oliver Spires   03/27/2018
# This script plots an XYZC toolpath.
# TODO: consider doing 3D visualization of 2D toolpath (including the spiral based on RPM and feedrate
# TODO: illustrate tool shape
# TODO: animate tool along path
# TODO: make this file XZ coordinate-capable ( and delete the comment in the "Data import" code section )


# Import Modules
# %matplotlib
# This only works in Jupyter Notebook, for inline plotting (if you use the argument inline after it; in a separate window otherwise.)
from tkinter import filedialog
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D     # this IS used, for the 3d projection option on plt.axes() in the "Set up the plot" section of this file
import numpy as np
import re
import copy


# Import the file
prevline = ''
ncfcfilename = ''
n_c_main_filename = filedialog.askopenfilename(initialdir="G://My Drive/Work/", title="Select Main NC file", filetypes=(("G-code Files", "*.nc"), ("G-code Files (Backup)", "*.nc.bak"), ("all files", "*.*")))


# Scan the Main file to find the Child file(s)
mnfile = open(n_c_main_filename)
for line in mnfile:  # Look for the child script
    #    print(line)
    if line.startswith("M98"):
        line = line[4:]  # Strip "M98(" from the filename
        ncfcfilename = line.split(")")[0]  # and the ")" from the end of it
if ncfcfilename == '':
    ncfcfilename = n_c_main_filename

nc_path_segments = n_c_main_filename.split("/")[0:-1]  # Take the path from the Main NC file
nc_path = '/'.join(nc_path_segments)  # Rejoin it into a single string

ncfcfilename = nc_path + "/" + ncfcfilename  # Append the Child script filename

mnfile.close()


# Import the data
p = re.compile('[CXYZ][-.]?\d')
index = 0
path = []
fcfile = open(ncfcfilename)
for line in fcfile:
    if p.match(line):
        # print(line.split(' '))
        if np.size(line.split(' ')) > 2:
            # print(np.size(line.split(' ')))
            path.append((line.split(' ')[0:4]))     # this won't work for XZ coordinate file inputs
            for i in range(len(path[index])):
                path[index][i] = float(path[index][i][1:])
        elif np.size(line.split(' ')) == 2:
            path.append(copy.deepcopy(path[index - 1]))
            slot = 5    # force an error if one of the coordinate axes (XYZC) isn't matched
            if line[0] == 'C':
                slot = 0
            elif line[0] == 'X':
                slot = 1
            elif line[0] == 'Y':
                slot = 2
            elif line[0] == 'Z':
                slot = 3
            path[index][slot] = float(line.split(' ')[0][1:])
        # print(path[index])
        index += 1

fcfile.close()


# Convert the data
pathX = []
pathY = []
pathZ = []
for i in range(len(path)):
    pathX.append(path[i][1]*np.cos(np.radians(path[i][0])) - path[i][2]*np.sin(np.radians(path[i][0])))
    pathY.append(path[i][2]*np.cos(np.radians(path[i][0])) + path[i][1]*np.sin(np.radians(path[i][0])))
    pathZ.append(path[i][3])


# Set up the plot
fig = plt.figure()
ax = plt.axes(projection='3d')
ax.plot(pathX, pathY, pathZ)
plt.show(block=True)
