# XZCoordFromNC.py
# Oliver Spires          University of Arizona      12/12/2017
# This script takes the XZ coordinates from an .nc file generated
# by NanoCAM 2D, and returns the coordinates in a tuple made up of
# an x list and a z list. It also generates an output .csv. When
# run as a standalone program, instead of as a module, it also has
# UI elements for opening the file and reporting the output location.
# 3/26/2018: Fixed some PEP8 formatting errors. Removed the file path code from the __main__ section (it's still in the
#   function, and wasn't called in the __main__ part of the code). Renamed XZtoNC to x_z_to_n_c to follow convention.
#   Renamed function input variable to prevent confusion with the function call.

# Setup


def x_z_to_nc(n_c_main_filename: str):
    """
    :type n_c_main_filename: str


    """
    import re

    ncfcfilename = ''
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

    p = re.compile('X-?\d+\.\d+\s?Z-?\d+\.\d+')  # Build the search string for the coordinates lines,
    q = re.compile('X-?\d+\.\d+')  # for the X coordinates,
    r = re.compile('Z-?\d+\.\d+')  # for the Z coordinates

    # Scan and modify the Child file
    ncinfile = open(ncfcfilename, 'r')  # Read from the input file
    ncoutfile = open(ncfcfilename + ".coords.csv", 'a+')  # designate the output file
    xes = []
    zes = []
    for line in ncinfile:
        matches = p.match(line)  # Search for coordinates lines
        if matches is not None:
            xpos = float((q.findall(matches[0]))[0][1:])  # Read the initial x coordinate of this line as a number
            #        print(xpos)
            zpos = float((r.findall(matches[0]))[0][1:])  # Read the initial x coordinate of this line as a number
            line = str(xpos) + ',' + str(zpos) + '\n'  # Put a newline on the end of the modified string
            print(line)
            xes.append(xpos)
            zes.append(zpos)
        ncoutfile.write(line)  # Write the modified or initial code to the outfile
    ncinfile.close()  # Release both files
    ncoutfile.close()
    coords = [xes, zes]
    return coords


if __name__ == "__main__":
    import tkinter
    from tkinter import filedialog

    # Import the file
    root = tkinter.Tk()
    ncmainfilename = filedialog.askopenfilename(initialdir="/", title="Select Main NC file", filetypes=(
        ("G-code Files", "*.nc"), ("G-code Files (Backup)", "*.nc.bak"), ("all files", "*.*")))

    x_z_to_nc(ncmainfilename)

    # Provide an output file message
    def close_outstring():
        root.withdraw()
        root.destroy()


    OutString = "The output file is a .csv file, in \n" + ncpath + "\n"
    w = tkinter.Label(root, text=OutString)
    w.pack()
    button = tkinter.Button(root, text='OK', width=25, command=close_outstring)
    button.pack()
    root.mainloop()
