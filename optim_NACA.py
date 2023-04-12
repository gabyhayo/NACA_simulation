import os
import shutil
import sys
import numpy as np
import pickle
from scipy import optimize

from write_launch import create_NACA, write_mesh, write_t, launch_mesh_optim, launch_simu, get_force

R = float(sys.argv[1])  # radius in m

c = 0.02  # m, chord length
t = 100. * 0.001 / c  # maximum thickness in percentage of chord
x0 = [5., 6., 3.]  # angle[degree], m, p

base_dir = 'optim_' + str(R)
if os.path.isdir(base_dir):
    shutil.rmtree(base_dir)
os.mkdir(base_dir)

shutil.copy('gmsh2mtc.py',
            os.path.join(base_dir, 'gmsh2mtc.py'))
shutil.copy('mtc.exe',
            os.path.join(base_dir, 'mtc.exe'))
shutil.copytree('Mesh_optim',
                os.path.join(base_dir, 'Mesh_optim'))
shutil.copytree('Simulator',
                os.path.join(base_dir, 'Simulator'))

os.chdir(base_dir)

with open(base_dir + '.txt', 'w') as f:
    f.write('iteration\t-force\tangle\tm\tp\tt\tc\n')

# rotation velocity
w = 10_000  # tour/min
w = w * 2. * np.pi / 60.  # rad/s

# air density
rho = 1.  # kg.m-3

# dynamic viscosity coefficient
mu = 1.8 * 10 ** (-5)  # Pa.s

# maximum radius of the blade
R_tot = 0.06  # m

# surface of the disc described by the blade
S = np.pi * R_tot ** 2  # m2

# motor power
P = 167  # W

# velocity of the air along z-axis
Vz = (P / (2 * rho * S)) ** (1 / 3)

# velocity of the air along theta-axis
Vo = R * w

# angle between the x-axis and the direction of the wind
alpha = np.arctan(Vz / Vo)

# norm of the velocity of the air
V = np.sqrt(Vz ** 2 + Vo ** 2)

optim_step = 0


def cost_function(X):
    """
    create a NACA profile from parameters and compute the lift force
    :param X: 5-elements array (floats) :
                    - i, angle of incidence in degree
                    the following coefficients are those for the NACA profile
                    - m, maximum camber in percentage of chord
                    - p, position of the maximum camber in tenths of chord
                    - t, maximum thickness in percentage of chord
                    - c, chord length
    :return: Fl cos(alpha) - Fd sin(alpha)
    """
    global optim_step
    optim_step += 1

    # i, m, p, t, c = X  # assign values, angle, m, p, t, c
    i, m, p = X  # assign values, angle, m, p

    # Reynolds number
    Re = rho * V * c * np.cos(i) / mu

    naca_name = f'naca{optim_step}_{m:.2f}_{p:.2f}_{t:.2f}_{c:.2f}_{i:.2f}'  # unique because of optim_step
    os.mkdir(naca_name)  # make directory
    create_NACA(m, p, t, save_path=os.path.join(naca_name, naca_name + '.csv'), plot_Flag=False)
    write_mesh(naca_name, mesh_name=naca_name + '.msh', rotate_angle=i, in_optim_Flag=True)
    write_t(naca_name, mesh_name=naca_name + '.msh',
            output_name=naca_name + '.t', )  # no rotate angle because it is only for the name
    launch_mesh_optim(naca_name=naca_name, )  # no rotate angle because it is only for the name
    launch_simu(naca_name=naca_name, Re=Re, only_sensors=True,
                radius=R)  # no rotate angle because it is only for the name

    if R:
        results_folders = 'resultats_' + str(R)
    else:
        results_folders = 'resultats'

    path2Efforts = os.path.join(os.path.join(os.path.join(naca_name, results_folders),
                                             'capteurs'
                                             ),
                                'Efforts.txt'
                                )

    force = get_force(path2Efforts, alpha)

    with open(base_dir + '.txt', 'a') as f:
        f.write(f'{optim_step}\t{-force:.5f}\t{i:.5f}\t{m:.5f}\t{p:.5f}\t{t:.5f}\t{c:.5f}\n')

    return -force


res = optimize.minimize(cost_function, x0, method='Nelder-Mead')

with open('results.pkl', 'wb') as f:
    pickle.dump(res, f, protocol=pickle.HIGHEST_PROTOCOL)
