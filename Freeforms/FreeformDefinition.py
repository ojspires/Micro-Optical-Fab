# FreeformDefinition.py     Oliver Spires   University of Arizona   1/31/2020
# This program takes user input from either the console or input arguments and builds feature definitions and arrays.
# TODO: use while loops and try...except ValueError to verify each input

import numpy


def define_freeform(arrays=None, capturing_feature_data=False):
    if arrays is None:
        arrays = []

    features = []
    all_array_coords = []
    array = ''

    # Start capturing input

    while capturing_feature_data:

        # Enter feature parameters
        feature_type = input('Enter the feature type (Sphere, Asphere, Plane) (Don\'t enter a plane first, and just hit ENTER when all entry is complete:').lower()
        if feature_type[0] == 's':
            print('Vertex will be z=0')
            sph_radius = float(input('Enter the radius of the spherical surface in mm (positive = concave, negative = convex):'))
            sph_diam = abs(float(input('Enter the diameter of the spherical surface in mm:')))
            sph_center = input('Enter the center coordinates of this spherical surface, in x,y order:')
            edge_sag = sph_radius * (1 - numpy.cos(numpy.arcsin(sph_diam / 2 / sph_radius)))
            feature_specs = [feature_type, sph_radius, sph_diam, sph_center, edge_sag]
            features.append(feature_specs)
        elif feature_type[0] == 'a':
            print('Vertex will be z=0')
            asph_radius = float(input('Enter the radius of the aspheric surface in mm (positive = concave, negative = convex):'))
            asph_diam = abs(float(input('Enter the diameter of the spherical surface in mm:')))
            asph_conic = float(input('Enter the conic constant (oblate elliptical (K > 0), spherical (K = 0), prolate elliptical (0 > K > −1), parabolic (K = −1), hyperbolic (K < −1)):'))
            asph_even = input('Enter the even aspheric constants, starting from the 4th:').split(',')    # Input is text, don't forget to convert to float when extracting the coords
            asph_center = input('Enter the center coordinates of this spherical surface, in x,y order:')     # Input is text, don't forget to convert to float when extracting the coords
            asph_curv = 1 / asph_radius
            coord = asph_h_diam = float(asph_diam / 2)
            edge_sag = asph_curv * coord ** 2 / (1 + numpy.sqrt(1 - (1 + asph_conic) * asph_curv ** 2 * coord ** 2))    # Generate the conic sag
            coeff_order = 4
            for aCon in asph_even:                                                                                   # Add the aspheric sag to the conic sag
                edge_sag += float(aCon) * coord ** coeff_order
                coeff_order += 2
            feature_specs = [feature_type, asph_radius, asph_diam, asph_conic, asph_even, asph_center, asph_curv, asph_h_diam, edge_sag]
            features.append(feature_specs)
        elif feature_type[0] == 'p':
            array = False
            plane_diam = abs(float(input('Enter the diameter of the plane in mm:')))
            edge_sag = float(input('Enter the height of this plane (you probably want to set this equal to the lens sag):'))
            feature_specs = [feature_type, plane_diam, edge_sag]
            features.append(feature_specs)
        else:
            print('Sphere, Asphere, or Plane not selected. Finishing surface definition.')
            capturing_feature_data = False
            continue                        # Exit the while loop when the user is done entering feature data
        print('Edge Sag = ', edge_sag)

        # Enter array parameters
        if feature_type[0] != 'p':
            array = input('Turn this feature into an array? (Y/N)').upper()[0]
            if array == 'Y':
                array = True
            elif array == 'N':
                array = False
            else:
                print('Invalid response. Type Y or N.')
        if array:
            array_center = input('Enter the coordinates of the center of the array, separated by commas, in x,y order:').split(',')
            array_shape = input('Is the array a hex, circle, or square grid?').lower()
            array_spacing = float(input('Enter the horizontal grid spacing in mm:'))
            array_dims = input('Enter the quantity of lens elements in the array, separated by commas, in x,y order:').split(',')
            if array_shape == 'square':
                array_shear = float(input('Enter the array shear angle in degrees (positive = //, negative = \\\\, 0 = #):'))
            elif array_shape == 'hex':
                array_shear = 30
            else:
                array_shear = 0
            array_of_index_num = numpy.size(features, 0) - 1
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
            y_modifier = numpy.cos(numpy.deg2rad(30))    # This modifies the vertical spacing so that the array becomes a true hex pattern
        else:
            y_modifier = 1
        for nx in numpy.linspace(-x_div, x_div, int(a[4][0])):
            for ny in numpy.linspace(-y_div, y_div, int(a[4][1])):
                array_coords.append([ny * a[3] * numpy.sin(numpy.deg2rad(float(a[5]))) + nx * a[3] + float(a[1][0]), ny * a[3] * y_modifier + float(a[1][1])])
        print(array_coords)
        all_array_coords.append(array_coords)
    return features, arrays, all_array_coords


if __name__ == '__main__':
    ask = True
    outerArrays = []
    define_freeform(outerArrays, ask)
