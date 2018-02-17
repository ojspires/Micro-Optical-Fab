# SSSflatSpeeder.py	1.0.0
# Oliver Spires		University of Arizona Micro-Optical Fabrication Facility	2/16/2018
# This script performs post-processing on *.nc files produced by NanoCAM 3D V 2.7.58.00
# Features (1.0):
# - Deletes most of the points in the outer radial coordinates of a part. This will greatly speed up the fabrication of freeforms that are surrounded by a flat.


# Setup

# reset -f      # doesn't work outside of Jupyter Notebook
# import tkinter
from tkinter import filedialog
import shutil
prevline = ''
ncfcfilename = ''
direction = ''


# Import the file

ncmainfilename = filedialog.askopenfilename(initialdir="D://UofA Part Programs/", title="Select Main NC file", filetypes=(("G-code Files", "*.nc"), ("G-code Files (Backup)", "*.nc.bak"), ("all files", "*.*")))


# Scan the Main file to find the Child file(s)
mnfile = open(ncmainfilename)
for line in mnfile:          # Look for the child script
    # print(line)
    if line.startswith("M98"):
        line = line[4:]                     # Strip "M98(" from the filename
        ncfcfilename = line.split(")")[0]   # and the ")" from the end of it
        break
ncpath = ncmainfilename.split("/")[0:-1]    # Take the path from the Main NC file
ncpath = '/'.join(ncpath)                   # Rejoin it into a single string
ncfcfilename = ncpath + "/" + ncfcfilename  # Append the Child script filename
mnfile.close()




# Back up the original files

# shutil.move(ncmainfilename, ncmainfilename + ".original")
shutil.move(ncfcfilename, ncfcfilename + ".original")


# Scan and modify the Child file

ncfcinfile = open(ncfcfilename + ".original", 'r')
ncfcoutfile = open(ncfcfilename, 'a+')
flat_segment = True
for line in ncfcinfile:
    if flat_segment and line.startswith("C"):
        c_coord = float(line.split('C')[1].split(' ')[0])
        z_coord = float(line.split('Z')[1].split('\n')[0])
        if c_coord % 5 != 0:
            if z_coord != 0:
                flat_segment = False
            else:
                line = ''

    ncfcoutfile.write(line)                    # Write the modified or initial code to the outfile
ncfcinfile.close()
ncfcoutfile.close()


