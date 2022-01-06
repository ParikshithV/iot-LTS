#include <SPI.h>
#include <Wire.h>
#include <MFRC522.h>
#include <ESP8266WiFi.h>
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"

#if defined(ESP8266)
  #define BUTTON_A  0
  #define BUTTON_B 16
  #define BUTTON_C  2
#endif

#define RST_PIN D3
#define SS_PIN D8

/********* WiFi Access Point ***********/


#define WLAN_SSID       "Dunder_Mifflin" //Wifi Name
#define WLAN_PASS       "lastroomkawifi" // Wifi Password


/********* Adafruit.io Setup ***********/


#define AIO_SERVER      "io.adafruit.com"
#define AIO_SERVERPORT  1883                   // use 8883 for SSL
#define AIO_USERNAME    "RedRabbit1" // AdaFruit Usernmae
#define AIO_KEY         "aio_api_key"// AdaFruit Key

WiFiClient client;

Adafruit_MQTT_Client mqtt(&client, AIO_SERVER, AIO_SERVERPORT, AIO_USERNAME, AIO_KEY);

Adafruit_MQTT_Subscribe rfidswitch = Adafruit_MQTT_Subscribe(&mqtt, AIO_USERNAME "/feeds/rfidswitch");
Adafruit_MQTT_Publish rfidata = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/rfiddata");

MFRC522 rfid(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
 Serial.begin(9600);
   
  SPI.begin();
  rfid.PCD_Init();
//  mfrc522.PCD_DumpVersionToSerial();
  Serial.println("RFID Active");

   delay(1000);
 
 // Connect to WiFi access point.
  Serial.println();
  Serial.println("Connecting to ");
  Serial.println(WLAN_SSID);

  WiFi.begin(WLAN_SSID, WLAN_PASS);
  while (WiFi.status() != WL_CONNECTED) {
  delay(500);
  Serial.print(".");
  }
  Serial.println();
 
 
  Serial.println("WiFi connected");
  Serial.println("IP address: "); Serial.println(WiFi.localIP());

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
 
  // Setup MQTT subscription.
  mqtt.subscribe(&rfidswitch);
  //mqtt.subscribe(&rfidata);
  
}
 
void loop() {

  MQTT_connect();
  Serial.print("Refreshing...\n");
  digitalWrite(LED_BUILTIN, LOW);
  Adafruit_MQTT_Subscribe *subscription;
  
  while ((subscription = mqtt.readSubscription(5000))) {

     if (subscription == &rfidswitch) {
      Serial.print("Switch toggle");
      char * temp = (char *) rfidswitch.lastread;
      Serial.print("\n");
      digitalWrite(LED_BUILTIN, HIGH);
      Serial.println("Reading RFID");
      // RFID read..
      if (rfid.PICC_IsNewCardPresent()) { // new tag is available
        if (rfid.PICC_ReadCardSerial()) { // NUID has been readed
          MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
          //Serial.print("RFID/NFC Tag Type: ");
          //Serial.println(rfid.PICC_GetTypeName(piccType));
          String id = "";
          // print NUID in Serial Monitor in the hex format
          Serial.print("UID:");
          for (int i = 0; i < rfid.uid.size; i++) {
            Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
            Serial.print(rfid.uid.uidByte[i], HEX);
            id = id + rfid.uid.uidByte[i];
          }
          Serial.println();
          Serial.println(id);
          char idpub[50];
          id.toCharArray(idpub, 50);
          rfidata.publish(idpub);
          rfid.PICC_HaltA(); // halt PICC
          rfid.PCD_StopCrypto1(); // stop encryption on PCD
        }
        Serial.println("Read complete");
        digitalWrite(LED_BUILTIN, LOW);
      }
      else{
        digitalWrite(LED_BUILTIN, LOW);
        rfidata.publish("No tag");
      }
    }
  }
}


void MQTT_connect() {
  int8_t ret;
  // Stop if already connected.
  if (mqtt.connected()) {
    //Serial.println("wifi on");
    return;
  }
 
 
  Serial.println("Connecting to MQTT... ");
 
 
  uint8_t retries = 3;
  while ((ret = mqtt.connect()) != 0) { // connect will return 0 for connected
    Serial.println(mqtt.connectErrorString(ret));
    Serial.println("Retrying MQTT connection in 5 seconds...");
    mqtt.disconnect();
    delay(5000);  // wait 5 seconds
    retries--;
    if (retries == 0) {
      // basically die and wait for WDT to reset me
      while (1);
    }
  }
  Serial.println("MQTT Connected!");
}
