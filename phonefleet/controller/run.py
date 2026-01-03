import urllib.request
import time


import phonefleet.server.connect as connect


import argparse

def gen_parser():
	parser = argparse.ArgumentParser(description="Run program to control Chipiron")
	parser.add_argument('-r',dest='ramp',type=str,default='down')
	parser.add_argument('-all',dest='all',type=bool,default=False)

def ramp(cmd=10):
	ip = connect.get_ip(protocol='self')
	port = 8080
	url = f"http://{ip}:{port}"

	a = urllib.request.urlopen(f"{url}/start").read()

	time.sleep(30)
	a = urllib.request.urlopen(f"{url}/usb-cmd/c{cmd}").read()

	time.sleep(210)
	a = urllib.request.urlopen(f"{url}/stop").read()

	time.sleep(0.1)
	a = urllib.request.urlopen(f"{url}/status").read()
	print(a)

def up():
        a = ramp(cmd=90)

def down():
        a = ramp(cmd=10)

def full():
        #start by descending first
        a = ramp(cmd=10)

        time.sleep(5)
        #then ascend
        a = ramp(cmd=90)

def main(args):
        if args.all == True:
                full()
        else:
                if args.ramp == 'up':
                        up()
                elif args.ramp == 'down':
                        down()
                        
if __name__=='__main__':
        args = gen_parser()
        main(args)
