import urllib.request
import time
import subprocess
import phonefleet.server.connect as connect

#write in a log file the following informations
#time
#battery level
#whoami
#ip adresses
#adb on/off
#
def main(T=300,protocol='self'):
	ip = connect.get_ip(protocol=protocol)
	port = 8080
	url = f"http://{ip}:{port}"

	a = urllib.request.urlopen(f"{url}/status").read()
	if a==b'STOPPED':
		a = urllib.request.urlopen(f"{url}/start").read()
		pass
	else:
		print('Gobannos already running')
	time.sleep(0.1)
	a = urllib.request.urlopen(f"{url}/status").read()
	s = time.asctime(time.gmtime())
	print(s+", "+a.decode())

	time.sleep(T)
	a = urllib.request.urlopen(f"{url}/stop").read()
	time.sleep(0.1)
	a = urllib.request.urlopen(f"{url}/status").read()
	s = time.asctime(time.gmtime())
	print(s+", "+a.decode())

if __name__=='__main__':
	main()
