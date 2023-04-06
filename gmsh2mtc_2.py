#!/usr/bin/env python
#
# GMSH4MTC
#
# Utilitaire de conversion des maillages gmsh (.msh) de format 2 et 4
# 2D et 3D en format mtc (.t).
#
# Fonctionne pour les maillages surfaciques et volumiques.
# Uniquement pour les éléments triangulaires, tetrahedriques.
#
# Peut être drag&drop sur le fichier à transformer.
#
# maxime.renault@minesparis.psl.eu
# 06/2022
#
# Inspiré du travail de Tommy Carozzani en 2010.

import sys, os
import numpy as np
import time
import gmsh

fichier_entree = sys.argv[1]
fichier_sortie = sys.argv[2]

_, ext = os.path.splitext(fichier_entree)

if ext == '.stl':
    gmsh.initialize()
    gmsh.open(fichier_entree)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(fichier_entree.rsplit('.stl', 1)[0] + '.msh')
    gmsh.finalize()
    fichier_entree = fichier_entree.rsplit('.stl', 1)[0] + '.msh'

# fichier_sortie = fichier_entree.rsplit('.msh', 1)[0] + '.t'

print("#########################################################")
print("# GMSH VERSION 2 to 4 MTC CONVERTER - CFL - MINES PARIS #")
print("#########################################################")
print("No mtc.exe version")
print("")


###########

def gmsh4mtc_single_step(input=fichier_entree, output=fichier_sortie):
    print("Initialisation...\n")

    f = open(input)
    f.readline()
    version = f.readline().split()[0]
    if len(version) > 1:
        version = version.split('.')[0]
    if version != '4' and version != '2':
        print("This version of gmsh isn't supported")
        input("Press enter to close...")
        sys.exit()

    flags = {"$Nodes": [],
             "$EndNodes": [],
             "$Elements": [],
             "$EndElements": []}
    ii = range(len(list(flags.keys())))

    nb_noeuds = 0

    connect_3d = []
    connect_2d = []
    connect_1d = []

    ###########

    print("Recuperation position flags...\n")

    t = f.readline()

    while t:
        t = t.strip("\t\n")
        if t.startswith("$"):
            for i in ii:
                if (t == list(flags.keys())[i]):
                    flags[t].append(f.tell())
                    break
        t = f.readline()

    ###########

    print("Traitement connectivites...\n")

    if version == '4':
        for index in range(len(flags["$Elements"])):
            f.seek(flags["$Elements"][index])

            t = f.readline()  # ligne ignoree (nb d'elements)
            t = f.readline()

            while (t and f.tell() != flags["$EndElements"][index]):
                t = t.strip("\t\n").split()

                if (len(t) <= 1):
                    break

                if (t[2] != '2' and t[2] != '4'):
                    for i in range(int(t[-1])):
                        f.readline()

                if (t[2] == '2'):  # triangle
                    for i in range(int(t[-1])):
                        elem = f.readline().strip("\t\n").split()
                        lig = [int(elem[1]), int(elem[2]), int(elem[3])]
                        connect_2d.append(lig)

                if (t[2] == '4'):  # tetrahedre
                    for i in range(int(t[-1])):
                        elem = f.readline().strip("\t\n").split()
                        lig = [int(elem[1]), int(elem[2]), int(elem[3]), int(elem[4])]
                        connect_3d.append(lig)

                t = f.readline()

    if version == '2':
        for index in range(len(flags["$Elements"])):
            f.seek(flags["$Elements"][index])

            t = f.readline()  # ligne ignoree (nb d'elements)
            t = f.readline()

            while (t and f.tell() != flags["$EndElements"][index]):
                t = t.split()

                if (len(t) <= 1):
                    break

                if (t[1] == '2'):  # triangle
                    lig = [int(t[-3]), int(t[-2]), int(t[-1])]
                    connect_2d.append(lig)

                if (t[1] == '4'):  # tetraedre
                    lig = [int(t[-4]), int(t[-3]), int(t[-2]), int(t[-1])]
                    connect_3d.append(lig)

                t = f.readline()

    connect_2d = np.array(connect_2d)
    connect_3d = np.array(connect_3d)

    # dim = 3
    # if(len(connect_3d) == 0):
    #    dim = 2

    ###########

    print("Verification noeuds et bords...")

    # noeuds

    nodes = []

    if version == '4':
        for index in range(len(flags["$Nodes"])):
            f.seek(flags["$Nodes"][index])
            f.readline()  # ligne ignoree (nb noeuds)

            t = f.readline()

            while (t and f.tell() != flags["$EndNodes"][index]):
                t = t.strip("\t\n").split()

                if (len(t) <= 1):
                    break

                for i in range(int(t[-1])):
                    f.readline()

                for i in range(int(t[-1])):
                    node = f.readline().strip("\t\n").split()
                    # if dim==3:
                    nodes.append([float(node[0]), float(node[1]), float(node[2])])
                    # else:
                    #    nodes.append([float(node[0]), float(node[1])])

                t = f.readline()

    if version == '2':
        for index in range(len(flags["$Nodes"])):
            f.seek(flags["$Nodes"][index])
            f.readline()  # ligne ignoree (nb noeuds)

            t = f.readline()

            while (t and f.tell() != flags["$EndNodes"][index]):
                t = t.strip("\t\n").split()

                if (len(t) <= 1):
                    break

                # if dim==3:
                nodes.append([float(t[1]), float(t[2]), float(t[3])])
                # else:
                #    nodes.append([float(t[1]), float(t[2])])

                t = f.readline()

    nodes = np.array(nodes)

    dim = 3
    if (np.all(nodes[:, 0] == nodes[0, 0])):
        dim = 2
        nodes = nodes[:, 1:]
    elif (np.all(nodes[:, 1] == nodes[0, 1])):
        dim = 2
        nodes = nodes[:, -1:1]
    elif (np.all(nodes[:, 2] == nodes[0, 2])):
        dim = 2
        nodes = nodes[:, :2]
    elif (len(connect_3d) == 0):
        dim = 2.5

    print("   - Detection des bords")

    if dim == 3:
        del connect_2d

        tris1 = connect_3d[:, [0, 2, 1]]  # Order is very important !
        tris2 = connect_3d[:, [0, 1, 3]]
        tris3 = connect_3d[:, [0, 3, 2]]
        tris4 = connect_3d[:, [1, 2, 3]]

        tris = np.concatenate((tris1, tris2, tris3, tris4), axis=0)
        tris_sorted = np.sort(tris, axis=1)  # creates a copy, may be source of memory error
        tris_sorted, uniq_idx, uniq_cnt = np.unique(tris_sorted, axis=0, return_index=True, return_counts=True)
        connect_2d = tris[uniq_idx][uniq_cnt == 1]

    if dim == 2:
        lin1 = connect_2d[:, [0, 1]]  # Once again, order is very important !
        lin2 = connect_2d[:, [2, 0]]
        lin3 = connect_2d[:, [1, 2]]

        lin = np.concatenate((lin1, lin2, lin3), axis=0)
        lin_sorted = np.sort(lin, axis=1)  # creates a copy, may be source of memory error
        lin_sorted, uniq_idx, uniq_cnt = np.unique(lin_sorted, axis=0, return_index=True, return_counts=True)
        connect_1d = lin[uniq_idx][uniq_cnt == 1]

    print("   - Detection des noeuds à effacer")

    to_delete = np.arange(1, len(nodes) + 1)  # Tous les indices de noeuds
    used_elems = np.unique(np.concatenate((connect_3d.flat, connect_2d.flat)))  # Tous les indices UTILISES

    bools_keep = np.in1d(to_delete, used_elems)
    to_delete = to_delete[~bools_keep]
    del used_elems

    print("   - Suppression des noeuds inutiles\n")

    nodes = nodes[bools_keep]
    del bools_keep

    if dim == 3 or dim == 2.5:
        connect_3d.flat -= np.searchsorted(to_delete, connect_3d.flat, side='left')
        connect_2d.flat -= np.searchsorted(to_delete, connect_2d.flat, side='left')

    if dim == 2:
        connect_2d.flat -= np.searchsorted(to_delete, connect_2d.flat, side='left')
        connect_1d.flat -= np.searchsorted(to_delete, connect_1d.flat, side='left')

    ##########

    nb_elems = len(connect_2d) + len(connect_3d)
    if dim == 2:
        nb_elems += len(connect_1d)
        print("Nb elements 1d : " + str(len(connect_1d)))

    print("Nb elements 2d : " + str(len(connect_2d)))
    print("Nb elements 3d : " + str(len(connect_3d)) + "\n")
    print("Dimension du maillage: " + str(dim) + "\n")

    ###########

    print("Ecriture .t ...")

    fo = open(output, "w")

    lig = str(len(nodes)) + " " + str(dim) + " " + str(nb_elems) + " " + str(dim + 1) + "\n"
    if (dim == 2.5):
        lig = str(len(nodes)) + " 3 " + str(nb_elems) + " 4\n"
    fo.write(lig)

    for node in nodes:
        fo.write("{0:.16f} {1:.16f}".format(node[0], node[1]))
        if (dim == 3 or dim == 2.5):
            fo.write(" {0:.16f}".format(node[2]))
        fo.write(" \n")

    for e in connect_3d:
        fo.write(str(e[0]) + " " + str(e[1]) + " " + str(e[2]) + " " + str(e[3]) + " \n")

    for e in connect_2d:
        if (dim == 3 or dim == 2.5):
            fo.write(str(e[0]) + " " + str(e[1]) + " " + str(e[2]) + " 0 \n")
        else:
            fo.write(str(e[0]) + " " + str(e[1]) + " " + str(e[2]) + " \n")

    if dim == 2:
        for e in connect_1d:
            fo.write(str(e[0]) + " " + str(e[1]) + " 0 \n")

    ###########

    fo.close()

    print("OK.")
    return


gmsh4mtc_single_step()