/**********************************************************************************
* BoxCo_Server then logs 
* it in a file
* 
* Cléis Benoit-Gonin - PMMH Lab - 2021/07/02 
* 
* Thierry Darnige - PMMH Lab - Modified 2021/11/08
* 
**********************************************************************************/

#include <RH_RF95.h>
#include "RTClib.h"
#include <SPI.h>
//#include "SdFat.h"
#include <SD.h>
//#include <U8glib.h>

//Constants to be changed
//------------------------------------------
//#define DEBUG
#define VERBOSE
#define SERVERVERSION "BoxCo_Server 2.1"
#define ARDUINO_MEGA
#define SERVER_ID 1
//------------------------------------------

#define HEADER "HBXCO"
#define ENDER "EBXCO"
#define FILE_STARTER "client"
#define EXTENSION ".log"
#define TIMEOUT_RECV 10000
#define FRAME_COUNTER_MAX 10

#ifdef __AVR__
    #include <SoftwareSerial.h>
    
    #ifdef ARDUINO_MEGA
        SoftwareSerial SSerial(62, 2); // RX, TX
    #endif
    #ifndef ARDUINO_MEGA
        SoftwareSerial SSerial(4, 5);
    #endif
    
    #define COMSerial SSerial
    #define ShowSerial Serial

    RH_RF95<SoftwareSerial> rf95(COMSerial);
#endif

#ifdef ARDUINO_SAMD_VARIANT_COMPLIANCE
    #define COMSerial Serial1
    #define ShowSerial SerialUSB

    RH_RF95<Uart> rf95(COMSerial);
#endif

#ifdef ARDUINO_ARCH_STM32F4
    #define COMSerial Serial
    #define ShowSerial SerialUSB

      RH_RF95<HardwareSerial> rf95(COMSerial);
#endif

#define DATE_LEN 20 //19 characters plus \0

//for the RTC module
RTC_DS1307 rtc;

// Pin Led
#define PINLED 3

// Frame counter
uint16_t frameCounter = 0;
uint8_t forceInitLora = 1; // Force Lora init 1= True 0=False

// Default SD chip select is pin 10
#ifdef ARDUINO_MEGA
  const uint8_t chipSelect = 53; // D53
#else
  const uint8_t chipSelect = 10;
#endif

//For the OLED screen
//U8GLIB_SSD1306_128X64 u8g(U8G_I2C_OPT_DEV_0|U8G_I2C_OPT_NO_ACK|U8G_I2C_OPT_FAST);

void dateTime(uint16_t* theDate, uint16_t* theTime) 
{
  // Get the timestamp
  DateTime nowTime = rtc.now();
  
  // return date using FAT_DATE macro to format fields
  *theDate = FAT_DATE(nowTime.year(), nowTime.month(), nowTime.day());

  // return time using FAT_TIME macro to format fields
  *theTime = FAT_TIME(nowTime.hour(), nowTime.minute(), nowTime.second());
}

void setup() {
    ShowSerial.begin(115200);
    #ifdef DEBUG
      ShowSerial.println(F("RF95 server test."));
    #endif

/*
    if (!rf95.init()) {
        ShowSerial.println(F("init failed"));
    }
    else
    {         
        rf95.setFrequency(868.0);
    }
    // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

    // The default transmitter power is 13dBm, using PA_BOOST.
    // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then
    // you can set transmitter powers from 5 to 23 dBm:
    //rf95.setTxPower(13, false);

*/

    //For the Real Time Computer
    rtc.begin();
    
    if (!rtc.isrunning()){
      Serial.println(F("RTC is NOT running!"));
      //sets the RTC to the date & time this sketch was compiled
      //rtc.adjust(DateTime(__DATE__, __TIME__));
    }

    // See if the SD card is present and can be initialized:
    if (!SD.begin(chipSelect)) 
    {
      Serial.println("Card failed, or not present");
      // Don't do anything more:
      //while (1);
    }
    #ifdef DEBUG
      Serial.println(F("card initialized."));
    #endif

    // set date time callback function
    SdFile::dateTimeCallback(dateTime);

    // The blinking pinled
    pinMode(PINLED, OUTPUT);
}


void loop() {
    
    char Header[] = HEADER;
    uint8_t ServerId = SERVER_ID;
    uint8_t ClientId = 0;
    uint8_t nbValues = 0;
    char pData[RH_RF95_MAX_MESSAGE_LEN];
    char pFName[16]; 
    File dataFile;
    char myDate[DATE_LEN];
    uint8_t initLoraFailed = 0; // False
   
    // Sometimes, reinitialize the Lora module
    if (forceInitLora == 1) // True
    {
      if (!rf95.init()) 
      {
        #ifdef DEBUG  
          ShowSerial.println(F("Init Lora failed"));
        #endif       
        initLoraFailed = 1; // True
        forceInitLora = 1; // True
      }
      else
      {       
        #ifdef DEBUG  
          ShowSerial.println(F("Reinit Lora"));
        #endif
        rf95.setFrequency(868.0);
        initLoraFailed = 0; // False
        forceInitLora = 0; // False
      }     
    }

    if (initLoraFailed == 0) // No error
    {
        if (rf95.available())
        //if (rf95.waitAvailableTimeout(TIMEOUT_RECV))
        {
            // Should be a message for us now
            uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
            uint8_t len = sizeof(buf);
            
            if (rf95.recv(buf, &len)) 
            {
                // We received something in the buf
                buf[len] = '\0';
                frameCounter++;
                if ( frameCounter > FRAME_COUNTER_MAX)
                {
                  frameCounter = 0;
                  forceInitLora = 1; // True                  
                }
    
                //Check if the frame is for this server
                if (parseFrame((char*) buf, Header, &ServerId, &ClientId, &nbValues, pData))
                {
                  // Switch on the Led
                  digitalWrite(PINLED, HIGH);
    
                  // Get date
                  getDate(myDate);
                  
                 //Write the data on the card             
                  createFileName(pFName, FILE_STARTER, EXTENSION, ClientId);
                  writeFrameToSd(pFName, pData, myDate);
 

                  #ifdef VERBOSE
                    ShowSerial.print(ClientId);              
                    ShowSerial.print('\t');
                    ShowSerial.print(myDate);
                    ShowSerial.print('\t');
                    ShowSerial.println(pData);
                  #endif
                  
                  // Switch off the Led
                  digitalWrite(PINLED, LOW);            
    

                }
            }            
        }
    }

  
    // Get commands from the serial line
    byte inChar;
    inChar = ShowSerial.read();
    getCommand(inChar);


}

void getCommand(byte command)
{
  // Set the date
  String dataDateString = "";
  if   (command == 'd')
  {
    #ifdef DEBUG
      ShowSerial.println(F("Date initialized"));
    #endif
    int uYear = Serial.parseInt();
    int uMonth = Serial.parseInt();
    int uDay = Serial.parseInt();
    int uHour = Serial.parseInt();
    int uMinute = Serial.parseInt();
    int uSecond = Serial.parseInt();

    rtc.adjust(DateTime(uYear, uMonth, uDay, uHour, uMinute, uSecond));
    
    // following line sets the RTC to the date & time this sketch was compiled
    dataDateString += String("Date set to :");
    dataDateString += String("\t");
    dataDateString += String(uYear);
    dataDateString += String("\t");
    dataDateString += String(uMonth);
    dataDateString += String("\t");
    dataDateString += String(uDay);
    dataDateString += String("\t");
    dataDateString += String(uHour);
    dataDateString += String("\t");
    dataDateString += String(uMinute);
    dataDateString += String("\t");
    dataDateString += String(uSecond);
    dataDateString += String("\n");
    ShowSerial.println(dataDateString.c_str());


  }

  //Get the firmware Version
  if (command == 'v')
  {
    ShowSerial.println(SERVERVERSION);
  }

}

void createFileName(char* clientFilename, const char* fileStarter, const char* extension, uint8_t ClientId)
{
  char tmpBuf[3];
  clientFilename[0] = '\0';
  strcat(clientFilename, fileStarter);
  itoa(ClientId,tmpBuf,10);
  strcat(clientFilename, tmpBuf);
  strcat(clientFilename, extension);
  clientFilename[11] = '\0';
}

uint8_t parseFrame(char* pFrame, char Header[], uint8_t* pServerId, uint8_t* pClientId, uint8_t* nbValues, char* pData)
{

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
  if (*pServerId != atoi(tmpBuf)){
    return 0;
  }
  
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
  *pClientId = atoi(tmpBuf);

  //Look for nbValues
  ibuf = 0;
  iframe ++;
  //tmpBuf = "";
  while(pFrame[iframe] != '\t'){
    tmpBuf[ibuf] = pFrame[iframe];
    iframe++;
    ibuf++;
  }
  tmpBuf[ibuf] = '\0';
  *nbValues = atoi(tmpBuf);
  //ShowSerial.println(*nbValues);

  //Look for values
  int idata = 0;
  for (int ivalues = 0; ivalues < *nbValues; ivalues++){ //For the number of values
    iframe ++;
    //tmpBuf = "";
    while(pFrame[iframe] != '\t'){ //Check if there is a tab
      pData[idata] = pFrame[iframe];
      iframe++;
      idata++;
    }
    pData[idata] = '\t'; //Put the tab to make some space
    idata ++;    
  }
  pData[idata] = '\0';

 //Look for Ender
  ibuf = 0;
  iframe ++;
  while(pFrame[iframe] != '\0'){
    tmpBuf[ibuf] = pFrame[iframe];
    iframe++;
    ibuf++;
  }
  tmpBuf[ibuf] = '\0';
  if (strcmp(ENDER, tmpBuf) != 0){
    #ifdef DEBUG  
      ShowSerial.println("Ender not found");
    #endif
    return 0;
  }

  // Everything is OK
  return 1;
}

int getDate(char* charArrayDate)
{
  
  DateTime nowTime = rtc.now();

  sprintf(charArrayDate, "%d-%02d-%02dT%02d:%02d:%02d", nowTime.year(), nowTime.month(), nowTime.day(), nowTime.hour(), nowTime.minute(), nowTime.second());
  charArrayDate[DATE_LEN] = '\0';
}


 void writeFrameToSd(char* fname, char* data, char* date)
 {
    //Write the data on the card
    File dataFile;
    dataFile = SD.open(fname, FILE_WRITE);
  
    // if the file is available, write to it:
    if (dataFile) 
    {
      dataFile.print(date);
      dataFile.print('\t');
      dataFile.println(data);
      dataFile.close();
    }
}



int createFrame(char* pFrame, const int ClientId) {
  
  sprintf(pFrame, "%s\t%d\t%d\t%s", HEADER, SERVER_ID, ClientId, ENDER);
  ShowSerial.println(pFrame);
  
  return 1;
}
