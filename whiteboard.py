import shutil
import os
import gmsh
import keyboard
import numpy as np

# help(gmsh.model.geo)
#
# os.chdir('Mesh_optim')
# print(os.path.dirname(os.getcwd()))

# os.system('cmd')
# print('here')
# os.system('0')
# keyboard.press_and_release('enter')
# i, m, p, t, c = [12.8569, 4.121256, 8.161568, 45.3669,0.5166]
#
# print(f'naca{m:.2f}_{p:.2f}_{t:.2f}_{c:.2f}_{i:.2f}')
#
# row = '0.019700 -0.034720'
# ind_space = [i for i in range(len(row)) if row[i] == ' '][0]  # index of first space
# print(row[ind_space:ind_space + 3])
# if '-' in row[ind_space:ind_space + 3]:  # check if y is negative
#     row = row.strip(' ').split(' ')
# else:
#     row = row.strip(' ').split('  ')
# print(row)
# # get coordinates
# print(float(row[0]))
# print(float(row[1]))

alpha_dic = {}

for R in [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06]:
    # rotation velocity
    w = 10_000  # tour/min
    w = w * 2. * np.pi / 60.  # rad/s

    # air density
    rho = 1.  # kg.m-3

    # maximum radius of the blade
    R_tot = 0.06  # m

    # surface of the disc described by the blade
    S = np.pi * R_tot ** 2  # m2

    # motor power
    P = 80  # W

    # velocity of the air along z-axis
    Vz = (P / (2 * rho * S)) ** (1 / 3)
    print(Vz)

    # velocity of the air along theta-axis
    Vo = R * w

    # angle between the x-axis and the direction of the wind
    alpha = np.arctan(Vz / Vo) * 180 / np.pi

    alpha_dic[str(R)] = alpha

print(alpha_dic)
print(alpha_dic.items())

# help(gmsh.model.geo.rotate)
# print(np.cos(5))
# print(np.cos(5*np.pi/180.))