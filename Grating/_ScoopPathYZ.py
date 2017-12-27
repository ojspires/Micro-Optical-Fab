# ScoopPathYZ.py    Oliver Spires   12/12/17
# This script generates a toolpath in the YZ plane, which scribes a straight line into a part, with an entry- and exit-
# path which is circular in shape and tangent to the grating plane, for a smooth entry/exit of the tool.


def scoop_path_yz(scribe_doc: float, tan_curve_radius: float, half_diameter: int):
    """
    :type scribe_doc: float
    :type tan_curve_radius: float
    :type half_diameter: int
    """
    import numpy as np
    y = np.linspace(2*half_diameter, -2*half_diameter, 500*half_diameter)
    z = []
    for y_loc in y:
        if y_loc > half_diameter:
            z.append(tan_curve_radius*(1-np.cos(np.arcsin((y_loc-half_diameter)/tan_curve_radius)))-scribe_doc)
        elif y_loc < -half_diameter:
            z.append(tan_curve_radius*(1-np.cos(np.arcsin((y_loc+half_diameter)/tan_curve_radius)))-scribe_doc)
        else:
            z.append(-scribe_doc)
    return y, z


if __name__ == "__main__":

    scribeDoC = .001
    tanCurveRadius = 60
    halfDiameter = 5
    (y_out, z_out) = scoop_path_yz(scribeDoC, tanCurveRadius, halfDiameter)
    import matplotlib.pyplot as plt
    plt.plot(y_out, z_out)
    plt.show()
    print(y_out[0])
