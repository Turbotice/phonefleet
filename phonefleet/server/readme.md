Install F-Droid
From there install termux and termux:API
> Mandatory to have access to the files !! (in particular on a Redmi)

———— How to ssh to the Phone ————
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
specify the port (8022)

——— Keep Termux running in the background ———
type termux-wake-lock to keep running termux in the background
Add an automatic script in the boot :
nano ~/.bashrc
sshd
termux-wake-lock

maintain ssh open whatever:
https://samutz.com/docs/books/tech/page/setting-up-ssh-on-termux
If need to reinstall Termux, you may need this command :
ssh-keygen -R [192.168.223.219]:8022



———— Other packages to install —————
pkg install android-tools
pkg install nmap
pkg install termux-api
pkg install termux-am-socket

install python & useful packages
https://github.com/termux/termux-packages/discussions/19126
For numpy, you may need : 
MATHLIB=m LDFLAGS="-lpython3.12" pip3 install --no-build-isolation --no-cache-dir numpy -vv


——— Set up git ————
On the phone make a git repository in ~/, type
mkdir ~/git

for setting up the authentification go here:
https://allahisrabb.hashnode.dev/link-termux-to-your-github-account-on-android-using-ssh-keys

Install git :
pkg install git

to access the phone storage, type : 
termux-setup-storage

then 
git clone git@github.com:Turbotice/phonefleet.git

——— Set up crontab ——
Crontab can be used to run automatically scripts on the phone

pkg install cronie termux-services
sv-enable crond
crontab -e


———— Use the phone as a distant server ———
Following steps open an adb channel on the phone, to manipulate screen state, to be tested on a long term distant access
Use the wifi connection, unclear it would work through internet


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
adb shell input keyevent 82 : unlock the screen
adb shell input keyevent 26 : lock the screen

To move to a known port, you can run :
adb tcpip 5555
To show the device list, type
adb devices
Then, you should have two devices in the list.
You can run 
adb kill-server
And restart adb by running :
adb devices
You should now have exactly one device in the list, which will be used by the crontab to unlock the screen before running Gobannos (work on both FP3 & FP4)
