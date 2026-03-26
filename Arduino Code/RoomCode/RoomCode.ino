#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Adafruit_Sensor.h>
// Replace the next variables with your SSID/Password combination
//const char* ssid = "iotvanier";
//const char* password = "14730078";
//const char* mqtt_server = "192.168.0.101";
//const char* ssid = "Nwantoly";
//const char* password = "Forind123";
//const char* mqtt_server = "192.168.2.163";
const char* ssid = "Talia's Iphone";
const char* password = "Hell0Hell0";
const char* mqtt_server = "172.20.10.6";
WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

const int DHTPIN = 4;
const int DHTTYPE = DHT11;
float humidity = 0;
float temperature = 0;
String strhumidity; 
String strtemperature;
String tempMessage;


DHT dht(DHTPIN, DHTTYPE);
void setup() {
  Serial.begin(115200);
  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}
void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}
void callback(String topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messagein;
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messagein += (char)message[i];
  }
  //if (topic == "room/temperature") {

 // }
}
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("vanieriot")) {
      Serial.println("connected");
      client.subscribe("room/temperature");

    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  if (!client.loop())
    client.connect("vanieriot");
 // client.setCallback(callback);
 // client.subscribe("room/temperature");
       while (true) {
        humidity = dht.readHumidity();
        temperature = dht.readTemperature();
         strhumidity = String(humidity, 2); 
         strtemperature = String(temperature, 2); 
          tempMessage = "{\"room\": {\"temperature\": " + strtemperature + ", \"humidity\": " + strhumidity + "}}";
         const char* finalMessage2 = tempMessage.c_str();
         client.publish("Temperature/Room", finalMessage);
         Serial.println(finalMessage);
        delay(2000);
    }
  Serial.println("looped");
  delay(5000);
}