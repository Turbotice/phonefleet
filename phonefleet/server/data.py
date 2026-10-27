
import phonefleet.rw_data as rw
import numpy as np
import os
import glob 

global SERVEUR_FOLDER
SERVEUR_FOLDER = '/data/data/com.termux/files/home/storage/downloads/Gobannos/'

def search(folder=None,date=None):
    if folder is None:
        folder = SERVEUR_FOLDER
    if date is None:
        filelist = glob.glob(folder + '*.csv')
    else:
        filelist = glob.glob(folder + f'{date}*.csv') 
    keys = set(['-'.join(os.path.basename(filename).split('-')[:3]) for filename in filelist])
    data = {}    
    for key in keys:
        filelist = glob.glob(folder + f'{key}*.csv') 
        data[key]={}
        data[key]['filelist']=filelist
        data[key]['n']=len(filelist)
    return data

def display(data):
    for key in data.keys():
        print(key, data[key]['n'])
        #print(data[key]['filelist'])
        #print()

def combine(data):
    data['data']={}
    for filename in data['filelist']:
        data['data'].update(load_data(filename))
    return data

def load_data(filename):
    #print(num)
    #phone = int(filename.split('/')[-2])
    num = int(filename.split('-')[1])
    data = rw.read_csv(filename,delimiter=',')
    name = os.path.basename(filename)
    dic = read_data(data,name)
    return dic

def read_data(data,name):
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
    dic = read_raw(data,var)
    return dic
    
def read_gps(data):
    var = 'gps'
    dic = {}
    try:
        float(data[0,0])
        j=0
    except:
        j=1

    dic['t'+var] = np.asarray(data)[j:,0].astype(float)/10**6
    dic[var+'lat'] = (np.asarray(data)[j:,1]).astype(float)
    dic[var+'lon'] = (np.asarray(data)[j:,2]).astype(float)
    dic[var+'elev'] = (np.asarray(data)[j:,3]).astype(float)
    return dic

def read_raw(d,var):
    try:
        d = np.asarray(d)
    except:
        print('dimension does not match ! Skipping')
        return {}
    dic = {}
    try:
        float(d[0,0])
        j=0
    except:
        j=1
        
    dic['t'+var] = np.asarray(d[j:,0]).astype(float)/10**6
    dic['coords']=['x','y','z']
    for i,c in enumerate(dic['coords']):
        dic[var+c]= np.asarray(d[j:,i+1]).astype(float)
    return dic