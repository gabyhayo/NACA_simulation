import os
import numpy as np
import matplotlib.pyplot as plt


def visu_optim_intermediate(naca_optim):
    print(os.getcwd())
    print(os.listdir(naca_optim))
    path = os.path.join(naca_optim,
                        naca_optim+'.txt')
    with open(path, 'r') as f:
        rows = list(f.readlines())[1:]
        for i, row in enumerate(rows):
            rows[i] = np.float_(row.strip('\n').split('\t'))
    print(rows)
    iter = range(len(rows))
    force = [-line[1] for line in rows]
    angle = [-line[2] for line in rows]
    m_list = [-line[3] for line in rows]
    p_list = [-line[4] for line in rows]

    angle = np.abs(angle / max(np.abs(angle)))
    m_list = np.abs(m_list / max(np.abs(m_list)))
    p_list = np.abs(p_list / max(np.abs(p_list)))

    fig, ax = plt.subplots(1,1)
    ax.plot(iter, force)
    ax.plot(iter, angle)
    ax.plot(iter,m_list)
    ax.plot(iter,p_list)

    plt.show()

visu_optim_intermediate('optim_0.03')