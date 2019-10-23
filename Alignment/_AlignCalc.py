#!C:\Program Files\Python36\python.exe
# _AlignCalc.py     Oliver Spires   10/16/2019
# This script takes the input data from metrology equipment to calculate and output the required alignment adjustments
# for diamond-tool alignment.

import numpy as np


def align_calc(part_radius: float, part_radius_meas: float, part_diam: float, part_diam_meas: float, part_cx: bool,
               cut_cw: bool, cutting: bool, ogive: float, fringe_in: bool, center_cyl: bool, center_diam: float,
               profile_m: bool, profile_pv: float, tool_radius: float):
    print('_AlignCalc Inputs:')
    print(part_radius, part_radius_meas, part_diam, part_diam_meas, part_cx, cut_cw, cutting,
          ogive, fringe_in, center_cyl, center_diam, profile_m, profile_pv, tool_radius)
    max_fnum_to_use = part_radius / part_diam
    fnum_actual = part_radius_meas / part_diam_meas
    center_pip_r = center_diam / 2000
    if center_cyl:
        y_adjust = np.negative(center_pip_r)
    else:
        y_adjust = center_pip_r
    part_radius_error = part_radius - part_radius_meas
    if part_cx:
        cc_geometry_adjust = part_radius_error
    else:
        cc_geometry_adjust = np.negative(part_radius_error)

    x_error_ogive = .000318 * ogive * part_radius_meas / part_diam_meas
    if cutting:
        x_error_ogive = -x_error_ogive
    if not part_cx:
        x_error_ogive = -x_error_ogive
    if cut_cw:
        x_error_ogive = -x_error_ogive
    if fringe_in:
        x_error_ogive = -x_error_ogive
    x_adjust_ogive = x_error_ogive
    print('Commanded adjustment based on ogive:')
    print(x_adjust_ogive)

    x_error_pv = part_radius_meas / part_diam_meas * 0.008 * profile_pv
    if not part_cx:
        x_error_pv = np.negative(x_error_pv)
    if cut_cw:
        x_error_pv = np.negative(x_error_pv)
    if not profile_m:
        x_error_pv = np.negative(x_error_pv)
    x_adjust_pv = x_error_pv
    print('Commanded adjustment based on PV:')
    print(x_adjust_pv)

    if ogive == 0:
        x_adjust = x_adjust_pv
    else:
        x_adjust = np.average((x_adjust_pv, x_adjust_ogive))

    if (part_cx and (part_cx == fringe_in)) or (not part_cx and part_cx != fringe_in):
        z_backup = np.abs(part_radius * np.cos(np.arcsin((part_diam / 2 + x_adjust) / part_radius)) -
                          part_radius * np.cos(np.arcsin(part_diam / 2 / part_radius)))
    else:
        z_backup = 0

    return np.round((x_adjust, y_adjust, z_backup, cc_geometry_adjust, max_fnum_to_use, fnum_actual), 6)


if __name__ == "__main__":
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

    output = np.round(align_calc(part_radius, part_radius_meas, part_diam, part_diam_meas, part_cx, cut_cw, cutting,
                                 ogive, fringe_in, center_cyl, center_diam, profile_m, profile_pv, tool_radius), 6)
    print(output)
