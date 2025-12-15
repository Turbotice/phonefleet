import glob
import os
import numpy as np
import time
import datetime 
import phonefleet.load as load

from pprint import pprint

global path
global path_android

import platform
ostype = platform.platform()#.split('-')[0]

print(ostype)
ostype = ostype.split('-')[0]

if ostype=='macOS':
    path = 'Test_data_FP3/'
    path_android = 'Test_data_FP3/'
elif ostype=='Linux':
    path = 'datatest/'
    path_android = '/storage/self/primary/Download/Gobannos/'
else:
    print('OS not recognized, add the corresponding path')

def data_stats():
    #load all the files in the path folder
    data = load.load_folder(path)
    data = load.sync_time(data)
    load.stat(data)

    return data

def parse_files(date=None):
    if date==None:
        date = str(datetime.date.today())
    #print(date)
    filelist = glob.glob(path_android+'*'+date+'*.csv')

    experiments={}
    for filename in filelist:
        exp = get_start_time(filename)
        if not exp in experiments:
            print(date,exp)
            experiments[exp]=[]
        experiments[exp].append(filename)

    for exp in experiments.keys():
        data = load.load_files(experiments[exp],header_only=False)
        if data is not None:
            data = load.sync_time(data)
            load.stat(data)
        else:
            print(f'{exp} is empty, no data available')
    #parse  per start time

def get_start_time(filename):
    filename = os.path.basename(filename)
    filename = '20'+filename.split('20')[1]
    date = '-'.join(filename.split('-')[:3])
    date,todaytime = date.split('T')
    #print(date,todaytime)
    return todaytime

if __name__=='__main__':
    parse_files()
#data_stats()





