# NACA simulation
 Project Mecaero - Mines Paris

The aim of the project is to build a drone. I am in the subgroup in charge of designing the blade, we have to choose the shape of the blade in order to optimize the lift of the drone.

In write_launch.py, there are scripts to create a NACA profile, write the mesh and the .t file but also to launch the Boundary layer mesh optimization and the simulation.

miss_France.py is a script used to launch a single simulation.

optim_NACA.py is a script which compute the best 4-digits NACA profile and the angle of incidence for a defined radius.
