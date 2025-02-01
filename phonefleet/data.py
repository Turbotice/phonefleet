import urllib
import re
from pprint import pprint
import numpy as np
import time

import icewave.tools.rw_data as rw

import phonefleet.connect as connect
global port
port = 8080

global savefolder
savefolder = ''

def list_files(phone,prefix='',date=''):
    ip = connect.get_adress(phone)
    a = urllib.request.urlopen(f"http://{ip}:{port}/list-files").read()
    s = a.decode('utf-8')
    filelist = s[1:-1].split(', ')

    if len(prefix)>0:
        if date=='':
            time.today()
        rx = re.compile(f'-{date}T*')
        filelist = list(filter(rx.search, filelist)) 

    pprint(f"Phone {phone}, number of files : {len(filelist)}")
    #files[phone]=filelist
    return filelist

def save_files_onedate(phone,date,imin=0):
    dategob = f'2025-{date[:2]}-{date[2:]}'
    filelist = list_files(phone,prefix='-',date=dategob)

    for i,filename in enumerate(filelist):
        if i>=0:
            print(i,filename)
            data = dataphone.get_file(phone,filename)
            print(data['raw'].keys())
            name = list(data['raw'].keys())[0]
            filename = savefolder+name+'.pkl'
            rw.write_csv(filename,data['raw'][name])

def get_files(phone,filelist):
    data = {}
    data['raw'] = {}
    ip = connect.get_adress(phone)

    for i,filename in enumerate(filelist):
        print(i,filename)
        a = urllib.request.urlopen(f"http://{ip}:{port}/get-file/"+filename).read()
        name = filename.split('.')[-2]
        data['raw'][name] = a
    return data

def get_file(phone,filename):
    ip = connect.get_adress(phone)
    data = {}
    data['raw'] = {}
    a = urllib.request.urlopen(f"http://{ip}:{port}/get-file/"+filename).read()
    name = filename.split('.')[-2]

    dic = decode_data(a,name)
    data['raw'][name] = dic
    return data

def decode_data(data,name):
    if 'gps' in name:
        dic = read_gps(data)
        return dic
    elif 'accelerometer' in name:
        var='a'
    elif 'gyroscope' in name:
        var='g'
    elif 'magnetic' in name:
        var='m'
    else:
        print('Data type not recognized')
        print(name)
        return None
    dic = read_timeserie(data,var)
    return dic
    
def read_gps(data):
    d = decode(data)
    print(d.shape)
    var = 'gps'
    dic = {}
    dic['t'+var] = d[:,0]
    dic[var+'lat'] = d[:,1]
    dic[var+'lon'] = d[:,2]
    dic[var+'elev'] = d[:,3]
    return dic

def decode(data):
    d = data.decode('utf-8')
    lines = d.split('\n')
    d = np.asarray([line.split(', ')[:-1] for line in lines]).astype(float)
    return d

def read_timeserie(data,var):
    d = decode(data)
    print(d.shape)
    dic = {}
    dic['t'+var] = d[:,0]
    dic[var+'x' ]= d[:,1]
    dic[var+'y'] = d[:,2]
    dic[var+'z'] = d[:,3]
    return dic