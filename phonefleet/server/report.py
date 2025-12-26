import urllib.request
import time
import subprocess
import phonefleet.server.connect as connect
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

def full_report():
        report = {}
        report.update(termux.get_time())

        report.update(termux.get_battery())

        report.update(termux.get_whoami())

        report.update(termux.get_all_ips())

        report.update(termux.get_adb_status())

        pprint(report)

        return report

def short_report():
        report = full_report()
        #sort the report to keep only some keys
        
        
def main():
	out = full_report()


if __name__=='__main__':
	main()
