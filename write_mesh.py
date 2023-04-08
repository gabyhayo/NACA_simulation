import csv
import matplotlib.pyplot as plt
import gmsh
import os
import numpy as np
import shutil

h = 0.01  # mesh size

naca_profile = [name for name in os.listdir() if name.startswith('naca')]  # list of all naca folders in the dir
print(naca_profile)


def check_dir(naca_name, rotate_angle=None):
    """
    This function check if the directory exists or not, if not make the directory
    :param naca_name: the name of the naca profile
    :param rotate_angle: if rotation of the profile, equals to the rotation in degree (float)
    :return: /
    """
    if rotate_angle:
        path = naca_name + '_' + str(int(rotate_angle))  # define the path
    else:
        path = naca_name

    if not os.path.isdir(path):
        os.mkdir(path)  # make directory
        shutil.copy(os.path.join(naca_name, naca_name + '.csv'),
                    os.path.join(path, path + '.csv'))  # copy the naca profile '.csv' in the new directory


def get_coords(naca_name, dat=True, naca=False, normalize=True, to0=True):
    """
    get coordinates of the control points of your profile
    :param naca_name:  the name of the naca profile
    :param dat: True if .csv comes from the scrapping
    :param naca: True if .csv manually downloaded
    :param normalize: True if you want your profile coordinates to be between -1 and 1
    :param to0: True if you want your profile x-coordinates to begin at 0
    :return: x-coordinates (np.array), Y-coordinates (np.array)
    """
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

        # read .csv file
        with open(path, 'r') as f:
            reader = list(csv.reader(f))[1:]

        X = []
        Y = []
        for i in range(len(reader)):
            row = reader[i][0]
            if naca_name == 'profile_base':
                row = row.strip(' ').split(' ')
            elif '-' in row[1:]:
                row = row.strip(' ').split(' ')
            else:
                row = row.strip(' ').split('  ')
            # get coordinates
            X.append(float(row[0]))
            Y.append(float(row[1]))

        X = np.array(X)
        Y = np.array(Y)

        # translate x-coordinates to 0
        if to0:
            X = X - min(X)

        # normalize x and y coordinates
        if normalize:
            max_value = max(np.max(abs(X)), np.max(abs(Y)))

            X, Y = X / max_value, Y / max_value
    return X, Y


def create_NACA(m, p, t, c, plot_Flag=False, save_path=''):
    """
    create a NACA profile from the 4 digits and the chord length,
    and write its associate .csv (dat type for geet_coords function)
    :param m: maximum camber in percentage of chord
    :param p: position of the maximum camber in tenths of chord
    :param t: maximum thickness in percentage of chord
    :param c: chord length
    :param plot_Flag: True if you want to plot the profile
    :return: /
    """
    m = m * c / 100
    p = p * c / 10
    t = t * c / 100

    n0 = 10
    n1 = 10
    n2 = 20
    x = np.concatenate((np.linspace(0, 0.02 * c, n0), np.linspace(0.02 * c, 0.1 * c, n1), np.linspace(0.1 * c, c, n2)))
    print(x)
    yc = []
    yt = []
    theta = []

    for elem in x:
        if elem < p:
            yc.append(m * (2 * p * elem - elem ** 2) / p ** 2)
            theta.append(np.arctan(m * (2 * p - 2 * elem) / p ** 2))
        else:
            yc.append(m * (1 - 2 * p + 2 * p * elem - elem ** 2) / (1 - p) ** 2)
            theta.append(np.arctan(m * (2 * p - 2 * elem) / (1 - p ** 2)))

        yt.append(t * (0.2969 * np.sqrt(
            elem) - 0.1260 * elem - 0.3516 * elem ** 2 + 0.2843 * elem ** 3 - 0.1015 * elem ** 4) / 0.2)

    yc = np.array(yc)
    yt = np.array(yt)
    theta = np.array(theta)

    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)

    if plot_Flag:
        plt.scatter(xu, yu, c='r')
        plt.scatter(xl, yl)
        plt.xlim(left=-0.05, right=1.05)
        plt.ylim(bottom=-0.2, top=0.2)
        plt.show()

    if save_path:
        writer = ['NACA\n']
        for x, y in zip(xu[::-1][:-1], yu[::-1][:-1]):
            if y >= 0:
                writer.append(f'{x}  {y}\n')
            else:
                writer.append(f'{x} {y}\n')

        for x, y in zip(xl, yl):
            if y >= 0:
                writer.append(f'{x}  {y}\n')
            else:
                writer.append(f'{x} {y}\n')

        with open(save_path, 'w', newline='\n') as f:
            f.writelines(writer)


def write_mesh(naca_name,
               mesh_name='mesh.msh',
               rotate_angle=None,
               in_optim_Flag=False):
    """
    write the mesh of the naca in the naca_name folder, gmsh 2.16.0
    :param naca_name: the name of the naca profile
    :param mesh_name: the name of the generated mesh
    :param rotate_angle: if rotation of the profile, equals to the rotation in degree (float)
    :return: /
    """
    X, Y = get_coords(naca_name=naca_name)

    points = []
    curves = []

    # gmsh
    gmsh.initialize()
    for i in range(len(X)):
        if i == 0:
            first_point = gmsh.model.geo.add_point(X[i], Y[i], 0, h)
            points.append(first_point)
        else:
            point = gmsh.model.geo.add_point(X[i], Y[i], 0., h)
            points.append(point)

    # to reloop the curve on itself -> close curve
    points.append(first_point)

    # create curves
    curves.append(gmsh.model.geo.add_spline(points))

    if rotate_angle:
        angle = - np.pi * rotate_angle / 180.
        for curve in curves:  # rotation of the mesh
            gmsh.model.geo.rotate([(1, curve)], 0., 0., 0., 0., 0., 1., angle)

        # impossible to get the new coordinates of the points, compute by hand
        coords = [[x, y] for x, y in zip(X, Y)]
        mat_rot = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        coords_rot = [np.matmul(mat_rot, elem) for elem in coords]
        X_rot, Y_rot = zip(*coords_rot)  # new coordinates of the points after the rotation

        Y_min, Y_max = min(Y_rot), max(Y_rot)

        if Y_min < -0.2:  # outside the box of BoundaryLayerMesh
            for curve in curves:
                # translation in y-direction in order to be in the box
                gmsh.model.geo.translate([(1, curve)], 0., - 0.2 - Y_min + (0.4 - (Y_max + abs(Y_min))) / 2, 0.)

    face = gmsh.model.geo.add_curve_loop(curves)  # create face

    surface = gmsh.model.geo.add_plane_surface([face])  # create surface, mandatory for mesh generation

    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate()
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.16)

    if rotate_angle and not in_optim_Flag:
        save_name = naca_name + '_' + str(int(rotate_angle))
    else:
        save_name = naca_name

    gmsh.write(os.path.join(save_name, mesh_name))
    gmsh.finalize()


def write_t(naca_name,
            mesh_name,
            output_name='naca.t',
            rotate_angle=None):
    """
    write the .t file associated with a mesh
    :param naca_name: the name of the naca profile
    :param mesh_name: the name of the associated profile
    :param output_name: the name of the .t file generated
    :param rotate_angle: if rotation of the profile, equals to the rotation in degree (float) !!! only used for path !!!
    :return: /
    """
    # define path
    if rotate_angle:
        path = naca_name + '_' + str(int(rotate_angle))
    else:
        path = naca_name

    # copy the mesh in ./
    shutil.copy(os.path.join(path, mesh_name),
                mesh_name)

    # launch scripts
    os.system(""f'python gmsh2mtc.py {mesh_name} {output_name}'"")
    os.system(""f'echo 0 | mtc.exe {output_name}')

    # copy the .t in ./naca_name
    shutil.copy(output_name,
                os.path.join(path, output_name),
                )

    # remove the mesh and .t in ./
    os.remove(mesh_name)
    os.remove(output_name)


def launch_mesh_optim(naca_name, t_name='', rotate_angle=None):
    """
    launch the optimization of the boundary layer mesh of the naca_name profile
    :param naca_name: the name of the naca profile
    :param t_name: the name of the .t file
    :param rotate_angle: if rotation of the profile, equals to the rotation in degree (float) !!! only used for path !!!
    :return: /
    """
    print(f'naca name = {naca_name}')

    # define name of the .t file
    if not t_name:
        if rotate_angle:
            t_name = naca_name + '_' + str(int(rotate_angle)) + '.t'
        else:
            t_name = naca_name + '.t'

    # define path
    if rotate_angle:
        path = naca_name + '_' + str(int(rotate_angle))
    else:
        path = naca_name

    if not os.path.isdir(os.path.join(path, 'Output_mesh_optim')):  # try if the Boundary layer mesh already computed
        base_dir = 'Mesh_optim_' + path
        if os.path.isdir(base_dir):  # if the directory already exists
            shutil.rmtree(base_dir)  # remove the directory
        shutil.copytree('Mesh_optim', base_dir)  # create a new directory with all the files for the simulation
        shutil.copy(os.path.join(path, t_name),
                    os.path.join(base_dir, 'naca.t'))  # copy the .t file

        os.chdir(base_dir)  # go to base_dir
        os.system('"LANCER"')  # launch the optimization of the boundary layer mesh
        os.chdir(os.path.dirname(os.getcwd()))  # go to ./
        if os.path.isdir(os.path.join(path, 'Output_mesh_optim')):  # if the directory already exists
            shutil.rmtree(os.path.join(path, 'Output_mesh_optim'))  # remove the directory
        shutil.copytree(os.path.join(base_dir, 'Output'),
                        os.path.join(path,
                                     'Output_mesh_optim'))  # create a directory with the results in naca_name folder
        shutil.rmtree(base_dir)  # remove the directory in which the optimization was computed


def launch_simu(naca_name, t_name='', rotate_angle=None, Re=None, radius=None, only_sensors=True):
    """
    launch the simulation of air flow around the naca_name profile
    :param naca_name: the name of the naca profile
    :param t_name: the name of the .t file
    :param rotate_angle: if rotation of the profile, equals to the rotation in degree (float) !!! only used for path !!!
    :param Re: Reynolds number if you have to change it
    :param radius: the radius of the section
    :param only_sensors: True if you want to save only the sensors results
    :return: /
    """
    print(f'naca name = {naca_name}')

    # define name of the .t file
    if not t_name:
        if rotate_angle:
            t_name = naca_name + '_' + str(int(rotate_angle)) + '.t'
        else:
            t_name = naca_name + '.t'

    # define path
    if rotate_angle:
        path = naca_name + '_' + str(int(rotate_angle))
    else:
        path = naca_name

    base_dir = 'Simulator_' + path

    if os.path.isdir(base_dir):  # if the directory already exists
        shutil.rmtree(base_dir)  # remove the directory

    shutil.copytree('Simulator', base_dir)  # create a new directory with all the files for the simulation

    # change Reynolds number in the simulation
    if Re:
        with open(os.path.join(base_dir, 'IHM.mtc'), 'r') as f:
            lines = list(f.readlines())
        ind = [i for i in range(len(lines)) if 'MuFluide' in lines[i]][0]
        lines[ind] = f'{{ Target= MuFluide {1 / Re} }}\n'
        with open(os.path.join(base_dir, 'IHM.mtc'), 'w') as f:
            f.writelines(lines)

    path2sensor = os.path.join(os.path.join(base_dir, 'resultats'), 'capteurs')
    results_files = [elem for elem in os.listdir(path2sensor)]

    # delete former results file, in order to only have the results of the current simulation
    for file in results_files:
        with open(os.path.join(path2sensor, file), 'r') as f:
            lines = list(f.readlines())
        with open(os.path.join(path2sensor, file), 'w') as f:
            f.writelines(lines[0])

    shutil.copy(os.path.join(path, t_name),
                os.path.join(base_dir, 'naca.t'))  # copy the .t file
    mesh_optimized = 'Mesh_00020.t'  # the mesh used in the simulation
    shutil.copy(os.path.join(path, os.path.join('Output_mesh_optim', mesh_optimized)),
                os.path.join(base_dir, 'domaine.t'))  # copy the domaine

    os.chdir(base_dir)  # go to base_dir
    os.system('"LANCER"')  # launch the simulation
    os.chdir(os.path.dirname(os.getcwd()))  # go to ./

    if radius:
        results_folders = 'resultats_' + str(radius)
    else:
        results_folders = 'resultats'
    if os.path.isdir(os.path.join(path, results_folders)):
        shutil.rmtree(os.path.join(path, results_folders))
    if only_sensors:
        os.mkdir(os.path.join(path, results_folders))
        shutil.copytree(os.path.join(os.path.join(base_dir, 'resultats'), 'capteurs'),
                        os.path.join(os.path.join(path, results_folders), 'capteurs'))
        # create a directory with the results in naca_name folder
    else:
        shutil.copytree(os.path.join(base_dir, 'resultats'),
                        os.path.join(path, results_folders))  # create a directory with the results in naca_name folder
    shutil.rmtree(base_dir)  # remove the directory in which the optimization was computed


def get_force(path, alpha, t_min=10.):
    """
    compute the force from the 'Efforts.txt' file
    :param path: str, path to the Efforts.txt file
    :param alpha: angle between the x-axis and the wind direction, alpha = arctan(Vz/Vo)
    :param t_min: minimum time such as average Fl and Fd are computed for t > t_min, avoid transitory regime
    :return: Fl cos(alpha) - Fd sin(alpha)
    """
    # open 'Efforts.txt' file
    with open(path, 'r', newline='\n') as f:
        lines = list(f.readlines())

    T, Fd, Fl = [], [], []

    for line in lines[1:]:  # get time, Fd, Fl
        T.append(float(line.strip('\r\n').split('\t')[0]))
        Fd.append(float(line.strip('\r\n').split('\t')[1]))
        Fl.append(float(line.strip('\r\n').split('\t')[2]))

    ind_t_min = [i for i in range(len(T)) if T[i] == t_min][0]  # get index such as T[ind] = t_min
    Fd_value = np.mean(Fd[ind_t_min:])
    Fl_value = np.mean(Fl[ind_t_min:])

    return Fl_value * np.cos(alpha) - Fd_value * np.sin(alpha)


if __name__ == "__main__":
    pass
    # get_force(os.path.join(
    #     r'C:\Users\computer\etudes\Mines\2A\Mecaero\Aero\NACA_simulation\Simulator_naca6412_5\resultats\capteurs',
    #     'Efforts.txt'))
    # for name in naca_profile:
    #     write_mesh(name, mesh_name=name+'.msh')
    #     write_t(naca_name=name, mesh_name=name+'.msh', output_name=name+'.t', Ramy_version=input)
    # launch_mesh_optim('naca0008')
    # launch_simu('naca2412')
