#!C:\Program Files\Python36\python.exe
# DiamAlign.py   Oliver Spires      10/18/2019
# This file accepts input of data about alignment metrology, and provides a prescription for machine adjustments. The
# intended machine for this script to be use with is the Moore Nanotech 350FG, with default axis orientations.

from tkinter import *
from Alignment._AlignCalc import align_calc

# Test Section: GUI

fields = 'Designed Radius of Curvature (mm)', 'Measured Radius of Curvature (mm)', 'Designed Part Diameter (mm)', \
         'Measured Part Diameter (mm)', 'Ogive Fringe Count', 'Center Pip Diameter (um)', 'Profile PV (um)', \
         'Tool Radius (mm)'
# selectors = 'Tool Flat Side', 'Mist Number', 'C Offset', 'G54 Offset'
selections = (('Part Rotation', ('CW', 'CCW')),
              ('Part Shape', ('Convex |)', 'Concave |(')),
              ('Machining Type', ('Cutting', 'Grinding')),
              ('Fringe Movement', ('Inward as Part -> Interferometer', 'Outward as Part -> Interferometer')),
              ('Center Pip Shape', ('Cylinder []', 'Cone /\\')),
              ('Profile Shape', ('M', 'W')))
outputs = 'X Adjust by: (mm)', 'Y Adjust by: (mm)', 'Z Adjust by: (mm)', \
          'Tool Adjust by: (mm)', 'Max f/# to use:', 'Part f/#:'

part_radius = 153
part_radius_meas = 153
part_diam = 51
part_diam_meas = 50.8
part_cx = False
cut_cw = False
cutting = True
ogive = 0
fringe_in = True
center_cyl = True
center_diam = 0
profile_m = True
profile_pv = .147
tool_radius = 1.892147



root = Tk()
root.title("Select options and close")

# Add a grid
mainframe = Frame(root)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)
mainframe.pack(pady=10, padx=10)
col_num = 0
variables_gui = []

for name, options in selections:
    # Create a Tkinter variable
    tkvar = StringVar(root)

    # Dictionary with options
    tkvar.set(options[0])  # set the default option

    popupMenu = OptionMenu(mainframe, tkvar, *options)
    Label(mainframe, text=name).grid(row=1, column=col_num)
    popupMenu.grid(row=2, column=col_num)
    col_num += 1
    variables_gui.append(tkvar)
row_num = 3
fields_gui = []
for field in fields:
    # print(field)
    entry_label = Label(mainframe, text=field).grid(row=row_num, column=0)
    entry = Entry(mainframe)
    entry.grid(row=row_num, column=2)
    fields_gui.append((field, entry))
    row_num += 1

# on change dropdown value
def change_dropdown():
    for tkvar_inner in variables_gui:
        print(tkvar_inner.get())


def fetch(fields_func):
    global all_fields
    all_fields = []
    for fetch_entry in fields_func:
        fetch_field = fetch_entry[0]
        text = fetch_entry[1].get()
        print('%s: "%s"' % (fetch_field, text))
        all_fields.append(text)
    part_rad = float(all_fields[0])
    meas_rad = float(all_fields[1])
    part_diam = float(all_fields[2])
    meas_diam = float(all_fields[3])
    ogive = float(all_fields[4])
    pip_diam = float(all_fields[5])
    shape_pv = float(all_fields[6])
    tool_rad = float(all_fields[7])
    if variables_gui[0].get() == 'CW':
        part_cw = True
    else:
        part_cw = False
    if variables_gui[1].get() == 'Convex |)':
        convex = True
    else:
        convex = False
    if variables_gui[2].get() == 'Cutting':
        cutting = True
    else:
        cutting = False
    if variables_gui[3].get() == 'Inward as Part -> Interferometer':
        fringes_in = True
    else:
        fringes_in = False
    if variables_gui[4].get() == 'Cylinder []':
        cylinder = True
    else:
        cylinder = False
    if variables_gui[5].get() == 'M':
        m_profile = True
    else:
        m_profile = False
    calculated_values = align_calc(part_rad, meas_rad, part_diam, meas_diam, convex, part_cw, cutting, ogive,
                                   fringes_in, cylinder, pip_diam, m_profile, shape_pv, tool_rad)
    print(calculated_values)
    row_num = 4
    row = 0
    for output in outputs:
        output_label = Label(mainframe, text=output).grid(row=row_num, column=3)
        clear_window = Label(mainframe, text='            ').grid(row=row_num, column=4)
        output_data = Label(mainframe, text=calculated_values[row]).grid(row=row_num, column=4)
        row_num += 1
        row += 1

# link function to change dropdown
# tkvar.trace('w', change_dropdown)
for tkvar in variables_gui:
    tkvar.trace('w', change_dropdown)
root.bind('<Return>', (lambda event, e=fields_gui: fetch(e)))
b1 = Button(root, text='Enter',
            command=(lambda e=fields_gui: fetch(e)))
b1.pack(side=LEFT, padx=5, pady=5)
b2 = Button(root, text='Quit', command=root.quit)
b2.pack(side=LEFT, padx=5, pady=5)

root.mainloop()

# convert the variables that came from the GUI
if all_fields == [] or "" in all_fields:
    print('Input error: data missing. Re-run program.')
    root.quit()
    root.withdraw()
    valid_data = False
else:
    print('Input successful')
    # a = 0
    # for title in fields:
    #     print('%s: "%s"' % (title, all_fields[a]))
    #     a += 1
    # b = 0
    # for tkvar in variables_gui:
    #     print(selections[b][0], ': ', tkvar.get())
    #     b += 1
    root.withdraw()
    valid_data = True

