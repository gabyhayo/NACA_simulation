import csv
import sys
import matplotlib.pyplot as plt
import gmsh
import os
import numpy as np
import shutil

h = 0.01  # mesh size

# input = sys.argv[1]
naca_profile = [name for name in os.listdir() if name.startswith('naca')]
print(naca_profile)


def check_dir(naca_name, rotate_angle=None):
    if rotate_angle:
        path = naca_name + '_' + str(rotate_angle)
    else:
        path = naca_name

    if not os.path.isdir(path):
        os.mkdir(path)
        shutil.copy(os.path.join(naca_name, naca_name + '.csv'),
                    os.path.join(path, path + '.csv'))


def get_coords(naca_name, dat=True, naca=False, normalize=True, to0=True):
    if naca:
        path = os.path.join(naca_name, naca_name + '-il.csv')
        with open(path, 'r') as f:
            reader = list(csv.reader(f))
            in_coord_FLAG = False
            X = []
            Y = []
            for i in range(len(reader)):
                row = reader[i]
                # print(row)
                if row[0] == 'X(mm)' and reader[i - 1][0] == 'Airfoil surface':
                    in_coord_FLAG = True
                elif in_coord_FLAG and row[0] == '':
                    in_coord_FLAG = False
                elif in_coord_FLAG:
                    X.append(float(row[0]))
                    Y.append(float(row[1]))
            X = np.array(X)
            Y = np.array(Y)

            max_value = max(np.max(abs(X)), np.max(abs(Y)))

            if normalize:
                X, Y = X / max_value, Y / max_value
    elif dat:
        path = os.path.join(naca_name, naca_name + '.csv')

        with open(path, 'r') as f:
            reader = list(csv.reader(f))[1:]
            # print(reader[1][0])
            # print(reader[1][0].strip(' ').split(' '))

        X = []
        Y = []
        for i in range(len(reader)):
            row = reader[i][0]
            if naca_name == 'profile_base':
                row = row.strip(' ').split(' ')
            elif '-' in row:
                row = row.strip(' ').split(' ')
            else:
                row = row.strip(' ').split('  ')

            # print(row)
            X.append(float(row[0]))
            Y.append(float(row[1]))

        X = np.array(X)
        Y = np.array(Y)

        if to0:
            X = X - min(X)

        if normalize:
            max_value = max(np.max(abs(X)), np.max(abs(Y)))

            X, Y = X / max_value, Y / max_value
    # print(X, Y)
    return X, Y


def create_NACA(m, p, t, c):
    m = m * c / 100
    p = p * c / 10
    t = t * c / 100

    n = 100
    x = np.linspace(0, c, n)
    yc = []
    yt = []
    theta = []
    print(len(x))

    for elem in x:
        if elem < p:
            yc.append(m * (2 * p * elem - elem ** 2) / p ** 2)
            theta.append(np.arctan(m * ( 2 * p - 2 * elem)/ p ** 2))
        else:
            yc.append(m * (1 - 2 * p + 2 * p * elem - elem ** 2) / (1 - p) ** 2)
            theta.append(np.arctan(m * ( 2 * p - 2 * elem)/ (1 - p ** 2)))

        yt.append(t * (0.2969 * np.sqrt(
            elem) - 0.1260 * elem - 0.3516 * elem ** 2 + 0.2843 * elem ** 3 - 0.1015 * elem ** 4) / 0.2)

    yc = np.array(yc)
    yt = np.array(yt)
    theta = np.array(theta)

    print(yc)

    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)

    plt.scatter(xu, yu, c='r')
    plt.scatter(xl, yl)
    plt.xlim(left=-0.05, right=1.05)
    plt.ylim(bottom=-0.2, top=0.2)
    plt.show()


# create_NACA(6, 4, 12, 1)


# print(get_coords('naca0008'))


def write_mesh(naca_name, mesh_name='mesh.msh',
               optim_Flag=False, X_optim=None, Y_optim=None,
               rotate_angle=None):
    if optim_Flag:
        X, Y = X_optim, Y_optim

    else:
        X, Y = get_coords(naca_name=naca_name)

    gmsh.initialize()

    points = []
    curves = []

    for i in range(len(X)):
        if i == 0:
            first_point = gmsh.model.geo.add_point(X[i], Y[i], 0, h)
            # if rotate_angle:
            #     gmsh.model.geo.rotate([(0, first_point)], 0., 0., 0., 0., 0., 1., np.pi * rotate_angle / 180.)

            points.append(first_point)
        else:
            point = gmsh.model.geo.add_point(X[i], Y[i], 0., h)
            # print(f'point = {point}')
            # if rotate_angle:
            #     gmsh.model.geo.rotate([(0, point)], 0., 0., 0., 0., 0., 1., np.pi * rotate_angle / 180.)

            points.append(point)

    points.append(first_point)

    # if rotate_angle:
    #     for point in points:
    #         print(point)
    #         gmsh.model.geo.rotate([(0,point)], 0.,0., 0., 0., 0., 1., np.pi*rotate_angle/180.)

    curves.append(gmsh.model.geo.add_spline(points))
    if rotate_angle:
        for curve in curves:
            gmsh.model.geo.rotate([(1, curve)], 0., 0., 0., 0., 0., 1., -np.pi * rotate_angle / 180.)

    # print(points)
    # print(curves)

    face = gmsh.model.geo.add_curve_loop(curves)
    # print(face)
    # gmsh.model.geo.rotate([(2, face)], 0.,0., 0., 0., 0., 1., np.pi*rotate_angle/180.)

    surface = gmsh.model.geo.add_plane_surface([face])

    gmsh.model.geo.synchronize()

    gmsh.model.mesh.generate()

    gmsh.option.setNumber("Mesh.MshFileVersion", 2.16)
    if rotate_angle:
        save_name = naca_name + '_' + str(rotate_angle)
    else:
        save_name = naca_name
    gmsh.write(os.path.join(save_name, mesh_name))

    gmsh.finalize()


def write_t(naca_name, mesh_name, output_name='naca.t', Ramy_version=False, rotate_angle=None):
    if rotate_angle:
        path = naca_name + '_' + str(rotate_angle)
    else:
        path = naca_name

    shutil.copy(os.path.join(path, mesh_name),
                mesh_name)
    if not Ramy_version:
        os.system(""f'python gmsh2mtc_2.py {mesh_name} {output_name}'"")

    else:
        os.system(""f'python gmsh2mtc.py {mesh_name} {output_name}'"")
        os.system(""f'mtc.exe {output_name}')

    shutil.copy(output_name,
                os.path.join(path, output_name),
                )
    os.remove(mesh_name)
    os.remove(output_name)


# write_mesh('naca0009', rotate_angle=-30.)
# for name in naca_profile:
#     write_mesh(name, mesh_name=name+'.msh')
#     write_t(naca_name=name, mesh_name=name+'.msh', output_name=name+'.t', Ramy_version=input)
write_mesh('naca0008', mesh_name='naca0008.msh')
write_t(naca_name='naca0008', mesh_name='naca0008.msh', output_name='naca0008.t')


def launch_mesh_optim(naca_name, t_name='', rotate_angle=None):
    print(f'naca name = {naca_name}')
    if not t_name:
        if rotate_angle:
            t_name = naca_name + '_' + str(int(rotate_angle)) +'.t'
        else:
            t_name = naca_name + '.t'

    if rotate_angle:
        path = naca_name + '_' + str(int(rotate_angle))
    else:
        path = naca_name

    base_dir = 'Mesh_optim_' + path
    if os.path.isdir(base_dir):
        shutil.rmtree(base_dir)
    shutil.copytree('Mesh_optim', base_dir)
    shutil.copy(os.path.join(path, t_name),
                os.path.join(base_dir, 'naca.t'))

    os.chdir(base_dir)
    os.system('"LANCER"')
    os.chdir(os.path.dirname(os.getcwd()))
    if os.path.isdir(os.path.join(path, 'Output_mesh_optim')):
        shutil.rmtree(os.path.join(path, 'Output_mesh_optim'))
    shutil.copytree(os.path.join(base_dir, 'Output'),
                    os.path.join(path, 'Output_mesh_optim'))
    shutil.rmtree(base_dir)


launch_mesh_optim('naca0008')


def choose_mesh(naca_name):
    return 'mesh_00020.t'


def launch_simu(naca_name, t_name='', rotate_angle=None, Re=None):
    print(f'naca name = {naca_name}')
    if not t_name:
        if rotate_angle:
            t_name = naca_name + '_' + str(int(rotate_angle)) + '.t'
        else:
            t_name = naca_name + '.t'

    if rotate_angle:
        path = naca_name + '_' + str(int(rotate_angle))
    else:
        path = naca_name

    base_dir = 'Simulator_' + path

    if os.path.isdir(base_dir):
        shutil.rmtree(base_dir)

    shutil.copytree('Simulator', base_dir)
    if Re:
        with open(os.path.join(base_dir, 'IHM.mtc'), 'r') as f:
            lines = list(f.readlines())
        ind = [i for i in range(len(lines)) if 'MuFluide' in lines[i]][0]
        lines[ind] = f'{{ Target= MuFluide {1/Re} }}\n'
        with open(os.path.join(base_dir, 'IHM.mtc'), 'w') as f:
            f.writelines(lines)

    path2sensor = os.path.join(os.path.join(base_dir, 'resultats'), 'capteurs')
    results_files = [elem for elem in os.listdir(path2sensor)]
    for file in results_files:
        with open(os.path.join(path2sensor, file), 'r') as f:
            lines = list(f.readlines())
        with open(os.path.join(path2sensor, file), 'w') as f:
            f.writelines(lines[0])

    shutil.copy(os.path.join(path, t_name),
                os.path.join(base_dir, 'naca.t'))
    mesh_optimized = choose_mesh(naca_name=path)
    shutil.copy(os.path.join(path, os.path.join('Output_mesh_optim', mesh_optimized)),
                os.path.join(base_dir, 'domaine.t'))

    os.chdir(base_dir)
    os.system('"LANCER"')
    os.chdir(os.path.dirname(os.getcwd()))
    shutil.copytree(os.path.join(base_dir, 'resultats'),
                    os.path.join(path, 'resultats'))
    shutil.rmtree(base_dir)

# launch_simu('naca2412')

# help(shutil)


# with open('n6409-il.csv', 'r') as f:
#     reader = csv.reader(f)
#     reader = list(reader)
#     writer = []
#     X = []
#     Y = []
#     for i in range(61):
#         # if i == 0:
#         #     first_point = gmsh.model.geo.add_point(float(reader[i][0]),float(reader[i][1]),0, h)
#         #     points.append(first_point)
#         # else:
#         #     point = gmsh.model.geo.add_point(float(reader[i][0]), float(reader[i][1]), 0, h)
#         #     # print(f'point = {point}')
#         #     points.append(point)
#         X.append(float(reader[i][0]))
#         Y.append(float(reader[i][1]))
#
#         # print(i)
#         # print(row)
#         # writer.append(f'Point({i}) = ' + '{' + f'{float(reader[i][0])},{float(reader[i][1])}, 0.,h' + '};\n')
#         writer.append(f'Point({i}) = {{{float(reader[i][0])},{float(reader[i][1])}, 0.,{h}}};\n')
# X = np.array(X)
# Y = np.array(Y)
#
# Xmax = np.max(X)
# Ymax = np.max(Y)
# max_value = max(Xmax, Ymax)
# X = X / max_value
# Y = Y / max_value
# print(f'{Xmax}, {Ymax}')


# print(f'Point({i}) = ' + '{' + f'{float(reader[i][0])},{float(reader[i][1])}, 0.,h' + '};\n')
# print(f'Point({i}) = {{{float(reader[i][0])},{float(reader[i][1])}, 0.,h}};\n')


# print('here')

# os.system('"mtc.exe surface.t 0 0 0"')


# Spline_list = ['Spline(1) = {0:60};\n',
#                'Spline(2)={60,0};\n',
#                'Line Loop(3) = {1, 2};\n',
#                'Plane Surface(4) = {3};\n'
#                ]
# for elem in Spline_list:
#     writer.append(elem)

# with open('doc.geo', 'w', newline='\n') as f1:
#     f1.writelines(writer)
