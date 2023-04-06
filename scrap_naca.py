import os
import shutil

import requests
import csv

# r = requests.get('http://airfoiltools.com/plotter/index?airfoil=naca0021-il/tocsv',
#                  allow_redirects=True)

# r1 = requests.get('airfoiltools.com/plotter/tocsv')
# print(r.content)
# json = r.json()
# print(json)
#
# with open("save.csv", 'w') as f:
#     f.write(r.content)

def scrap(naca_name, url):
    print(naca_name)
    # r = requests.get(url)
    # if r.status_code == 200:
    #     print(r.content)
    #     content = (r.content).decode()
    #     if os.path.isdir(naca_name):
    #         shutil.rmtree(naca_name)
    #     os.mkdir(naca_name)
    #     with open(os.path.join(naca_name, naca_name + '.csv'), 'w', newline='\n') as f:
    #         f.write(content)

    try:
        r = requests.get(url)
        if r.status_code == 200:
            print('exists')
            # print(r.content)
            content = (r.content).decode()
            if os.path.isdir(naca_name):
                shutil.rmtree(naca_name)
            os.mkdir(naca_name)
            with open(os.path.join(naca_name, naca_name + '.csv'), 'w', newline='\n') as f:
                f.write(content)

    except requests.exceptions.RequestException:
        return None

N_max = 15
# for n in range(N_max):
#     if n < 10 :
#         number = '000'+str(n)
#     elif n < 100:
#         number = '00'+str(n)
#     elif n < 1000:
#         number = '0'+str(n)
#     else :
#         number = str(n)
#
#     scrap('naca'+number)

def get_url(url_father = 'http://airfoiltools.com/airfoil/naca4digit'):
    r = requests.get(url_father)
    r = (r.content).decode()
    r = r.split('\n')
    ind = r.index('<p>NACA 4 digit airfoils in the database</p>')

    list_profile = r[ind + 1].split('</a>')
    link_profile = dict()
    ind += 1

    for row in list_profile:
        # print(row)
        if 'NACA' in row:
            first_ind_link = row.find('href=') + len('href=') + 1
            row = row[first_ind_link:]

            last_ind_link = row.rfind('"')
            link = str(row[:last_ind_link])

            naca_name = 'naca' + row[last_ind_link+len('NACA')+3:]
            # print(row[:last_ind_link])
            # print(row[last_ind_link+len('NACA')+2:])
            # print(naca_name)
            link_profile[naca_name] = "http://airfoiltools.com" + link


    for naca_name, link in link_profile.items():
        r = requests.get(link)
        r = (r.content).decode()
        r = r.split('\n')
        ind = [i for i in range(len(r)) if 'Selig format dat file' in r[i]][0]
        row = [elem for elem in r[ind].split('</a>') if 'Selig format dat file' in elem][0]
        # print(row)
        first_ind_link = row.find('href=') + len('href=') + 1
        row = row[first_ind_link:]
        last_ind_link = row.rfind('"')
        link = "http://airfoiltools.com" + str(row[:last_ind_link])
        # print(f'{naca_name}, {link}')
        # print(r.content)
        link_profile[naca_name] = link

    return link_profile

# print(type(r))
url_dict = get_url()
for naca, url in url_dict.items():
    scrap(naca_name=naca, url=url)


# help(open)

# r1 = requests.get('https://m-selig.ae.illinois.edu/ads/coord/naca1212.dat')
# print(r1.content)
# print(f'status code {r1.status_code}')
# print(type(r1.status_code))

# r = (r1.content).decode()
# print(r)
# print(type(r))

# with open('save.csv', 'w', newline='\n') as f:
#     f.write(r)

# l = list(str(r1.content))
# print(type(str(r1.content)))

# for row in r:
#     print(row)
# with open('save.txt', 'w') as f:
#     f.write(r1.content)