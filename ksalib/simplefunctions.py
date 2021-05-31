import requests
import os
import re
from datetime import datetime

def get_filename_from_cd(cd):

    #Get filename from content-disposition

    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]

def download(url,path):
    r = requests.get(url, allow_redirects=True)
    filename = get_filename_from_cd(r.headers.get('content-disposition'))
    open(os.path.join(path,filename), 'wb').write(r.content)

def try_find(a):
    if a is None:
        pass
    else:
        a = a.text
        if a is None:
            pass
        else:
            a = a.strip()
    return a

def to_http(link):
    if link.startswith('https'):
        link = 'http' + link[len('https'):]
    return link

# "year-month-day hour:minute:second"
def str_to_time(s):
    time = s.split(' ')
    time[0] = time[0].split('-')
    time[1] = time[1].split(':')
    for i in range(2):
        for j in range(3):
            time[i][j] = int(time[i][j])
    return datetime(year=time[0][0], month=time[0][1], day=time[0][2],
                    hour=time[1][0], minute=time[1][1], second=time[1][2])
