/**********************************************************************************
* BoxCo_Client then sends it to server through Lora
* 
* 
* Cléis Benoit-Gonin - PMMH Lab - 2021/07/02 
* 
* Thierry Darnige - PMMH Lab - Modified 2021/11/08
* Thierry Darnige - PMMH Lab - Modified 2025/03/14
* Thierry Darnige - PMMH Lab - Modified 2025/11/18
* 
**********************************************************************************/

#include <Arduino.h>
#include <RH_RF95.h>
#include <DHT.h>
#include <SoftwareSerial.h>
#include <DFRobot_AirQualitySensor.h>

//Constants to be changed
//------------------------------------------
//#define DEBUG
#define ClientVersion "BoxCo_Client 3.0"
#define SERVERID 1
#define CLIENTID 3
//#define TIMEOUT 1000 //millisecond
//#define MAX_RESEND 2
#define SEND_DATA_DELAY 4000 //millisecond
#define SEND_DATA_RANDOM 1000 //millisecond
//-------------------------------------------

#ifdef __AVR__
    #include <SoftwareSerial.h>
    SoftwareSerial SSerial(5, 6); // RX, TX
    //SoftwareSerial SSerial(0, 1); // RX, TX
    #define COMSerial SSerial
    #define Serial Serial

    RH_RF95<SoftwareSerial> rf95(COMSerial);
#endif

#ifdef ARDUINO_SAMD_VARIANT_COMPLIANCE
    #define COMSerial Serial1
    #define Serial SerialUSB

    RH_RF95<Uart> rf95(COMSerial);
#endif

#ifdef ARDUINO_ARCH_STM32F4
    #define COMSerial Serial
    #define Serial SerialUSB

    RH_RF95<HardwareSerial> rf95(COMSerial);
#endif

#ifdef ARDUINO_UNOR4_MINIMA
    #define COMSerial Serial
    #define Serial SerialUSB

    RH_RF95<HardwareSerial> rf95(COMSerial);
#endif
 

#define HEADER "HBXCO"
#define ENDER "EBXCO"

// Pin Led
#define PINLED 3

// DHT22 Thermo sensor
#define DHTPIN 2 // Use the digital pin2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

//Particle sensor
#define I2C_ADDRESS    0x19
DFRobot_AirQualitySensor particle(&Wire ,I2C_ADDRESS);


#define LENG 31   //0x42 + 31 bytes equal to 32 bytes
uint8_t buf[LENG];
uint16_t PM01Value=0;          //define PM1.0 value of the air detector module
uint16_t PM2_5Value=0;         //define PM2.5 value of the air detector module
uint16_t PM10Value=0;         //define PM10 value of the air detector module
uint16_t PM0_3Value=0;
uint16_t PM0_5Value=0;
uint16_t PM1_0Value=0;
uint16_t PM2_5uValue=0;
uint16_t PM5_0Value=0;
uint16_t PM10_0Value=0;
//SoftwareSerial PMSerial(10, 11); // RX, TX
//SoftwareSerial PMSerial(8, 11); // RX, TX


//CO2 sensor
SoftwareSerial CO2Serial(12, 13); // RX, TX
unsigned char getDensity[9] = {0xFF,0x01,0x86,0x00,0x00,0x00,0x00,0x00,0x79}; //Read the gas density command /Don't change the order
long CO2;
unsigned char setCalibration[9] = {0xFF, 0x01, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00, 0x78};


void setup() {
    Serial.begin(115200);
    #ifdef DEBUG
      //Serial.println("RF95 client test.");
    #endif
    
    //PMSerial.setTimeout(1500);

/*  if (!rf95.init()) {
        Serial.println("init failed");
        while (1);
    }
*/
    // Set up DHT
    dht.begin();

    // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

    // The default transmitter power is 13dBm, using PA_BOOST.
    // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then
    // you can set transmitter powers from 5 to 23 dBm:
    //rf95.setTxPower(13, false);

    //rf95.setFrequency(868.0);

/**
  Sensor initialization is used to initialize IIC, which is determined by the communication mode used at this time.
*/
  while(!particle.begin())
  {
    Serial.println("NO Devices !");
    delay(1000);
  }
  Serial.println("sensor begin success!");
  delay(1000);
/**
  Get sensor version number
*/
  uint8_t version = particle.gainVersion();
  Serial.print("version is : ");
  Serial.println(version);
  delay(1000);


    pinMode(PINLED, OUTPUT);
}

void loop() {
    #ifdef DEBUG
      Serial.println("Sending to rf95_server");
    #endif

    String values = getValues();

    //Gets the number of values
    int nbvalues = getNbValues(values);
    #ifdef DEBUG
      //Serial.println(nbvalues);
    #endif

    //Create the frame
    char pMyFrame[RH_RF95_MAX_MESSAGE_LEN];
 
    //To check if the char is empty
    if (pMyFrame != NULL){
      memset(pMyFrame, '\0', RH_RF95_MAX_MESSAGE_LEN);
      createFrame(pMyFrame, HEADER, ENDER, SERVERID, CLIENTID, values, nbvalues); //function to create the frame
    }

    //Sending the frame to the server
    if (!rf95.init()) {
        Serial.println("init failed");
    }
    else
    {
        rf95.setFrequency(868.0);
        rf95.send((uint8_t*) pMyFrame, strlen(pMyFrame));
        digitalWrite(PINLED, HIGH);
        rf95.waitPacketSent();
        #ifdef DEBUG
          Serial.println(pMyFrame);
        #endif
        digitalWrite(PINLED, LOW);
    
       
        delay(SEND_DATA_DELAY + random(-SEND_DATA_RANDOM, SEND_DATA_RANDOM));
    
        
    
        // Get commands from the serial line
        byte inChar;
        inChar = Serial.read();
        getCommand(inChar);
    }
}

void getCommand(byte command){
  // Set the date
    if   (command == 'c')
    {
      Serial.println(F("CO2 initialized"));
      CO2Serial.write(setCalibration, 9);
    }

    //Get the firmware Version
    if (command == 'v')
    {
      String acquString = String("Version : ");
      acquString += String(ClientVersion);
      acquString += String("\n");
      Serial.write(acquString.c_str());
    }
}

uint8_t parseFrame(char* pFrame){

  char tmpBuf[10];

  //Look for the Header
  int ibuf = 0;
  int iframe = 0;
  while(pFrame[iframe] != '\t'){
    tmpBuf[ibuf] = pFrame[iframe];
    iframe++;
    ibuf++;
  }
  tmpBuf[ibuf] = '\0';
  if (strcmp(HEADER, tmpBuf) != 0){
    return 0;
  }
  //Serial.println(F("Good header"));

  //Look for ServerId
  ibuf = 0;
  iframe ++;
  //tmpBuf = "";
  while(pFrame[iframe] != '\t'){
    tmpBuf[ibuf] = pFrame[iframe];
    iframe++;
    ibuf++;
  }
  tmpBuf[ibuf] = '\0';
  if (SERVERID != atoi(tmpBuf)){
    return 0;
  }
  //Serial.println(F("Good server"));
  
  //Look for ClientId
  ibuf = 0;
  iframe ++;
  //tmpBuf = "";
  while(pFrame[iframe] != '\t'){
    tmpBuf[ibuf] = pFrame[iframe];
    iframe++;
    ibuf++;
  }
  tmpBuf[ibuf] = '\0';
  if (CLIENTID != atoi(tmpBuf)){
    return 0;
  }
  //Serial.println(F("Good client"));

  //Look for the Ender
  /*ibuf = 0;
  iframe ++;
  while(pFrame[iframe] != '\t'){
    tmpBuf[ibuf] = pFrame[iframe];
    iframe++;
    ibuf++;
  }
  tmpBuf[ibuf] = '\0';
  if (strcmp(ENDER, tmpBuf) != 0){
    return 0;
  }*/
  //Serial.println(F("Good ender"));

  return 1;
}

String getValues(){
  return getHumTemp() + getParticleValues() + getCO2Value(CO2);
}

String getHumTemp(){
  return String(dht.readHumidity()) +'\t'+ String(dht.readTemperature()) +'\t';
}

String getParticleValues()
{
  //PMSerial.begin(9600);


  PM01Value=particle.gainParticleConcentration_ugm3(PARTICLE_PM1_0_STANDARD); //count PM1.0 value of the air detector module
  PM2_5Value=particle.gainParticleConcentration_ugm3(PARTICLE_PM2_5_STANDARD);//count PM2.5 value of the air detector module
  PM10Value=particle.gainParticleConcentration_ugm3(PARTICLE_PM10_STANDARD); //count PM10 value of the air detector module
  //Serial.println(F("It's working"));
  PM0_3Value=particle.gainParticleNum_Every0_1L(PARTICLENUM_0_3_UM_EVERY0_1L_AIR);
  PM0_5Value=particle.gainParticleNum_Every0_1L(PARTICLENUM_0_5_UM_EVERY0_1L_AIR);
  PM1_0Value=particle.gainParticleNum_Every0_1L(PARTICLENUM_1_0_UM_EVERY0_1L_AIR);
  PM2_5uValue=particle.gainParticleNum_Every0_1L(PARTICLENUM_2_5_UM_EVERY0_1L_AIR);
  PM5_0Value=particle.gainParticleNum_Every0_1L(PARTICLENUM_5_0_UM_EVERY0_1L_AIR);
  PM10_0Value=particle.gainParticleNum_Every0_1L(PARTICLENUM_10_UM_EVERY0_1L_AIR);

/*
  if(PMSerial.find(0x42))
  {
    PMSerial.readBytes(buf,LENG);
    
    if(buf[0] == 0x4d)
    {
      if(checkValue(buf,LENG))
      {
        PM01Value=transmitPM01(buf); //count PM1.0 value of the air detector module
        PM2_5Value=transmitPM2_5(buf);//count PM2.5 value of the air detector module
        PM10Value=transmitPM10(buf); //count PM10 value of the air detector module
        //Serial.println(F("It's working"));
        PM0_3Value=transmitPM0_3(buf);
        PM0_5Value=transmitPM0_5(buf);
        PM1_0Value=transmitPM1_0(buf);
        PM2_5uValue=transmitPM2_5u(buf);
        PM5_0Value=transmitPM5_0(buf);
        PM10_0Value=transmitPM10_0(buf);
      }
    }
  }

  //PMSerial.end();
*/
  String particleValues = String(PM01Value) +'\t'+ String(PM2_5Value) +'\t'+ String(PM10Value) +'\t'+ String(PM0_3Value) +'\t'+ String(PM0_5Value) +'\t'+ String(PM1_0Value) +'\t'+ String(PM2_5uValue) +'\t'+ String(PM5_0Value) +'\t'+ String(PM10_0Value) +'\t';
  
  return particleValues;
}

String getCO2Value(long CO2){

  String CO2String = "";
  CO2Serial.begin(9600);
  CO2Serial.write(getDensity,9);
  delay(500);
  
  for(int i=0,j=0;i<9;i++){
      
    if (CO2Serial.available()>0){
        
      long hi,lo;
      int ch=CO2Serial.read();
    
      if(i==2){     hi=ch;   }   //High concentration
      if(i==3){     lo=ch;   }   //Low concentration
      if(i==8){
        CO2=hi*256+lo;  //CO2 concentration
        #ifdef DEBUG
          Serial.print("CO2 concentration: ");
          Serial.print(CO2);
          Serial.println("ppm");
        #endif
      }
    }
  }
  //Serial.print(CO2);
  //CO2Serial.end();
  return String(CO2) + '\t';
}

int getNbValues(String values){
  int nbvalues = 0;
  int ivalues = 0;
  //char tmpBuf[RH_RF95_MAX_MESSAGE_LEN];
  //values.toCharArray(tmpBuf, RH_RF95_MAX_MESSAGE_LEN);
  
  while(values[ivalues] != '\0'){
    while(values[ivalues] != '\t'){
      ivalues ++;
    }
    ivalues ++;
    nbvalues ++;
  }
  return nbvalues;
}

int createFrame(char* pFrame, const char* Header, const char* Ender, const int ServerId, const int ClientId, String values, int nbvalues) {
  
  //Fills the frame with the data to send
  char tmpBuf[values.length()];
  values.toCharArray(tmpBuf, values.length());
  
  sprintf(pFrame, "%s\t%d\t%d\t%d\t%s\t%s", Header, ServerId, ClientId, nbvalues, tmpBuf, Ender);
  #ifdef DEBUG
    Serial.println(pFrame);
  #endif
  
  return 1;
}




char checkValue(unsigned char *thebuf, char leng)
{
  char receiveflag=0;
  int receiveSum=0;

  for(int i=0; i<(leng-2); i++){
  receiveSum=receiveSum+thebuf[i];
  }
  receiveSum=receiveSum + 0x42;

  if(receiveSum == ((thebuf[leng-2]<<8)+thebuf[leng-1]))  //check the serial data
  {
    receiveSum = 0;
    receiveflag = 1;
  }
  return receiveflag;
}


/*
//transmit PM Value to PC
uint16_t transmitPM01(uint8_t *thebuf)
{
  uint16_t PM01Val;
  PM01Val=((thebuf[3]<<8) + thebuf[4]); //count PM1.0 value of the air detector module
  return PM01Val;
}

//transmit PM Value to PC
uint16_t transmitPM2_5(uint8_t *thebuf)
{
  uint16_t PM2_5Val;
  PM2_5Val=((thebuf[5]<<8) + thebuf[6]);//count PM2.5 value of the air detector module
  return PM2_5Val;
}

//transmit PM Value to PC
uint16_t transmitPM10(uint8_t *thebuf)
{
  uint16_t PM10Val;
  PM10Val=((thebuf[7]<<8) + thebuf[8]); //count PM10 value of the air detector module
  return PM10Val;
}

//transmit PM Value to PC
uint16_t transmitPM0_3(uint8_t *thebuf)
{
  uint16_t PM0_3Val;
  PM0_3Val=((thebuf[15]<<8) + thebuf[16]); //count PM0_3 value of the air detector module
  return PM0_3Val;
}

//transmit PM Value to PC
uint16_t transmitPM0_5(uint8_t *thebuf)
{
  uint16_t PM0_5Val;
  PM0_5Val=((thebuf[17]<<8) + thebuf[18]); //count PM0_5 value of the air detector module
  return PM0_5Val;
}

//transmit PM Value to PC
uint16_t transmitPM1_0(uint8_t *thebuf)
{
  uint16_t PM1_0Val;
  PM1_0Val=((thebuf[19]<<8) + thebuf[20]); //count PM1_0 value of the air detector module
  return PM1_0Val;
}


//transmit PM Value to PC
uint16_t transmitPM2_5u(uint8_t *thebuf)
{
  uint16_t PM2_5uVal;
  PM2_5uVal=((thebuf[21]<<8) + thebuf[22]); //count PM2_5u value of the air detector module
  return PM2_5uVal;
}

//transmit PM Value to PC
uint16_t transmitPM5_0(uint8_t *thebuf)
{
  uint16_t PM5_0Val;
  PM5_0Val=((thebuf[23]<<8) + thebuf[24]); //count PM5_0 value of the air detector module
  return PM5_0Val;
}

//transmit PM Value to PC
uint16_t transmitPM10_0(uint8_t *thebuf)
{
  uint16_t PM10_0Val;
  PM10_0Val=((thebuf[25]<<8) + thebuf[26]); //count PM10_0 value of the air detector module
  return PM10_0Val;
}

*/