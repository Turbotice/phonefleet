import urllib.request
import time


import phonefleet.server.connect as connect


import argparse

def gen_parser():
	parser = argparse.ArgumentParser(description="Run program to control Chipiron")
	parser.add_argument('-r',dest='ramp',type=str,default='down')
	parser.add_argument('-all',dest='all',type=bool,default=False)

def up():
	ip = connect.get_ip(protocol='self')
	port = 8080
	url = f"http://{ip}:{port}"

	a = urllib.request.urlopen(f"{url}/start").read()

	time.sleep(30)
	a = urllib.request.urlopen(f"{url}/usb-cmd/c90").read()

	time.sleep(210)
	a = urllib.request.urlopen(f"{url}/stop").read()

	time.sleep(0.1)
	a = urllib.request.urlopen(f"{url}/status").read()
	print(a)

if __name__=='__main__':
        main()
