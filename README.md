# phonefleet
Python application to control remotely the sensors of a smartphone fleet


#### Command line mode #####

1. Connect all devices to the same local network (over Wifi)
2. Recommended : allocate to each smartphone a static IP, which simplify the identifications of the devices.
3. All address should be of the form 192.168.X.YY, where X is the subnet mask, and it must be the same for all devices. YY is the network number of the device.
4. Open a terminal and in the phonefleet path run mobile.py, by typing : python3 mobile.py
mobile.py implements all basics functions to interact with the phone. It is minimalist, but you may take few minutes to get the syntax.
	- network : specify the subnet mask, and type the number X
	- phones : specify the list of phone to control, update the active phonelist.
	- status :  check the connection of all elements of phonelist.
	- start : start an acquisition on all elements of phonelist
	- stop : stop current acquisition on all elements of phonelist.
	- ls phone : display all gobannos files in the specified phone number
	- pull phone imin:imax : pull gobannos files from the phone number, from imin index to imax index (included)
	- save : interactive command to retrieve one of last files from all the phonelist.
	- save_all : retrieve all gobannos files from the phonelist.
	

#### Web interface mode #####
