import urllib.request
import time

import subprocess
import phonefleet.server.connect as connect


import argparse
global songstart
songstart = "test.mp3"

def gen_parser():
	parser = argparse.ArgumentParser(description="Run program to control Chipiron")
	parser.add_argument('-r',dest='ramp',type=str,default='down')
	parser.add_argument('-all',dest='all',type=bool,default=True)
	parser.add_argument('-n',dest='cycles',type=int,default=1)
	parser.add_argument('-s',dest='song',type=bool,default=False)

	args = parser.parse_args()
	return args

def command(cmd):
        return urllib.request.urlopen(f"{url}/usb-cmd/c{cmd}").read()


def ramp(cmd=10,song=False):
	ip = connect.get_ip(protocol='self')
	port = 8080
	url = f"http://{ip}:{port}"

	a = urllib.request.urlopen(f"{url}/start").read()

	if song:
		subprocess.Popen(["play", songstart],text=True)
	time.sleep(30)
        a = command(cmd)
        
	time.sleep(210)
	a = urllib.request.urlopen(f"{url}/stop").read()

	time.sleep(0.1)
	a = urllib.request.urlopen(f"{url}/status").read()
	print(a)

def up(song=False):
        a = ramp(cmd=90,song=song)

def down(song=False):
        a = ramp(cmd=10,song=song)

def full(args,song=False):
        #start by descending first
        a = ramp(cmd=90,song=song)

        time.sleep(5)
        #then ascend
        a = ramp(cmd=10)

def main(args):
        if args.all == True:
                for i in range(args.cycles):
                        full(args,song=args.song)
        elif args.type == 'ramp':
                if args.ramp == 'up':
                        up(song=args.song)
                elif args.ramp == 'down':
                        down(args,song=args.song)
        elif args.type == 'steps':
                values = [11,12,15,20,30]
                steps(values,T=60*5)
        else:
                print('-t argument not recognized')
                        
if __name__=='__main__':
        args = gen_parser()
        main(args)
