#* install paho-mqtt
#* pip3 install paho-mqtt
import paho.mqtt.client as mqtt

BROKER = "192.168.0.111"

# please take note of the media placements
# if your wiring is different, update the position below
# Fan 1 ______________________
# GPIO 18: Motor Driver IN1
# Motor Driver OUT1: Motor +
# Motor Driver OUT2: Motor -

# Fan 2 ______________________
# GPIO 23: Motor Driver IN2
# Motor Driver OUT3: Motor +
# Motor Driver OUT4: Motor -

# Power ______________________________
# Raspberry Pi GND: Motor Driver GND
# External 5V/9V: Motor Driver VCC

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT")

    client.subscribe("Frig1/temperature")
    client.subscribe("Frig1/humidity")
    client.subscribe("Frig2/temperature")
    client.subscribe("Frig2/humidity")


def on_message(client, userdata, msg):
    value = msg.payload.decode()
    print(msg.topic + " : " + value)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)

client.loop_forever()