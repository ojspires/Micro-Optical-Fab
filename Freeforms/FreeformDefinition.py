# FreeformDefinition.py     Oliver Spires   University of Arizona   1/31/2020
# This program takes user input from either the console or input arguments and builds feature definitions and arrays.
# Refs.:
#   2nd order (or first) derivative of aspheric equation:
#       https://www.wolframalpha.com/input/?i=second+derivative+of+%28cx%5E2%2F%281%2Bsqrt%281-nx%5E2%29%29+%2B+ax+%2B+bx%5E2+%2B+cx%5E3+%2Bdx%5E4%29
#   Aspheric Equation:
#       https://www.edmundoptics.com/knowledge-center/application-notes/optics/all-about-aspheric-lenses/
# TODO: use while loops and try...except ValueError to verify each input
#   2-19-20: this task in work. Done up to start of array definition.
# TODO: place array(Y/N) question before center coord question in feature input section; if array, don't ask about center. Centers will be defined by array.
# TODO: only allow one plane in the features list

import numpy as np
import logging


def check_cartesian_input(ex_why: str):
    try:
        ex_why = [float(ex_why.split(',')[0]), float(ex_why.split(',')[1])]
        print(ex_why)
    except ValueError:
        logging.error('Invalid coordinates. Clearing and recapturing. Entered: ' + ex_why)
        ex_why = ''
    except IndexError:
        logging.error('Both x and y coordinates required. Clearing and recapturing. Entered: ' + ex_why)
        ex_why = ''
    return ex_why


def asphere_slope(conic: float, curvature: float, x: float, a: list):       # TODO: check the math in this! It differs by ~0.1% from NanoCAM 2D!
    logging.debug('Starting asphere_slope() function. Inputs: ' + str(conic) + ' ' + str(curvature) + ' ' + str(x) + ' ' + str(a))
    conicurv = (1 + conic) * np.square(curvature)
    complicated_root = np.sqrt(1 - (conicurv * np.square(x)))
    f_prime_intermed = x * curvature / complicated_root
    term_count = 1
    asph_contrib = 0
    for term in a:
        asph_contrib += float(term) * np.power(x, (term_count - 1)) * term_count
        term_count += 1
    f_prime = f_prime_intermed + asph_contrib
    return f_prime


def asphere_sag(conic: float, curvature: float, x: float, a: list):
    logging.debug(
        'Starting asphere_sag() function. Inputs: ' + str(conic) + ' ' + str(curvature) + ' ' + str(x) + ' ' + str(a))
    conicurv = (1 + conic) * np.square(curvature)
    complicated_root = np.sqrt(1 - (conicurv * np.square(x)))
    f_intermed = x * x * curvature / (1 + complicated_root)
    term_count = 1
    asph_contrib = 0
    for term in a:
        asph_contrib += float(term) * np.power(x, term_count)
        term_count += 1
    f = f_intermed + asph_contrib
    return f

def asphere_max_slope(conic: float, curvature: float, x_max: float, a: list):
    logging.debug('Starting asphere_max_slope() function. Inputs: ' + str(conic) + ' ' + str(curvature) + ' ' + str(x_max) + ' ' + str(a))
    desired_interval = .1
    zero_count = f_double_prime_previous = x_previous = 0
    xes = np.linspace(0, x_max, max(int(x_max / desired_interval) + 1, 10))
    # print('List of x values to test: ', xes)
    conicurv = (1 + conic) * np.square(curvature)
    approx_zero = 0
    for x in xes:
        complicated_root = np.sqrt(1 - (conicurv * np.square(x)))   # TODOne: this doesn't have the c_v * x^2 included when i did the 2nd derivative
        f_double_prime_intermed = curvature * np.square(x) * (np.square(conicurv) * np.square(x) / (np.power(1 - conicurv * np.square(x), 1.5) * np.square(complicated_root + 1))
                                                                       + 2 * np.square(conicurv) * np.square(x) / ((1 - conicurv * np.square(x)) * np.power(complicated_root + 1, 3))
                                                                       + conicurv / (complicated_root * np.square(complicated_root + 1))) + \
                                       4 * curvature * conicurv * np.square(x) / (complicated_root * np.square(complicated_root + 1)) + \
                                       2 * curvature / (complicated_root + 1)
        # print('f\'\' intermediate: ', f_double_prime_intermed)
        term_count = 1
        asph_contrib = 0
        for term in a:
            if term_count > 1:
                asph_contrib += float(term) * np.power(x, (term_count - 2)) * term_count * (term_count - 1)
            term_count += 1
        f_double_prime = f_double_prime_intermed + asph_contrib
        # print('f\'\': ', f_double_prime)
        if x > 0:
            if np.sign(f_double_prime) != np.sign(f_double_prime_previous):
                zero_count += 1
                b = f_double_prime_previous - x_previous * (f_double_prime - f_double_prime_previous) / (x - x_previous)
                x_est = -b * (x - x_previous) / (f_double_prime - f_double_prime_previous)
                print('Estimated Zero #', zero_count, ': ', x_est)
                approx_zero = max(abs(x_est), approx_zero)
        f_double_prime_previous = f_double_prime
        x_previous = x
    if zero_count < 1:
        approx_zero = x_max
    max_slope = asphere_slope(conic, curvature, approx_zero, a)
    return approx_zero, max_slope


def define_freeform(arrays: list = None, capturing_feature_data: bool = False):
    logging.debug('Starting define_freeform() function.')
    if arrays is None:
        arrays = []
    array_of_index_num = array_center = array_shape = array_spacing = array_dims = array_shear = ''
    features = []
    all_array_coords = []

    # Start capturing input

    while capturing_feature_data:
        array = ''
        # Enter feature parameters
        feature_type = input('Enter the feature type (Sphere, Asphere, Plane) (Don\'t enter a plane first, and just hit ENTER when all entry is complete:').lower()
        if feature_type.__len__() != 0:
            plane_diam = sph_radius = sph_diam = sph_center = edge_sag = asph_radius = asph_diam = asph_conic = asph_even = asph_center = asph_curv = asph_h_diam = ''
            if feature_type[0] == 's':
                feature_type = 'sphere'
                print('Vertex will be z=0')
                while sph_radius == '':
                    sph_radius = input('Enter the radius of the spherical surface in mm (positive = concave, negative = convex):')
                    try:
                        sph_radius = float(sph_radius)
                    except ValueError:
                        logging.warning('Invalid spherical radius. Value should be a float. Clearing and recapturing. Entered: ' + sph_radius)
                        sph_radius = ''
                while sph_diam == '':
                    sph_diam = input('Enter the diameter of the spherical surface in mm:')
                    # print(sph_diam)
                    try:
                        sph_diam = abs(float(sph_diam))
                        # print(sph_diam)
                        if abs(sph_radius) <= sph_diam / 2:
                            # TODOne: fill in code to prevent half diam >= part radius
                            logging.warning('Spherical Radius may not be less than the feature half-diameter;\nthe feature would not fill the requested diameter. Clearing and recapturing. Entered: ' + str(sph_diam))
                            sph_diam = ''
                    except ValueError:
                        logging.warning('Invalid diameter. Clearing and recapturing. Entered: ' + sph_diam)
                        sph_diam = ''
                while sph_center == '':
                    sph_center = input('Enter the center coordinates of this spherical surface, in x,y order:')
                    sph_center = check_cartesian_input(sph_center)
                edge_sag = sph_radius * (1 - np.cos(np.arcsin(sph_diam / 2 / sph_radius)))
                feature_specs = [feature_type, sph_radius, sph_diam, sph_center, edge_sag]
                features.append(feature_specs)
                print('Sphere Edge Sag = ', edge_sag)
            elif feature_type[0] == 'a':
                feature_type = 'asphere'
                print('Vertex will be z=0')
                while asph_radius == '':
                    asph_radius = input('Enter the radius of the aspheric surface in mm (positive = concave, negative = convex):')
                    try:
                        asph_radius = float(asph_radius)
                    except ValueError:
                        logging.warning('Invalid spherical radius. Value should be a float. Clearing and recapturing. Entered: ' + asph_radius)
                        asph_radius = ''
                while asph_diam == '':
                    asph_diam = input('Enter the diameter of the aspheric surface in mm:')
                    # print(asph_diam)
                    try:
                        asph_diam = abs(float(asph_diam))
                        # print(asph_diam)
                        if abs(asph_radius) <= asph_diam / 2:
                            logging.warning('Aspheric Radius may not be less than the feature half-diameter;\nthe feature would not fill the requested diameter. Clearing and recapturing. Entered: ' + str(asph_diam))
                            asph_diam = ''
                    except ValueError:
                        logging.warning('Invalid diameter. Clearing and recapturing. Entered: ' + asph_diam)
                        asph_diam = ''
                while asph_conic == '':
                    try:
                        asph_conic = input('Enter the conic constant (oblate elliptical (K > 0), spherical (K = 0), prolate elliptical (0 > K > −1), parabolic (K = −1), hyperbolic (K < −1)):')
                        asph_conic = float(asph_conic)
                        if asph_conic == 0:
                            print('Spheroid selected (unless aspheric terms are entered)')
                        elif asph_conic == -1:
                            print('Paraboloid selected (unless aspheric terms are entered)')
                        elif asph_conic > 0:
                            print('Oblate ellipsoid selected (unless aspheric terms are entered)')
                        elif asph_conic < -1:
                            print('Hyperboloid selected (unless aspheric terms are entered)')
                        elif -1 < asph_conic < 0:
                            print('Prolate ellipsoid selected (unless aspheric terms are entered)')
                    except ValueError:
                        logging.warning('Invalid conic constant. Clearing and recapturing. Entered: ' + asph_conic)
                        asph_conic = ''
                while asph_even == '':
                    try:
                        asph_even = input('Enter the even aspheric constants, starting from the 4th:').split(',')    # Input is text, don't forget to convert to float when extracting the coords
                        asph_curv = 1 / asph_radius
                        coord = asph_h_diam = float(asph_diam / 2)
                        edge_sag = asph_curv * coord ** 2 / (1 + np.sqrt(1 - (1 + asph_conic) * asph_curv ** 2 * coord ** 2))  # Generate the conic sag
                        coeff_order = 4
                        for aCon in asph_even:  # Add the aspheric sag to the conic sag
                            edge_sag += float(aCon) * coord ** coeff_order
                            coeff_order += 2
                    except ValueError:
                        logging.warning('Invalid even aspheric terms. Clearing and recapturing. Entered: ' + asph_even)
                        asph_even = ''
                while asph_center == '':
                    asph_center = input('Enter the center coordinates of this aspheric surface, in x,y order:')
                    asph_center = check_cartesian_input(asph_center)
                feature_specs = [feature_type, asph_radius, asph_diam, asph_conic, asph_even, asph_center, asph_curv, asph_h_diam, edge_sag]
                features.append(feature_specs)
                print('Asphere Edge Sag = ', edge_sag)
            elif feature_type[0] == 'p':
                feature_type = 'plane'
                while plane_diam == '':
                    try:
                        plane_diam = input('Enter the diameter of the plane in mm:')
                        plane_diam = abs(float(plane_diam))
                    except ValueError:
                        logging.warning('Invalid diameter. Clearing and recapturing. Entered: ' + plane_diam)
                        plane_diam = ''
                while edge_sag == '':
                    try:
                        edge_sag = input('Enter the height of this plane (you probably want to set this equal to the lens sag):')
                        edge_sag = float(edge_sag)
                    except ValueError:
                        logging.warning('Invalid edge sag. Clearing and recapturing. Entered: ' + edge_sag)
                        edge_sag = ''
                feature_specs = [feature_type, plane_diam, edge_sag]
                features.append(feature_specs)
                print('Plane Edge Sag = ', edge_sag)
        else:
            print('Sphere, Asphere, or Plane not selected. Finishing surface definition.')
            capturing_feature_data = False
            continue                        # Exit the while loop when the user is done entering feature data
        # Enter array parameters
        if feature_type[0] != 'p':
            while array == '':
                try:
                    array = input('Turn this feature into an array? (Y/N)').upper()[0]
                    if array == 'Y':
                        array = True
                    elif array == 'N':
                        array = False
                    else:
                        print('Invalid response. Type Y or N.')
                        array = ''
                except IndexError:
                    print('Invalid response. Type Y or N.')
                    logging.warning('Invalid response. Type Y or N. Entered: ' + array)
                    array = ''
        if array:
            while array_center == '':
                array_center = input('Enter the coordinates of the center of the array, separated by commas, in x,y order:')
                array_center = check_cartesian_input(array_center)
            while array_shape == '':
                array_shape = input('Is the array a hex, circle, or square grid?').lower()       # TODOne: insert response verification code for each input() line from here down
                try:
                    if array_shape[0] == 'h':
                        array_shape = 'hex'
                    elif array_shape[0] == 'c':
                        array_shape = 'circle'
                    elif array_shape[0] == 's':
                        array_shape = 'square'
                    else:
                        print('Invalid input. Type a shape. Entered: ' + array_shape)
                        array_shape = ''
                except IndexError:
                    logging.warning('Invalid input. Type a shape or ctrl-c if you intended to exit. Entered: ' + array_shape)
                    array_shape = ''
            while array_spacing == '':
                try:
                    array_spacing = input('Enter the horizontal grid spacing in mm:')
                    array_spacing = abs(float(array_spacing))
                except ValueError:
                    logging.warning('Invalid grid spacing. Should be a positive float. Entered: ' + array_spacing)
                    array_spacing = ''
            while array_dims == '':
                try:
                    array_dims = input('Enter the quantity of lens elements in the array, separated by commas, in x,y order:')
                    array_dims = (int(array_dims.split(',')[0]), int(array_dims.split(',')[1]))
                except IndexError:
                    logging.warning('Invalid array dimensions. Should be two integers separated by a comma. Entered: ' + array_dims)
                    array_dims = ''
            if array_shape == 'square':
                while array_shear == '':
                    try:
                        array_shear = input('Enter the array shear angle in degrees (positive = //, negative = \\\\, 0 = #):')
                        array_shear = float(array_shear)
                    except ValueError:
                        logging.warning('Invalid array shear angle. Should be an angle, in degrees. Entered: ' + array_shear)
                        array_shear = ''
            elif array_shape == 'hex':
                array_shear = 30
            else:
                array_shear = 0
            array_of_index_num = np.size(features, 0) - 1
            array_specs = [array_of_index_num, array_center, array_shape, array_spacing, array_dims, array_shear]
            arrays.append(array_specs)

    # Report the captured parameters
    print('Arrays:   ', arrays)
    print('Surfaces: ', features)

    # Create the Array coordinates:

    for a in arrays:
        array_coords = []
        x_div, y_div = [(int(a[4][0]) - 1) / 2, (int(a[4][1]) - 1) / 2]
        if a[2] == 'hex':
            y_modifier = np.cos(np.deg2rad(30))    # This modifies the vertical spacing so that the array becomes a true hex pattern    # TODO: check to make sure this implements hex spacing fully
        else:
            y_modifier = 1
        for nx in np.linspace(-x_div, x_div, int(a[4][0])):
            for ny in np.linspace(-y_div, y_div, int(a[4][1])):
                array_coords.append([ny * a[3] * np.sin(np.deg2rad(float(a[5]))) + nx * a[3] + float(a[1][0]), ny * a[3] * y_modifier + float(a[1][1])])
        print(array_coords)
        all_array_coords.append(array_coords)   # TODO: verify that the array coordinates are accurate for center != 0,0
    return features, arrays, all_array_coords


if __name__ == '__main__':
    ask = True
    outerArrays = []
    define_freeform(outerArrays, ask)
