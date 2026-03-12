# How to Connect to an Android smartphone from a distant device

On a local network, make sure your two devices are connected to the same Wi-Fi. It can be the hotspot shared by the target Android smartphone

On a global network, first connect the two devices to the same private network, using zerotier.
Both devices should have an ip address starting with 172.28

### Connect to the FP5

Start ssh agent :
on the FP5 type
```shell
sshd
```

To identify its ip, either start Gobannos, it will display one functionning IP, or in the termux command line :
```shell
ifconfig
```
To identify the phone identifier 
```shell
whoami
```
If will return the phoneid.

On local network :
```shell
ssh phoneid@local_ip -p 8022
```

Everywhere (zerotier) :
```shell
ssh phoneid@ip_address -p 8022
```
mdp : usual

On your phone, you can also run 
```shell
nmap -PR ip_base.0/24
```
to identify the ip of the FP5

