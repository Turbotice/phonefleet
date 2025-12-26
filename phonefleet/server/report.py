import urllib.request
import time
import subprocess
import phonefleet.server.connect as connect
import phonefleet.server.status as status

import phonefleet.server.termux_cmd as termux

from pprint import pprint
#write in a log file the following informations
#time
#battery level
#whoami
#ip adresses
#adb on/off
#Zerotier running
#Gobannos running
#last saved Gobannos filename (with size)

def full_report(mail=True):
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
        #report['gobannos'] = status.get()

        if mail:
                print('Subject: Activity Report FP3 \n')
                print(report['time']['date']+'\n')
        pprint(report)

        return report

def short_report():
        report = full_report()
        #sort the report to keep only some keys

def mail_report(filename,email='stephane.perrard@espci.fr'):
        out = subprocess.run(['cat',filename,'|','msmtp','--debug',email],capture_output=True)
        print(out.stdout.decode())
        
def main():
	out = full_report()


if __name__=='__main__':
	main()
