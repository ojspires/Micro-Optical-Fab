# ncPostProc.py	1.2.2
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
# - TODOne: make the nozzle a variable which can be set from the main file
# - TODO: further shorten the spray nozzle time (speed up the between-passes translation time)
# - TODOne: make the offset slot a variable
# - TODO: tie the offset slot variable to filename (this is an iffy proposal)
# - TODO: provide a dialog box with radio buttons to select the offset slot (this might be a better option)
# Features (1.1.2, 2/5/2018):
# - made the offset slot a variable
# - TODOne: collect multiple child filenames and process all of them
# - TODOne: Change YZ parking positions to work with B-Axis geometry
# - TODOne: Zero B after the Tool Offset (e.g. T0101) line
# - TODO: Make separate script to convert existing .nc files to be compatible with B-axis
# Features (1.2, 4/12/2018):
# - Move to B = 0 after tool offset selection
# - Adjusted YZ parking positions to be compatible with B-Axis
# - Created looping function, to cycle through all available child files
# - put the nozzle code in a variable, to allow changing it from the Main file
# - Enabled M26.x mist codes (M26.1 = M26, M26.2 = M27)
# Features (1.2.1, 4/13/2018):
# - Repaired the offset slot variable
# Features (1.2.2, 4/18/2018):
# - Changed the mechanism for finding where to put the B0 line (finding the tool offset activation line)
# - Changed the if statement for placing the parking position and mist variables' definition lines, to avoid duplicate declarations
# - Removed the variable from the G54-G59 offsets; variables don't work in this G code
# - Gathered some more of the variable declarations and gathered the if statements for the child file(s)
# - TODO: Make this compatible with already-postprocessed files from previous versions of this script

# Setup
from tkinter import filedialog
import shutil
import re

# Initialize variables

prevline = ''
ncfcfilename = ''
direction = ''
mist_updated = False
mist_num = [26, 26, 26]
nc_child_filenames = ['', '', '']
nc_child_filepaths = ['', '', '']
mist_search = re.compile('M2[678][.]?\d?\d?')
offset_search = re.compile('G5[4-9]')
rc_subroutine = sf_subroutine = fc_subroutine = False
child_index = -1
b_axis_installed = True
nc_child_index = 0
mist_var = 563

if b_axis_installed:
    y_parking_position = str(-15)
    z_parking_position = str(-50)
else:
    y_parking_position = str(-95)
    z_parking_position = str(-150)

# Import the file

ncmainfilename = filedialog.askopenfilename(initialdir="D://UofA Part Programs/", title="Select Main NC file", filetypes=(("G-code Files", "*.nc"), ("G-code Files (Backup)", "*.nc.bak"), ("all files", "*.*")))


# Scan the Main file to find the Child file(s)

mnfile = open(ncmainfilename)
for line in mnfile:          # Look for the child script
    # print(line)
    if 'SUBROUTINE CALL' in line:
        if 'ROUGH' in line:
            nc_child_index = 0
        elif 'SEMI-FINISH' in line:
            nc_child_index = 1
        elif 'CALL FINISH' in line:
            nc_child_index = 2
    if line.startswith("M98"):
        line = line[4:]                             # Strip "M98(" from the filename
        ncfcfilename = line.split(")")[0]           # and the ")" from the end of it
        ncpath = ncmainfilename.split("/")[0:-1]    # Take the path from the Main NC file
        ncpath = '/'.join(ncpath)                   # Rejoin it into a single string
        ncfcfilename = ncpath + "/" + ncfcfilename  # Append the Child script filename
        nc_child_filepaths[nc_child_index] = ncfcfilename
mnfile.close()
shutil.move(ncmainfilename, ncmainfilename + ".original")


for child in nc_child_filepaths:
    print(child)
    mist_one = mist_two = mist_all = False
    child_index += 1
    if child is not '':

        # Scan the Child file to determine spindle direction and mist code
        for line in open(child):
            if line == 'M03S[#504]\n':
                direction = ''  # CW
                # break     # This was used prior to adding mist code to this section, in order to save time. But now I want to make sure to catch both mist lines, where two might exist, so i'm omitting the break statement
            elif line == 'M04S[#504]\n':
                direction = '-'  # CCW
                # break

            # Search for the mist numbers in the child file
            if line == 'M26\n' or line == 'M26 \n' or 'M26.1' in line:
                mist_one = True
            elif 'M27' in line or 'M26.2' in line:
                mist_two = True

            if (mist_one and mist_two) or 'M28' in line:
                mist_all = True
                break   # Here's a time-reducing compromise (ref. comment beside commented-out break lines above in this section: The mist lines exist after the spindle on lines, so doing a break when both M26 and M27 are active exits the for loop if both of them are turned on.

        if mist_one:
            mist_num[child_index] = 26
        if mist_two:
            mist_num[child_index] = 27
        if mist_all:
            mist_num[child_index] = 28
        # print(mist_num)

        # Modify the child file(s)

        # Back up the original files
        shutil.move(child, child + ".original")

        # Scan and modify the Child file
        mist_updated = False
        ncfcinfile = open(child + ".original", 'r')
        ncfcoutfile = open(child, 'a+')
        for line in ncfcinfile:
            if "CYLINDER" in child.upper():     # If cyl path, decrement the offset each loop iteration
                if line.startswith("G52 Z"):           # Insert this decrement code
                    line = line.replace("G52 Z", "#545 = #545 - " + direction + "#502                       ( Subtracts depth of cut from offset variable )\nG52 X[#545]Z")
                elif line.startswith("Z") and prevline == "G04P.1\n":
                    line = "M29\n"                     # Replace the slow Z offset with a nozzle shutoff in a cyl file
            elif prevline == "G04P.1\n":
                line = line + "M29\n"                  # Shut off the nozzle before the X translation (saves coolant)
            try:
                mist_found = mist_search.findall(line)[0][1:]
                if mist_updated:
                    line = "( Mist Line consolidated )"
                else:
                    line = line.replace(mist_found, "[#560]")
                    mist_updated = True
            except IndexError:
                # print("no mist found \n")
                pass

            prevline = line
            ncfcoutfile.write(line)                    # Write the modified or initial code to the outfile
        ncfcinfile.close()
        ncfcoutfile.close()


# Scan and modify the Main file

ncmaininfile = open(ncmainfilename+".original", 'r')
ncmainoutfile = open(ncmainfilename, 'a+')
for line in ncmaininfile:

    # Set the X offset for cylinder cutting files
    if "CYLINDER" in ncmainfilename.upper():  # If cyl path, set the initial offset
        if line == "#506 = 0                                 ( LOOP COUNT )\n":
            line = line + "#545 = " + direction + "[#542]*[#541]                     ( X cut offset var )\n"

    # Do the replacements
    if "SECTION COMMANDS" in line:               # The script won't take as long if we don't have to translate all the way to z = 0. Make variable the offset; this can later be tied to filename or tool # or something

        line = "#546 = " + z_parking_position + "                                ( Set Parking Position )\n#563 = " + \
            str(mist_num[2]) + \
            "                                ( Set mist number for FC. Acceptable = 26 to 28 ) \n" + line
        # Removed:      \n#548 = 54                                ( Set offset number.      Acceptable = 54 to 59 )    Variables don't work in G commands (at least not in this one)
    elif line.startswith("#524"):
        line = line + "#561 = " + \
            str(mist_num[0]) + \
            "                                ( Set mist number for RC. Acceptable = 26 to 28 ) \n"
    elif line.startswith("#534"):
        line = line + "#562 = " + \
            str(mist_num[1]) + \
            "                                ( Set mist number for RC. Acceptable = 26 to 28 ) \n"
    elif "PARKING POSITION" in line:          # Make the parking position a variable
        line = line.replace(" Z0.0 F200   ", " Z[#546] F200")
    elif "SET Y AXIS TO ZERO" in line:        # The script won't take as long if we don't have to translate to ymax
        line = line.replace("Y0.0", "Y" + y_parking_position)
    # elif line.startswith("G71"):
    #     line = line.replace(offset_search.findall(line)[0], "G[#548]")
    elif "( ACTIVATE TOOL OFFSET" in line:
        line = line + "B0 \n"
    elif line.startswith("#504"):
        if rc_subroutine:
            mist_var = 561
        elif sf_subroutine:
            mist_var = 562
        elif fc_subroutine:
            mist_var = 563
        line = line + "#560 = #" + str(mist_var) + "                              ( Set the mist number for this cycle ) \n"

    # Check which Subroutine Call section we might be in
    if "CALL ROUGH" in line:
        rc_subroutine = True
        sf_subroutine = fc_subroutine = False
    elif "CALL SEMI" in line:
        sf_subroutine = True
        rc_subroutine = fc_subroutine = False
    elif "CALL FINISH" in line:
        fc_subroutine = True
        rc_subroutine = sf_subroutine = False

    ncmainoutfile.write(line)                 # Write the initial or modified lines to the output file
ncmaininfile.close() 
ncmainoutfile.close()
