# PartContact.py    Oliver Spires   2/5/2020    University of Arizona
# Refs.:    http://math.stmarys-ca.edu/wp-content/uploads/2017/07/Kelly-Lynch.pdf

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

# Import:
import progressbar
import numpy
import tkinter
from tkinter import filedialog
import sys
from Freeforms.FreeformDefinition import define_freeform
from Freeforms.CuttingDefinition import cut_def
import logging
import time
import getpass

# Initialize:
outputFile = ''  # TODO: this can prob be deleted, i'm using mainfilename
introString = outroString = mainfilename = loopVariables = ''
errorWidth = maxSlope = 0
toolRadiusSearchMargin = 1.5
logger = logging.getLogger(__name__)
twoFeatures = planeFound = multiPass = False
machineName = 'Moore Nanotech 350FG'

# Setup:
logging.basicConfig(filename='Freeform Cutting Log.txt', filemode='w')
logger.setLevel('DEBUG')    # 'INFO' 'DEBUG' 'WARNING' 'ERROR'
logger.debug('Gathering features and arrays.')
arrayParameters = (features, arrays, all_array_coords) = define_freeform([], True)
logger.debug('Gathered. Gathering cutting parameters.')
cutParameters = (rotation, offset, tool_num, tool_radius, step_over, angular_sampling, step_ang, parking, mist_num, inverse_feed, total_doc, pass_doc) = cut_def()
mainfilename = tkinter.filedialog.asksaveasfilename(initialdir="G:\\My Drive\\Work", title="Select Output Location & Filename:", filetypes=[("G-code Files", ".nc")])
mainfilename = mainfilename.split('.nc')[0] + '.nc'
semifilename = mainfilename.split('.nc')[0] + '_SF.nc'
finishfilename = mainfilename.split('.nc')[0] + '_FC.nc'
logging.debug('Gathered. Took filenames to potentially save to.')
if total_doc > pass_doc:
    multiPass = True
    loops = int(numpy.ceil(total_doc / pass_doc))
    loopVariables = '#599 = ' + loops + '     ( Finish Cut Loops ) \n#589 = 0     ( Reinitialize Loop Counter ) \n'  # TODO: Enable semifinish cuts
logging.info(('Filename & Directory: ' + mainfilename))
logging.debug(('Feature Parameters: ' + str(arrayParameters)))
logging.debug(('Cutting Parameters: ' + str(cutParameters)))

for feature in features:
    if 'plane' in feature:
        logging.debug(('Plane diameter: ' + str(feature[1]) + '. This will be used to find the initial X position.'))
        planeFound = True
        cutDiameter = feature[1]
        edgeSag = feature[2]
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
    logging.error('No planes found. Program has no starting point. Re-enter surface data, including a plane to define the diameter.')
    try:
        print(initialX)
    except ValueError:
        raise ValueError('No overall part diameter specified.')

# File Header
headerText = '(((          ' + mainfilename + '          )))\n( Generated ' + str(time.asctime()) + ' by ' + getpass.getuser() + ' for ' + machineName + '. )\n( Features: ' + str(features) + ' )\n( Arrays: ' + str(arrays) + \
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
             str(initialX) + '                  ( Fast move to initial X position )\nZ' + str(edgeSag + 2) + '    ( Fast move to 2mm above the part )\n'
logging.debug('Display the prepared header data:\n' + headerText + variablesText + leadInOutText + leadInText)
