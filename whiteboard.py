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

row = '0.019700 -0.034720'
ind_space = [i for i in range(len(row)) if row[i] == ' '][0]  # index of first space
print(row[ind_space:ind_space + 3])
if '-' in row[ind_space:ind_space + 3]:  # check if y is negative
    row = row.strip(' ').split(' ')
else:
    row = row.strip(' ').split('  ')
print(row)
# get coordinates
print(float(row[0]))
print(float(row[1]))