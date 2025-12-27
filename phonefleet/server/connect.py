import subprocess
from pprint import pprint
global port
port = 8080
import csv


def get_my_MAC(protocol='wlan0'):
        out = subprocess.run(['ip','link'],text=True,capture_output=True)
        lines = out.stdout.split('\n')
        output = [lines[i:i+2] for i,line in enumerate(lines) if protocol in line]
        MAC = output.split(' ')[5]
        return MAC

def get_my_id():
        table = read_phone_table()#table with all the registered MAC Adresses
        MAC = get_my_MAC()

        l = [key for key in table.keys() if table[key]['Adresse MAC']==MAC]                
        if len(l)==1:
                print(f'Identifier : {key}')
        else:
                print(f'Phone not found in the table, check that {MAC} is in the list')
        return key
        
def read_phone_table():
        dic={}
        rows = read_csv('PhoneTable.csv')
        header = rows[0][1:]
        for row in rows[1:]:#remove header
                key = row[0]
                dic[key]={}
                for (k,elem) in zip(header,row[1:]):
                        dic[key][k] = elem
        return dic

def read_csv(filename,delimiter=';'):
    rows = []
    with open(filename,'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=delimiter, quotechar='|')
        for row in spamreader:
            rows.append(row)
    return rows


def get_all_ips():
        out = subprocess.run('ifconfig',capture_output=True)
        lines = out.stdout.decode().split('\n')
        protocols = [line.split(':')[0] for line in lines if ':' in line]
        ips= [line.split('inet ')[1].split(' netmask')[0] for line in lines if 'inet ' in line]

        if len(ips)==len(protocols):
                res = {}
                for p,ip in zip(protocols,ips):
                        res[p]=ip
                return res
        else:
                print('parsing of ifconfig non valid, abort')
                return None
        
def get_ip(protocol='self'):
        #possible protocols :
        # wlan : connection through the Wifi
        # self : use internal ip adress, should be more robust
        
        if protocol=='self':
                ip = '127.0.0.1'
        elif protocol=='wlan':
                out = subprocess.run('ifconfig',capture_output=True)
                ip = out.stdout.decode().split(protocol)[1].split('inet ')[1].split(' netmask')[0]
        else:
                print('protocol is not implemented, check phonefleet.server.connect')
                ip = None
        return ip
#                numbers = ip.split('.')
#                network = int(numbers[2])
#                phone = int(numbers[3])
#	return network,phone

def get_local_ip(protocol='wlan'):
        #possible protocols :
        # wlan : connection through the Wifi
	out = subprocess.run('ifconfig',capture_output=True)
	ip = out.stdout.decode().split(protocol)[1].split('inet ')[1].split(' netmask')[0]
	print(ip)
	numbers = ip.split('.')
	network = int(numbers[2])
	phone = int(numbers[3])
	return network,phone


def unlock():
#process to self unlock the redmis
    c=subprocess.run(['adb','shell','input','keyevent','KEYCODE_WAKEUP'],text=True,capture_output=True)
    c=subprocess.run(['adb','shell','input','swipe','200','900','200','300'],text=True,capture_output=True)
    c=subprocess.run(['adb','shell','input','text','01012000'],text=True,capture_output=True)
    c=subprocess.run(['adb','shell','input','keyevent','66'],text=True,capture_output=True)
    
#network,phone = get_ip()


