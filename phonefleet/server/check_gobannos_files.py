import urllib.request
import time
import os
import glob
import numpy as np
from pprint import pprint
import phonefleet.tests as tests

global path
path = '/storage/self/primary/Download/Gobannos/' #check the path, depends from where the code is run

def list_recent_files(Dt=3600):#last 1h
	filelist = glob.glob(path+'*.csv')
	print(f"Total number of files : ~{len(filelist)}")
	tnow = time.time()
	
	recentfiles = [filename for filename in filelist if (tnow-os.path.getmtime(filename))<Dt]
	print(f"Total number of recent files : ~{len(recentfiles)}")
	return recentfiles

def last_modified(filelist):
	tnow = time.time()
	tlist =  np.asarray([tnow-os.path.getmtime(filename) for filename in filelist])
	indices = np.argsort(tlist)
	tlist = tlist[indices]
	stats = []
	filelist = np.asarray(filelist)[indices]
	for i,filename in enumerate(filelist):
		stat = {}
		stat['path']=os.path.dirname(filename)
		stat['tm']=tlist[i]
		stat['filename']=os.path.basename(filename)
		stat['size']= os.path.getsize(filename)
		stats.append(stat)
	return stats

def display_stat(stats):
	for stat in stats:
		for key in ['filename','tm','size']:
			print(key,stat[key])

def test_last_data():
	filelist = list_recent_files(Dt=3600)
	stats = last_modified(filelist)
	display_stat(stats)

if __name__=='__main__':
	tests.parse_files()
#	test_last_data()
