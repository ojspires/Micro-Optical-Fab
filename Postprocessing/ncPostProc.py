# ncPostProc.py	1.1.1
# Oliver Spires		University of Arizona Micro-Optical Fabrication Facility	11/2/2017
# This script performs post-processing on *.nc files produced by NanoCAM 2D V 1.52.00.
# Features (1.0):
# - Cylinder-cutting script (rotation sense aware)
# - Variablize Parking Position
# - Back up initial files
# - Conservation of coolant
# - Save translation time when starting/ending the main script
# - GUI file dialog
# Features (1.1):
# - Disabled the %reset function which doesn't work outside of jupyter
# - Initialized prevline variable
# - Initial directory updated for actual usage
# Features (1.1.1, 1/30/2018):
# - Corrected some style issues
# - Gathered the initial variable declarations
# - TODO: make the nozzle a variable which can be set from the main file
# - TODO: shorten the spray nozzle time (speed up the between-passes translation time)
# - TODO: make the offset slot a variable
# - TODO: tie the offset slot variable to filename (this is an iffy proposal)
# - TODO: provide a dialog box with radio buttons to select the offset slot (this might be a better option)
# Features (1.1.2, 2/5/2018):
# - made the offset slot a variable


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
ncpath = ncmainfilename.split("/")[0:-1]    # Take the path from the Main NC file
ncpath = '/'.join(ncpath)                   # Rejoin it into a single string
ncfcfilename = ncpath + "/" + ncfcfilename  # Append the Child script filename
mnfile.close()


# Scan the Child file to determine spindle direction

for line in open(ncfcfilename):
    if line == 'M03S[#504]\n':
        direction = ''  # CW
        break
    elif line == 'M04S[#504]\n':
        direction = '-'  # CCW
        break
# print(direction)


# Back up the original files

shutil.move(ncmainfilename, ncmainfilename + ".original")
shutil.move(ncfcfilename, ncfcfilename + ".original")


# Scan and modify the Child file

ncfcinfile = open(ncfcfilename + ".original", 'r')
ncfcoutfile = open(ncfcfilename, 'a+')
for line in ncfcinfile:
    if "CYLINDER" in ncfcfilename.upper():     # If cyl path, decrement the offset each loop iteration
        if line.startswith("G52 Z"):           # Insert this decrement code
            line = line.replace("G52 Z", "#545 = #545 - " + direction + "#502                       ( Subtracts depth of cut from offset variable )\nG52 X[#545]Z")
        elif line.startswith("Z") and prevline == "G04P.1\n":
            line = "M29\n"                     # Replace the slow Z offset with a nozzle shutoff in a cyl file
    elif prevline == "G04P.1\n":
        line = line + "M29\n"                  # Shut off the nozzle before the X translation (saves coolant)
    prevline = line
    ncfcoutfile.write(line)                    # Write the modified or initial code to the outfile
ncfcinfile.close()
ncfcoutfile.close()


# Scan and modify the Main file

ncmaininfile = open(ncmainfilename+".original", 'r')
ncmainoutfile = open(ncmainfilename, 'a+')
for line in ncmaininfile:
    if "CYLINDER" in ncmainfilename.upper():  # If cyl path, set the initial offset
        if line == "#506 = 0                                 ( LOOP COUNT )\n":
            line = line + "#545 = " + direction + "[#542]*[#541]                     ( X cut offset var )\n"
    if line.startswith("#547"):               # The script won't take as long if we don't have to translate all the way to zmax. Make variable the offset; this can later be tied to filename or tool # or something
        line = "#546 = -150.0                            ( Set Parking Position )\n#548 = 54                                ( Set offset number. Acceptable = 54 to 59 )\n" + line
    elif "PARKING POSITION" in line:          # Make the parking position a variable
        line = line.replace(" Z0.0 F200   ", " Z[#546] F200")
    elif "SET Y AXIS TO ZERO" in line:        # The script won't take as long if we don't have to translate to ymax
        line = line.replace("Y0.0", "Y-95")
    elif line.startswith("G71"):
        line = line.replace("G54", "G[#548]")
    ncmainoutfile.write(line)                 # Write the initial or modified lines to the output file
ncmaininfile.close() 
ncmainoutfile.close()
