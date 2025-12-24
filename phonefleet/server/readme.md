Install F-Droid
From there install termux and termux:API
> Mandatory to have access to the files !! (in particular on the Redmis)

How to ssh to the Phone
in the phone, open Termux and install ssh 
pkg install openssh
pkg install termux-services

Enable ssh-agent


type sshd to check that ssh is running
type whoami to get the username
type passwd to change the password, set the usual one

In a terminal on the distant host, sharing the same local network, run the command
ssh u0_a213@192.168.223.197 -p 8022
where u0_a213 : phone identifier, 

password : usual
specify the port


type termux-wake-lock to keep running termux in the background

Add an automatic script in the boot :
nano ~/.bashrc
sshd
termux-wake-lock


other related package to install
pkg install cronie
pkg install android-tools
pkg install nmap
pkg install termux-api
pkg install termux-am-socket
pkg install python

In python
python -m pip install numpy



maintain ssh open whatever:
https://samutz.com/docs/books/tech/page/setting-up-ssh-on-termux
If need to reinstall Termux, you may need this command :
ssh-keygen -R [192.168.223.219]:8022

on the phone make a git repository in ~/
for the authentification go here:
https://allahisrabb.hashnode.dev/link-termux-to-your-github-account-on-android-using-ssh-keys

run 
pkg install git

termux-setup-storage

then 
git clone git@github.com:Turbotice/phonefleet.git

install python & useful packages
https://github.com/termux/termux-packages/discussions/19126

For numpy :
MATHLIB=m LDFLAGS="-lpython3.12" pip3 install --no-build-isolation --no-cache-dir numpy -vv


Crontab
pkg install cronie termux-services
sv-enable crond
crontab -e


Make a phone as a server
Unlock adb commands :
authorise ADB over Wifi
Identify the port (random value, probably change over time)
execute :
adp pair ip_adress:port_pairing
Then, give the id displayed on the phone
execute :
adb connect ip_adress:port_toconnect
Beware, the port number is different !
an adb device has been created, you can run classical adb command, for instance
adb shell input keyevent 26 : unlock the screen
adb shell input keyevent 82 : unlock the screen

