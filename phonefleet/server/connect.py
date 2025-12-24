import subprocess

global network
global phone
global port
port = 8080

def get_ip(protocol='wlan'):
	out = subprocess.run('ifconfig',capture_output=True)
	ip = out.stdout.decode().split(protocol)[1].split('inet ')[1].split(' netmask')[0]
	print(ip)
	numbers = ip.split('.')
	network = int(numbers[2])
	phone = int(numbers[3])
	return network,phone

network,phone = get_ip()


