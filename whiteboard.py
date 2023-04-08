import shutil
import os
import gmsh
import keyboard

# help(gmsh.model.geo)
#
# os.chdir('Mesh_optim')
# print(os.path.dirname(os.getcwd()))

# os.system('cmd')
# print('here')
# os.system('0')
# keyboard.press_and_release('enter')
i, m, p, t, c = [12.8569, 4.121256, 8.161568, 45.3669,0.5166]

print(f'naca{m:.2f}_{p:.2f}_{t:.2f}_{c:.2f}_{i:.2f}')