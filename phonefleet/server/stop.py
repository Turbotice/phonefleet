import urllib.request
import time

import phonefleet.server.connect as connect


def main():
        network,phone = connect.get_ip()
	port = 8080
	ip = f"192.168.{network}.{phone}"
	url = f"http://{ip}:{port}"
	a = urllib.request.urlopen(f"{url}/stop").read()

	time.sleep(0.1)
	a = urllib.request.urlopen(f"{url}/status").read()
	print(a)

if __name__=='__main__':
        main()
