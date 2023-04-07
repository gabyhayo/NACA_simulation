import os
import numpy as np
import sys
import keyboard
from write_mesh import write_mesh, write_t, launch_mesh_optim, launch_simu, check_dir

naca_list = ['naca2424', 'naca4424', 'naca6412']
angle_list = [0, 5, 10, 20]

w = 10_000  # tour/min
w = w * 2. * np.pi / 60.  # rad/s
rho = 1.3  # kg.m-3
mu = 1.8 * 10 ** (-5)  # Pa s
R_tot = 0.12  # m
S = np.pi * R_tot ** 2
P = 167  # W
L = 0.02  # m [largeur de l'aile]

naca = sys.argv[1]
angle = float(sys.argv[2])
R = float(sys.argv[3])

Vz = (P / (2 * rho * S)) ** (1 / 3)
Vo = R * w

V = np.sqrt(Vz ** 2 + Vo ** 2)

Re = rho * V * L * np.cos(angle)/ mu

# for naca in naca_list:
#     for angle in angle_list:
#         mesh_name = naca + '_' + str(angle) + '.msh'
#
#         check_dir(naca, angle)
#
#         write_mesh(naca, mesh_name=mesh_name, rotate_angle=angle)
#         write_t(naca_name=naca, mesh_name=mesh_name, output_name=naca+ '_' + str(angle)+'.t',
#                 Ramy_version=True, rotate_angle=angle)
# keyboard.press_and_release('enter')
# print('here')
# keyboard.press_and_release('enter')
#
#
# launch_mesh_optim(naca_name=naca, rotate_angle=angle)
launch_simu(naca_name=naca, rotate_angle=angle, Re=Re)
