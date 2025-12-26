import urllib.request
import time
import subprocess
import phonefleet.server.connect as connect
import phonefleet.server.status as status

import phonefleet.server.termux_cmd as termux

from pprint import pprint
import argparse

def gen_parser():    
    parser = argparse.ArgumentParser(description="Produce activity reports")
    parser.add_argument('-test_gobannos', dest='gobannos', type=bool,default=False,help='Boolean, if true, test Gobannos connection')
    parser.add_argument('-mailit', dest='mailit', type=bool,default=False,help='Boolean, send the report by email if True')
    parser.add_argument('-email', dest='email', type=str,default="turbots.pmmh@gmail.com",help='email adress of the recipient')
    parser.add_argument('-filename', dest='filename', type=str,default="report.txt",help='Name of the file to save the report')
    parser.add_argument('-cmd', dest='cmd', type=bool,default=False,help='Boolean, if True, the program is executed by an external console (such as crontab)')

#    print(parser)   
    args = parser.parse_args()
    #print(args)
    return args


#write in a log file the following informations
#time
#battery level
#whoami
#ip adresses
#adb on/off
#Zerotier running
#Gobannos running
#last saved Gobannos filename (with size)

def full_report(header=True,test_gobannos=False):
        report = {}

        #following steps required that termux running
        try:
                report['time'] = termux.get_time()
                report['battery'] = termux.get_battery()
                report['id'] = termux.get_whoami()
                report['network'] = termux.get_all_ips()
        except:
                print('Failed to execute basic Termux command. Check that termux is running')

        #following steps required adb, may fall off
        try:
                report['adb'] = termux.get_adb_status()
                report['apps'] = termux.get_apps_running()
        except:
                print('adb link may be broken, check that adb is running and device is connected')
                
        # test Gobannos connexion, only works if screen is on
        if test_gobannos:
                report['gobannos'] = status.get()

        if header:
                print('Subject: Activity Report FP3 \n')
                print(report['time']['date']+'\n')
        pprint(report)

        return report

def add_header(report):
        print('Subject: Activity Report FP3 \n')
        print(report['time']['date']+'\n')
        
def cat_report(report,header=True):
        if header:
                add_header(report)     
        pprint(report)
        
def save_report(report,filename='report.txt'):
        with open(filename, "w") as f:
                print('Subject: Activity Report FP3 \n',file=f)
                print(report['time']['date']+'\n',file=f) # must exist in the file !
                pprint(report,stream=f)

def short_report():
        report = full_report()
        #sort the report to keep only some keys

def mail_report(filename,email='stephane.perrard@espci.fr'):
        try:
                with open(filename, "rb") as f:
                        subprocess.run(["msmtp", email],stdin=f,capture_output=True,text=True,check=True)
        except subprocess.CalledProcessError as e:
                print("Command failed")
                print("stderr:", e.stderr)
                
def main(args):
	report = full_report()
        save_report(report,filename=args.filename)
	
        if args.mailit:
                mail_report(args.filename,email=args.email)

if __name__=='__main__':
        args = gen_parser()
	main(args)
