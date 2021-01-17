import requests
import os
import re

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