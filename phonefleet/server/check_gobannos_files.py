import urllib.request
import time
import os
import glob
import numpy as np
from pprint import pprint

global path
path = '../storage/downloads/Gobannos/' #check the path, depends from where the code is run

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
	for stat in stats:
		for key in stat.keys():
			print(key,stat[key])
	return stat

def main():
	network = 223
	phone = 197
	port = 8080
	ip = f"192.168.{network}.{phone}"
	url = f"http://{ip}:{port}"

	a = urllib.request.urlopen(f"{url}/status").read()
	if a==b'STOPPED':
		a = urllib.request.urlopen(f"{url}/start").read()
		pass
	else:
		pass
		#print('Gobannos already running')
	time.sleep(0.1)
	a = urllib.request.urlopen(f"{url}/status").read()
	s = time.asctime(time.gmtime())
	print(s+", "+a.decode())

def test_active():
	filelist = list_recent_files()
	last_modified(filelist)

test_active()
