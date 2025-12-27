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


to access the phone storage, type : 
termux-setup-storage
You wil need to grant access to your files to Termux

——— Keep Termux running in the background ———
to keep running termux in the background, type 
termux-wake-lock 
Add an automatic script in the boot :
nano ~/.bashrc
sshd
termux-wake-lock

maintain ssh open whatever:
https://samutz.com/docs/books/tech/page/setting-up-ssh-on-termux
If need to reinstall Termux, you may need this command to reboot keys :
ssh-keygen -R [192.168.223.219]:8022



———— Other packages to install —————
pkg install android-tools nmap termux-api termux-tools root-repo
pkg install termux-am-socket #does not exist on the redmi
apt upgrade


install python & useful packages (take few minutes and need a good connection, size ~1GB)

Detailed instructions here :
https://github.com/termux/termux-packages/discussions/19126


pkg upgrade
pkg install git python build-essential cmake ninja libopenblas libandroid-execinfo patchelf binutils-is-llvm
pip3 install setuptools wheel packaging pyproject_metadata cython meson-python versioneer
Check python version :
python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'
MATHLIB=m LDFLAGS="-lpython3.12" pip3 install --no-build-isolation --no-cache-dir numpy -vv


——— Set up git ————

On the phone make a git repository in ~/, type
mkdir ~/git
Install git (already done above) :
pkg install git

for setting up the authentification go here:
https://allahisrabb.hashnode.dev/link-termux-to-your-github-account-on-android-using-ssh-keys
ssh-keygen -t ed25519 -C stephane.perrard@espci.fr
cat ~/.ssh/id_ed25519.pub

copy it to your ssh github keys

eval $(ssh-agent -s)
ssh-add ~/.ssh/id_ed25519
ssh -T git@github.com

then 
git clone git@github.com:Turbotice/phonefleet.git

——— Set up crontab ——
Crontab can be used to run automatically scripts on the phone

pkg install cronie termux-services
sv-enable crond #sometimes get an error, unclear why. See https://github.com/termux/termux-services
crontab -e

#copy the default crontab file 



———— Use the phone as a distant server ———

The following steps open an adb channel on the phone to manipulate screen state.
The method still need to be tested on a long term distant access
Use the wifi connection, unclear it would work through internet -> yes if the phone is properly set up first


Unlock adb commands :
in Parameter/developer options, authorise ADB over Wifi
Identify the port (random value, probably change over time)
execute :
adp pair ip_adress:port_pairing

Then, give the id displayed on the phone
execute :
adb connect ip_adress:port_toconnect
Beware, the port number is different !
an adb device has been created, you can run classical adb command, for instance

Unlock the screen (FP3 & FP4)
adb shell input keyevent 82

Unlock the screen (RD10A)
adb shell input keyevent 82


adb shell input keyevent 26 : lock the screen

To move to a known port, you can run :
adb tcpip 5555
To show the device list, type
adb devices
Then, you should have one or two devices in the list, one may be offline

Then run
adb kill-server
And restart adb by running :
adb devices
You should now have exactly one device in the list, of the type emulator-5554
adb will be used by the crontab to unlock the screen before running Gobannos (work on FP3 & FP4, RD10A)

_______ set up a mail sender on the phone ————

Follow :
https://www.reddit.com/r/termux/comments/1mt3xi1/sending_email_from_termux_via_cli/

And adapt it to ESPCI server
Exemple configuration file in /phonefleet/phonefleet/server


cat report_2026_12_26_FP3.txt | msmtp --debug antonin.eddi@espci.fr jishen.zhang@espci.fr stephane.perrard@espci.fr
