#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

// --- SETTINGS FOR THIS SPECIFIC BOARD ---
// Change to "Frig2" for your second ESP32
const char* FRIDGE_ID = "Frig2";

#define DHT11PIN 4
DHT dht(DHT11PIN, DHT11);

const char* ssid = "Talia's Iphone";
const char* password = "Hell0Hell0";
const char* mqtt_server = "172.20.10.7";

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a unique client ID based on the Fridge ID
    String clientId = "ESP32Client-";
    clientId += FRIDGE_ID;
    
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  float humi = dht.readHumidity();
  float temp = dht.readTemperature();

  if (isnan(humi) || isnan(temp)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // Construct topics based on Fridge ID (e.g., Frig1/temp)
  String tempTopic = String(FRIDGE_ID) + "/temp";
  String humTopic = String(FRIDGE_ID) + "/hum";

  client.publish(tempTopic.c_str(), String(temp).c_str());
  client.publish(humTopic.c_str(), String(humi).c_str());

  Serial.print(FRIDGE_ID);
  Serial.print(" - Temp: "); Serial.print(temp);
  Serial.print(" Hum: "); Serial.println(humi);

  delay(5000); // Send data every 5 seconds
}