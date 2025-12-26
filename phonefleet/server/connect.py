import subprocess
from pprint import pprint
global port
port = 8080

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
                print('parsing of ifconfig non valid, abort)
                return None
        
def get_ip(protocol='wlan'):
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

#network,phone = get_ip()


