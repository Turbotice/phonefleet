import urllib.request
import time
def main():
	network = 223
	phone = 197
	port = 8080
	ip = f"192.168.{network}.{phone}"
	url = f"http://{ip}:{port}"
	a = urllib.request.urlopen(f"{url}/stop").read()

	time.sleep(0.1)
	a = urllib.request.urlopen(f"{url}/status").read()
	print(a)
main()
