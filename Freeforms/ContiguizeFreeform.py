# ContiguizeFreeform.py   Oliver Spires   4/24/18
# This program takes a 3D R-theta-Z profile, one with a freeform on one section of the part and a rotationally symmetric
# surface on the other part of the part. This script replaces that rot. symm segment with tangent lines that flatten out
# in slope as they get farther from the freeform surface.

import numpy as np
import tkinter
from tkinter import filedialog
import csv
import sys
import matplotlib.pyplot as plt

# Import the file
trzfilename = ''
rtzfilename = 'G:/My Drive/Work/180402 Umiami/DesignParameter_Polar_back rtz Scale Fixed Decimated.csv'
if rtzfilename == '':
    rtzfilename = filedialog.askopenfilename(initialdir="/", title="Select surface R-theta-Z .csv file",
                                             filetypes=(("R-theta-Z .CSV Files", "*.csv"), ("all files", "*.*")))
rtzpath = rtzfilename.split("/")[0:-1]  # Take the path from the RTZ file
rtzpath = '/'.join(rtzpath)  # Rejoin it into a single string
surf = []
surfrow = []

with open(rtzfilename, newline='') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in csvreader:
        for col in row:
            surfrow.append(float(col))
        surf.append(surfrow)
        surfrow = []
    # print(surf[0][0:10])
    # print(surf[1][0:10])

histTest = np.histogram(surf[56][1:], bins=2000)
# print(histTest)
# fig = plt.figure()
# ax = plt.axes()
# ax.plot(histTest[1][0:-1], histTest[0])
# plt.show(block=True)


applicableRows = []
bar_length = 60
row_start = 15
row_max = np.size(surf, 0) - 1
row_count = np.size(surf, 0) - row_start
for row_index_scan in (np.linspace(row_start, row_max, row_count)):
    # Progress bar:
    percent = float(row_index_scan) / row_max
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\rProcessing Input:   [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()
    histRow = np.histogram(surf[int(row_index_scan)][1:], bins=2000)
    if histRow[0][0] > histRow[0][-1]:
        # print(row_index)
        start_col = surf[int(row_index_scan)].index(histRow[1][0])       # find where the r.Symm section starts
        surf[int(row_index_scan)].reverse()                              # reverse the array to search again
        end_col = - surf[int(row_index_scan)].index(histRow[1][0]) - 1   # find where the r. Symm section ends
        surf[int(row_index_scan)].reverse()                              # restore the array to its initial orientation
        applicableRows.append([int(row_index_scan), histRow[1][0], start_col, end_col])

# print(applicableRows)
# TODO: get rid of the tk window. Bypassed for now
# TODOne: use the applicable rows and columns... gather the slope leading in and out of the r.Symm segment and blend the Z points

rowIndices = [item[0] for item in applicableRows]
stepArray = [0]
halvingArray = np.logspace(0, -10, num=25, endpoint=True, base=5)
for step in halvingArray:
    stepArray.append(stepArray[-1] + step)
applicableSize = np.size(applicableRows, 0)
# for row_index_calc in rowIndices:
#     percent = (rowIndices.index(row_index_calc)) / applicableSize
#     hashes = '#' * int(round(percent * bar_length))
#     spaces = ' ' * (bar_length - len(hashes))
#     sys.stdout.write("\rProcessing Output:   [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
#     sys.stdout.flush()
#     lRise = (surf[row_index_calc][applicableRows[rowIndices.index(row_index_calc)][2]-1] -
#              surf[row_index_calc][applicableRows[rowIndices.index(row_index_calc)][2]-2])
#     rRise = (surf[row_index_calc][applicableRows[rowIndices.index(row_index_calc)][3]+2] -
#              surf[row_index_calc][applicableRows[rowIndices.index(row_index_calc)][3]+1])
#     # print(applicableRows[rowIndices.index(row_index_calc)])
#     # print(surf[row_index_calc][(applicableRows[rowIndices.index(row_index_calc)][2]-2):(applicableRows[rowIndices.index(row_index_calc)][2]+1)])
#     surf[row_index_calc][applicableRows[rowIndices.index(row_index_calc)][2]:
#                          (applicableRows[rowIndices.index(row_index_calc)][2] + 25)] = \
#         [i * lRise + surf[row_index_calc][applicableRows[rowIndices.index(row_index_calc)][2] - 1] for i in stepArray[1:]]
#     # print(surf[row_index_calc][(applicableRows[rowIndices.index(row_index_calc)][2]-2):(applicableRows[rowIndices.index(row_index_calc)][2]+1)])
#     stepArray.reverse()
#     surf[row_index_calc][(applicableRows[rowIndices.index(row_index_calc)][3] - 24):
#                          applicableRows[rowIndices.index(row_index_calc)][3]+1] = \
#         [i * -rRise + surf[row_index_calc][applicableRows[rowIndices.index(row_index_calc)][3] + 1] for i in stepArray[0:-1]]
#     stepArray.reverse()
#     # print(surf[row_index_calc][(applicableRows[rowIndices.index(row_index_calc)][2] + 24):(applicableRows[rowIndices.index(row_index_calc)][3] - 24)])
#     surf[row_index_calc][(applicableRows[rowIndices.index(row_index_calc)][2] + 25):
#                          (applicableRows[rowIndices.index(row_index_calc)][3] - 24)] = \
#         [surf[row_index_calc][(applicableRows[rowIndices.index(row_index_calc)][2] + 24)]] * \
#         np.size(surf[row_index_calc][(applicableRows[rowIndices.index(row_index_calc)][2] + 25):
#                                      (applicableRows[rowIndices.index(row_index_calc)][3] - 24)])
#     # print(surf[row_index_calc][(applicableRows[rowIndices.index(row_index_calc)][2] + 24):(applicableRows[rowIndices.index(row_index_calc)][3] - 24)])

for row_index_calc in rowIndices:
    percent = (rowIndices.index(row_index_calc)) / applicableSize
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\rProcessing Output:   [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()
    print(row_index_calc)
    col_count = np.size(surf, 1) + applicableRows[rowIndices.index(row_index_calc)][3] + 1
    span = int(np.ceil(np.size(col_count)/2))
    col_indices = np.linspace(applicableRows[rowIndices.index(row_index_calc)][2], col_count, col_count)
    col_indices = list(col_indices)
    for col_index_calc in col_indices[:span]:
        col_index_calc = int(col_index_calc)
        surf[row_index_calc][col_index_calc] = np.average([surf[row_index_calc - 1][col_index_calc - 1],
                                                           surf[row_index_calc - 1][col_index_calc + 1],
                                                           surf[row_index_calc - 1][col_index_calc],
                                                           surf[row_index_calc][col_index_calc - 1]])
    col_indices.reverse()
    for col_index_calc in col_indices[:span]:
        col_index_calc = int(col_index_calc)
        surf[row_index_calc][col_index_calc] = np.average([surf[row_index_calc - 1][col_index_calc - 1],
                                                           surf[row_index_calc - 1][col_index_calc + 1],
                                                           surf[row_index_calc - 1][col_index_calc],
                                                           surf[row_index_calc][col_index_calc + 1]])
    # surf[row_index_calc][applicableRows[rowIndices.index(row_index_calc)][2]:(applicableRows[rowIndices.index(row_index_calc)][2] + 25)]

with open(rtzfilename[:-4] + '.out' + rtzfilename[-4:], 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for row_out in surf:
        spamwriter.writerow(row_out)
