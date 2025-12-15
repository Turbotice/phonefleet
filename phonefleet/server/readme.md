Install F-Droid
From there install termux and termux:API
> Mandatory to have access to the files !!
other related:
pkg termux-api
pg install cronie

Connect to the Phone : 
in the phone, open Termux,
type sshd to check that ssh is running
type whoami to get the username
password : usual
specify the port
ssh u0_a213@192.168.223.197 -p 8022

maintain ssh open whatever:
https://samutz.com/docs/books/tech/page/setting-up-ssh-on-termux
If need to reinstall Termux, you may need this command :
ssh-keygen -R [192.168.223.219]:8022

on the phone make a git repository in ~/
for the authentification go here:
https://allahisrabb.hashnode.dev/link-termux-to-your-github-account-on-android-using-ssh-keys

run 
pkg install git

then 
git clone git@github.com:Turbotice/phonefleet.git

install python & useful packages
https://github.com/termux/termux-packages/discussions/19126

For numpy :
MATHLIB=m LDFLAGS="-lpython3.12" pip3 install --no-build-isolation --no-cache-dir numpy -vv