BoxCo_Server 1.1

Librairies
-Grove_LoRa_433MHz_and_915MHz_RF-master.zip
-RTCLib 1.8.0 from Adafruit

What does it do ?
Receive the frame from the client via the Grove loRa Radio module and the RH_RF95.h
Puts the frame in a buffer and then checks if the frame is adressed to itself
using the decodeFrame() function
Replaces decodeFrame() by parseFrame()
Puts only the values on the card, and creates a different file for each client

This code is to use with a MEGA 2560 with the following modifications
--> pin 10 shield --> pin 53 MEGA - chipselect becoming 53
--> pin 11 shield --> pin 51 MEGA
--> pin 12 shield --> pin 50 MEGA
--> pin 13 shield --> pin 52 MEGA

--> loRa RX --> pin 2
--> loRa TX --> pin A8 (62)
