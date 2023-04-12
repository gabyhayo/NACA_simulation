#------------------------------------------------------------------------------------------------

## USELESS

#------------------------------------------------------------------------------------------------


from scipy import minimize
import os
import numpy
from write_launch import write_mesh, write_t, launch_mesh_optim, launch_simu

name = 'optim_brute'

def function(x):
    X, Y = zip(*x)

    write_mesh(naca_name=name, mesh_name='optim_brute.msh',
               optim_Flag=True, X_optim=X, Y_optim=Y)

    write_t(naca_name=name, mesh_name='optim_brute.msh', output_name='naca.t')
    write_mesh(naca_name=name,)

    launch_mesh_optim(naca_name=name)
    launch_simu(naca_name=name)

