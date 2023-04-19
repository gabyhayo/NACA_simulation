import os
import numpy as np
import sys
from write_launch import write_mesh, write_t, launch_mesh_optim, launch_simu, check_dir, get_force, create_NACA

# naca_list = ['naca2424', 'naca4424', 'naca6412']
# angle_list = [0, 5, 10, 15]

# naca = sys.argv[1]

m = float(sys.argv[1])
p = float(sys.argv[2])
t = float(sys.argv[3])

angle = float(sys.argv[4])
R = float(sys.argv[5])

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

# blade width
c = 0.02  # m

# velocity of the air along z-axis
Vz = (P / (2 * rho * S)) ** (1 / 3)

# velocity of the air along theta-axis
Vo = R * w

# angle between the x-axis and the direction of the wind
alpha = np.arctan(Vz/Vo)

# norm of the velocity of the air
V = np.sqrt(Vz ** 2 + Vo ** 2)

# Reynolds number
Re = rho * V * c * np.cos(angle) / mu


def Miss_France(naca_name, rotate_angle):
    """
    launch the simulation for the naca_name profile from its shape points
    :param naca_name: the name of the naca profile
    :param rotate_angle: if rotation of the profile, equals to the rotation in degree (float)
    :return: /
    """
    naca_name = 'naca_'+str(m)+'_'+str(p)+'_'+str(t)+ '_' + str(int(rotate_angle))
    # define mesh name
    mesh_name = naca_name + '_' + str(int(rotate_angle)) + '.msh'

    # os.mkdir(naca_name)
    check_dir(naca_name, rotate_angle)
    create_NACA(m, p, t, c, save_path=os.path.join(naca_name, naca_name+'.csv'))

    write_mesh(naca_name, mesh_name=mesh_name, rotate_angle=rotate_angle)
    write_t(naca_name=naca_name,
            mesh_name=mesh_name,
            output_name=naca_name + '_' + str(int(rotate_angle)) + '.t',
            rotate_angle=rotate_angle)

    launch_mesh_optim(naca_name=naca_name, rotate_angle=rotate_angle)
    launch_simu(naca_name=naca_name, rotate_angle=rotate_angle, Re=Re, radius=R)

    if R:
        results_folders = 'resultats_' + str(R)
    else:
        results_folders = 'resultats'

    path2Efforts = os.path.join(os.path.join(os.path.join(naca_name + '_' + str(int(rotate_angle))
                                                          , results_folders),
                                             'capteurs'
                                             ),
                                'Efforts.txt'
                                )

    force = get_force(path2Efforts, alpha)

    with open('force_Miss_France.txt', 'a') as f:
        f.write(f'{naca_name}\t{angle}\t{R}\t{force:.3f}\n')


Miss_France(naca_name='nothing', rotate_angle=angle)
