BoxCo_Client 1.7

Librairies
-Grove_LoRa_433MHz_and_915MHz_RF-master.zip
-DHT-sensor-library

What does it do ?
Sends a frame to the server via the Grove loRa Radio module and the RH_RF95.h
Connect RX to pin6 and TX to pin5
pMyFrame is used as a pointer via the function createFrame()
The function createFrame(), creates the frame with:
	--> A header, here HBXCO
	--> The server id (can be changed)
	--> The client id (can be changed)
	--> nbValues (depends on the number of values via getNbValues())
	--> The values we want to send
	--> A end, here EBXCO

We now have a termo sensor, a particle sensor (now 9 values), and a Co2 sensor
Each sensor has its own function
To add a sensor, you have to call its function in getValues()

There are python scripts to get the version of the program and set the calibration
of the Co2 sensor

We have a DEBUG variable to enable the ShowSerial and have a "mute" client