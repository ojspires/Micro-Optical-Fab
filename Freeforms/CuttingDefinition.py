# CuttingDefinition.py      Oliver Spires       University of Arizona       2/19/2020
# This script takes inputs which will define the cutting parameters of a Slow Slide Servo cut. At the moment, it's
# designed for a Moore Nanotech FG350. If I learn anything about other machines, I could load certain formatting or
# cutting parameters appropriate to each machine.

import logging


# Capture the cutting parameters
def cut_def():
    rotation = offset = tool_num = tool_radius = step_over = angular_sampling = step_ang = parking = mist_num = inverse_feed = total_doc = pass_doc = ''
    logging.debug('Starting cutting parameter input within module...')
    while rotation != 'CW' and rotation != 'CCW':
        rotation = input('CCW or CW cutting?:').upper()
        print(rotation)
    while offset.__len__() != 3:
        offset = input('Workpiece Offset (Options: G54 thru G59):').upper()
        print(offset)
        if offset.__len__() == 3 and offset[1:].isdecimal():
            if not (offset[0] == 'G' and 53 < int(offset[1:]) < 60):
                # print(offset)
                logging.error('Improper Workpiece offset entered. Prefix with a G and obey the range. Clearing and recapturing. Entered: ' + offset)
                offset = ''
        else:
            # print(offset)
            logging.error('Improper Workpiece offset entered. Wrong length or characters. Clearing and recapturing. Entered: ' + offset)
            offset = ''
    while tool_num.__len__() != 5:
        t_n_typed = input('Tool Number (enter 1 thru 50):')
        if t_n_typed.isdecimal():
            t_n_typed = int(t_n_typed)
            if 0 < t_n_typed < 51:
                tool_num = 'T' + 2 * ('%02d' % t_n_typed)
                print(tool_num)
            else:
                logging.error('Incorrect tool number. Clearing and recapturing. Entered: ' + str(t_n_typed))
                t_n_typed = ''
        else:
            logging.error('Invalid input. Type a tool number. Clearing and recapturing. Entered: ' + str(t_n_typed))
            t_n_typed = ''
    while tool_radius == '':
        tool_radius = input('Enter the tool radius in mm:')
        try:
            tool_radius = abs(float(tool_radius))
        except ValueError:
            logging.error('Invalid tool radius. Clearing and recapturing. Entered:' + tool_radius)
            tool_radius = ''
        # if tool_radius.isdecimal():
        #     tool_radius = abs(float(tool_radius))
        # else:
        #     if tool_radius.split('.').__len__() == 2:
        #         if tool_radius.split('.')[0].isdecimal() and tool_radius.split('.')[1].isdecimal():
        #             tool_radius = abs(float(tool_radius))
        #         else:
        #             logging.error('Invalid tool radius. Clearing and recapturing. Entered:' + tool_radius)
        #             tool_radius = ''
        #     else:
        #         logging.error('Invalid tool radius. Clearing and recapturing. Entered:' + tool_radius)
        #         tool_radius = ''
    while step_over == '':
        step_over = input('Enter the stepover distance (X travel per rotation, in mm):')
        try:
            step_over = abs(float(step_over))
            if step_over > tool_radius / 2:
                logging.error('Invalid stepover distance. Should be considerably less than the tool radius. (' + str(tool_radius) + 'mm) Clearing and recapturing. Entered: ' + str(step_over))
                step_over = ''
        except ValueError:
            logging.error('Invalid stepover distance. Clearing and recapturing. Entered: ' + step_over)
            step_over = ''
        # if step_over.isdecimal():   # TODOne: switch to try...except
        #     step_over = abs(float(step_over))
        # else:
        #     if step_over.split('.').__len__() == 2:
        #         if (step_over.split('.')[0].isdecimal() or step_over.split('.')[0] == '') and step_over.split('.')[1].isdecimal():
        #             step_over = abs(float(step_over))
        #         elif step_over[0] == '-':
        #             logging.error('Stepover can\'t be negative. Clearing and recapturing. Entered:' + step_over)
        #             step_over = ''
        #         else:
        #             logging.error('Invalid stepover distance. Clearing and recapturing. Entered:' + step_over)
        #             step_over = ''
        #     else:
        #         step_over = ''
        #         logging.error('Invalid stepover distance. Clearing and recapturing.')
    while angular_sampling == '':
        angular_sampling = input('Enter CR for Constant aRc, or CA for Constant Angle:').upper()
        if angular_sampling == 'CA':
            step_ang_string = 'Enter the angular resolution at which to sample the surface (degrees):'
        elif angular_sampling == 'CR':
            step_ang_string = 'Enter the arclength at which to sample the surface (mm):'
        else:
            logging.error('Invalid angular sampling. Clearing and recapturing. Entered:' + angular_sampling)
            angular_sampling = ''
    while step_ang == '':
        step_ang = input(step_ang_string)
        try:
            step_ang = abs(float(step_ang))
        except ValueError:
            logging.error('Invalid step angle. Clearing and recapturing. Entered: ' + step_ang)
            step_ang = ''
        # if step_ang.isdecimal():    #TODOne: Use try...float()...except
        #     step_ang = abs(float(step_ang))
        # else:
        #     if step_ang.split('.').__len__() == 2:
        #         if (step_ang.split('.')[0].isdecimal() or step_ang.split('.')[0] == '') and step_ang.split('.')[1].isdecimal():
        #             step_ang = abs(float(step_ang))
        #         elif step_ang[0] == '-':
        #             logging.error('Step angle can\'t be negative. Clearing and recapturing. Entered:' + step_ang)
        #             step_ang = ''
        #         else:
        #             logging.error('Invalid step angle. Clearing and recapturing. Entered:' + step_ang)
        #             step_ang = ''
        #     else:
        #         step_ang = ''
        #         logging.error('Invalid step angle. Clearing and recapturing.')
    while parking == '':
        parking = input('Enter the Z parking position in mm:')
        try:
            parking = float(parking)
            if not -150 < parking < 24:
                logging.error('Invalid parking position. Value should be between -150mm and +24mm. Clearing and recapturing. Entered: ' + str(parking))
                parking = ''
        except ValueError:
            logging.error('Invalid parking position. Clearing and recapturing. Entered: ' + parking)
            parking = ''
        # if parking.isdecimal() or parking.strip('-').isdecimal():
        #     parking = float(parking)
        # else:
        #     if parking.split('.').__len__() == 2:
        #         if (parking.split('.')[0].isdecimal() or parking.split('.')[0] == '') and parking.split('.')[1].isdecimal():    # TODOne: utilize ''.strip('-') to simplify here NO! Easier! :D use try...input_variable = float(input_variable)...except ValueError
        #             parking = float(parking)
        #         elif parking[0] == '-':
        #             if (parking.split('-')[1].split('.')[0].isdecimal() or parking.split('-')[1].split('.')[0] == '') and parking.split('-')[1].split('.')[1].isdecimal():    # TODOne: utilize ''.strip('-') to simplify here
        #                 parking = float(parking)
        #             else:
        #                 logging.error('Invalid parking position. Clearing and recapturing. Entered: ' + parking)
        #                 parking = ''
        #         else:
        #             logging.error('Invalid parking position. Clearing and recapturing. Entered: ' + parking)
        #             parking = ''
        #     else:
        #         logging.error('Invalid parking position. Clearing and recapturing. Entered: ' + parking)
        #         parking = ''
        # if parking != '':
        #     if parking < -150 or parking > 24:
        #         logging.error('Invalid parking position. Value should be between -150mm and +24mm. Clearing and recapturing. Entered:' + str(parking))
        #         parking = ''
    while mist_num == '':
        mist_num = input('Enter the mist number (1 or 2):')
        if mist_num == '1':
            mist_num = '26'
        elif mist_num == '2':
            mist_num = '27'
        else:
            logging.error('Invalid mist number. Refer to the mist buttons on the 350FG Pendant. Entered: ' + mist_num)
            mist_num = ''
    while total_doc == '':
        total_doc = input('Enter the total depth to cut, in mm (see Edge Sag):')
        try:
            total_doc = abs(float(total_doc))
        except ValueError:
            logging.error('Invalid total depth of cut. Value should be a positive float. Clearing and recapturing. Entered: ' + str(total_doc))
            total_doc = ''
    while pass_doc == '':
        pass_doc = input('Enter the depth of cut per pass, in mm:')
        try:
            pass_doc = abs(float(pass_doc))
            if pass_doc > tool_radius / 2:
                logging.error('Invalid per-pass depth of cut. Value should be less than half the tool radius, and much less than that for metals. Clearing and recapturing. Entered: ' + str(pass_doc))
                pass_doc = ''
        except ValueError:
            logging.error('Invalid per-pass depth of cut. Value should be a positive float. Clearing and recapturing. Entered: ' + str(pass_doc))
            pass_doc = ''
    while inverse_feed == '':
        inverse_feed = input('Enter the inverse feedrate (seconds per line)(a good start is to set it equal to the arclength)')
        try:
            inverse_feed = abs(float(inverse_feed)).__round__(3)
        except ValueError:
            logging.error('Invalid inverse feed. Value should be a positive float. Clearing and recapturing. Entered: ' + str(inverse_feed))
            inverse_feed = ''
    logging.debug('Finished collecting cutting parameters. Returning them to user or to the calling program...')
    return rotation, offset, tool_num, tool_radius, step_over, angular_sampling, step_ang, parking, mist_num, inverse_feed, total_doc, pass_doc


if __name__ == '__main__':
    a = cut_def()
    print(a)
