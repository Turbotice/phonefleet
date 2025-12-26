import urllib.request
import time


import phonefleet.server.connect as connect

def get():
        dic = {}
        ip,status = main()
        dic['status']=status
        dic['default_ip']=ip
        return dic

def main(display=False):
	ip = connect.get_ip(protocol='self')
	port = 8080
	if display:
        	print(ip)
	url = f"http://{ip}:{port}"
	a = urllib.request.urlopen(f"{url}/status").read()
        if display:
        	print(a)
        status = a.decode()
        return ip,status

if __name__=='__main__':
        main(display=True)
