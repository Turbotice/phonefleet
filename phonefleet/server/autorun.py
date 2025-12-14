import urllib.request
import time
def main():
	network = 223
	phone = 197
	port = 8080
	ip = f"192.168.{network}.{phone}"
	url = f"http://{ip}:{port}"

	a = urllib.request.urlopen(f"{url}/status").read()
	if a==b'STOPPED':
		#a = urllib.request.urlopen(f"{url}/start").read()
		pass
	else:
		pass
		#print('Gobannos already running')
	time.sleep(0.1)
	a = urllib.request.urlopen(f"{url}/status").read()
	s = time.asctime(time.gmtime())
	print(s+", "+a.decode())
main()
