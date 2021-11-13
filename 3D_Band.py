import numpy as np
import pandas as pd
import mayavi.mlab as mlab
from tvtk.api import tvtk
import math
from pandas import Series, DataFrame

# conversion
eV = 27.2114
NaN = float('NaN')


# read out of an input file
reference = input("Introduce your input file: \n")
reference = open(reference, 'r')
count2 = 0.0
ceck2 = True
file_list = []
no_band = []
while ceck2 == True:
    line2 = reference.readline()
    fine = len(line2)
    save_el = line2[0:fine]
    if count2 == 0:
        pt_x = save_el  # Number of file aka sampling point along the x direction
    elif count2 == 1:
        pt_y = save_el  # Number of sampling point explored in each segment aka no. sampling point along the y direction
    elif count2 == 2:
        sx = save_el  # starting point on the x direction
    elif count2 == 3:
        fx = save_el  # ending point on the x direction
    elif count2 == 4:
        sy = save_el  # starting point on the y direction
    elif count2 == 5:
        fy = save_el  # ending point on the y direction
    else:
        if save_el != 'end':  # readout of the file involved
            save_el = line2[0:(fine-1)]
            file_list.append(save_el)
        else:
            ceck2 = False
    count2 += 1

# conversion of pt_x and pt_y in integer
pt_x = int(pt_x)
pt_y = int(pt_y)
sx = float(sx)
sy = float(sy)
fx = float(fx)
fy = float(fy)

# conversion of file_list in a list of dataframe
for i in range(0, len(file_list)):  # (0,len(file_list))
    # determination of skiprow
    headers = ['#', '@']
    skiprow = 0
    header = open(file_list[i], 'r')
    ceck = True
    while ceck == True:
        line = header.readline()
        if line[0] in headers:
            skiprow += 1
        else:
            header.close()
            ceck = False
    # data import
    file_list[i] = pd.read_csv(
        file_list[i], sep="\s+", header=None, engine='python', skiprows=skiprow, skipfooter=1)
    no_band.append(len(file_list[i].columns))


# no band last element
last_file = len(no_band)


nb0 = no_band[0]
for f in range(1, last_file):
    if no_band[f] != nb0:
        print('Error, Number of bands do not match', f, no_band[f])
        exit()
    else:
        no_band2 = max(no_band)


# axis
dx = np.linspace(sx, fx, pt_x)
dy = np.linspace(sy, fy, pt_y)
X, Y = np.meshgrid(dx, dy)

# creation of Z matrix
Z = np.zeros((pt_y, pt_x, no_band2))
count1 = 0
for i in file_list:
    for p in range(1, no_band2):
        n = p-1
        Z[:, count1, n] = i[p]*eV

        for k in range(0, len(i[p])):
            if Z[k, count1, n] > 0.55 or Z[k, count1, n] < -0.55:
                Z[k, count1, n] = NaN

        if count1 >= pt_x:
            count1 = 0
    count1 += 1

# algorithm to find the Weyl point coordinates
E_Delta = 100
Weyl_x_file = 0
Weyl_x2_file = 0
Weyl_y_index = 0
Weyl_y2_index = 0
for k in range(0, pt_x):
    i = file_list[k]
    for index in range(0, pt_y):
        Delta_E = (i.iloc[index, 10]*eV) - (i.iloc[index, 9]*eV)
        if abs(Delta_E) < E_Delta:
            Weyl_x_file = k
            Weyl_y_index = index
            Cond_energy = i.iloc[index, 10]*eV
            Val_energy = i.iloc[index, 9]*eV
            E_Delta = abs(Delta_E)

if abs(E_Delta) < 0.009999999999999999:
    print(Weyl_x_file, Weyl_y_index)
    x_seg_lenght = fx-sx
    y_seg_lenght = fy-sy
    step_x = 1/pt_x
    step_y = 1/pt_y
    Weyl_x = ((Weyl_x_file*step_x)*x_seg_lenght)+sx
    Weyl_y = ((Weyl_y_index*step_y)*y_seg_lenght)+sy
    print('You probably have a Weyl point at kx:', Weyl_x, 'ky:', Weyl_y,
          'Conduction band energy:', Cond_energy, 'eV and valence band:', Val_energy, 'eV', 'delta E:', E_Delta)
else:
    print("You don't have any possible Weyl point")


fig = mlab.figure(bgcolor=(1, 1, 1), fgcolor=(0, 0, 0), size=(1920, 1080))


for i in range(8, no_band2-5):
    s = mlab.mesh(X, Y, Z[:, :, i])


# mlab.pipeline.user_defined(s, filter=tvtk.CubeAxesActor())
mlab.outline(s, extent=[sx, fx, sy, fy, -0.55, 0.55])
mlab.axes(x_axis_visibility=True, xlabel='kx', y_axis_visibility=True,
          ylabel='ky', nb_labels=5)

mlab.axes().axes.font_factor = 0.6

# mlab.axes(x_axis_visibility=True,y_axis_visibility=True,z_axis_visibility=True, nb_labels=5)
# ax2=mlab.axes(x_axis_visibility=True,y_axis_visibility=True,z_axis_visibility=True, nb_labels=5,extent=[0,1,0,2,0,1])
mlab.view(azimuth=45, elevation=90, distance=2.4)

# box=tvtk.CubeAxesActor()

mlab.show()
