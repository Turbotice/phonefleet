# phonefleet/acoustic
Python application to generate and record acoustic signals on a pair of smartphone

### requirements

venv


pkg install -y rust binutils 
CARGO_BUILD_TARGET="$(rustc -Vv | grep "host" | awk '{print $2}')" pip install maturin 
 pip install paramiko


### Command line mode


