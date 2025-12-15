import urllib.request
import time
import os
import glob
import numpy as np
from pprint import pprint

global path
path = '../storage/downloads/Gobannos/' #check the path, depends from where the code is run
path = '/storage/self/primary/Download/Gobannos/'
global network
global phone
global port
port = 8080

import subprocess

def get_ip(protocol='wlan'):
	out = subprocess.run('ifconfig',capture_output=True)
	ip = out.stdout.decode().split(protocol)[1].split('inet ')[1].split(' netmask')[0]
	print(ip)
	numbers = ip.split('.')
	network = int(numbers[2])
	phone = int(numbers[3])
	return network,phone
network,phone = get_ip()
print(network,phone)

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
	filelist = np.asarray(filelist)[indices][:4]
	for i,filename in enumerate(filelist):
		stat = {}
		stat['path']=os.path.dirname(filename)
		stat['tm']=tlist[i]
		stat['filename']=os.path.basename(filename)
		stat['size']= os.path.getsize(filename)
		stats.append(stat)
	#display_stat(stats)
	return stats

def display_stat(stats):
	for stat in stats:
		for key in ['filename','tm','size']:
			print(key,stat[key])

def start():
	ip = f"192.168.{network}.{phone}"
	url = f"http://{ip}:{port}"

	a = urllib.request.urlopen(f"{url}/status").read()
	time.sleep(0.1)
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

def stop():
	ip = f"192.168.{network}.{phone}"
	url = f"http://{ip}:{port}"

	a = urllib.request.urlopen(f"{url}/stop").read()
	time.sleep(0.1)
	a = urllib.request.urlopen(f"{url}/status").read()
	s = time.asctime(time.gmtime())
	print(s+", "+a.decode())

def test_active(t=10):
	start()
	time.sleep(t)
	stop()
	time.sleep(1)
	filelist = list_recent_files()
	stats = last_modified(filelist)
	return stats

def test_program():
	stop()
	time.sleep(1)
	tlist = [10,20,60,120,240,360]
	for t in tlist:
		print(f"Test duration : {t}s")
		stats = test_active(t=t)
		print(display_stat(stats))
		print('')

test_program()
