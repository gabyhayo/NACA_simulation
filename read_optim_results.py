import os
import numpy as np
import matplotlib.pyplot as plt

optim_list = ['optim_0.03',
              'optim_0.035',
              'optim_0.04',
              'optim_0.045',
              'optim_0.05',
              ]


def visu_optim_intermediate(naca_optim, show_FLAG=True, cord_length=True):
    """

    :param naca_optim: name of the optimization
    :param show_FLAG: True if you want to plot
    :return:
    """
    print(os.getcwd())
    print(os.listdir(naca_optim))
    path = os.path.join(naca_optim,
                        naca_optim + '.txt')
    with open(path, 'r') as f:
        rows = list(f.readlines())[1:]
        for i, row in enumerate(rows):
            rows[i] = np.float_(row.strip('\n').split('\t'))
    # print(rows)
    iter = range(len(rows))
    force = [-line[1] for line in rows]
    angle = [line[2] for line in rows]
    m_list = [line[3] for line in rows]
    p_list = [line[4] for line in rows]
    c_list = [line[-1] for line in rows]

    ind_max_force = np.argmax(force)

    if cord_length:
        print(f'{naca_optim} : {100. * 0.001 / c_list[ind_max_force]:2f}, {c_list[ind_max_force]}')
    else:
        print(f'{naca_optim} max force : {force[ind_max_force]}, {angle[ind_max_force]}, {m_list[ind_max_force]}, {p_list[ind_max_force]}')


    angle = np.abs(angle / max(np.abs(angle)))
    m_list = np.abs(m_list / max(np.abs(m_list)))
    p_list = np.abs(p_list / max(np.abs(p_list)))

    fig, ax = plt.subplots(1, 1)
    ax.plot(iter, force, label='force')
    ax.plot(iter, angle, label='angle')
    ax.plot(iter, m_list, label='m parameter')
    ax.plot(iter, p_list, label='p parameter')
    ax.legend()
    ax.set_title(naca_optim)

    if show_FLAG:
        plt.show()

for optim_name in optim_list:
    visu_optim_intermediate(optim_name, show_FLAG=False)
# plt.show()
