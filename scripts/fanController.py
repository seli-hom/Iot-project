import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

BROKER = "192.168.0.111"

FAN1 = 18
FAN2 = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN1, GPIO.OUT)
GPIO.setup(FAN2, GPIO.OUT)

GPIO.output(FAN1, GPIO.LOW)
GPIO.output(FAN2, GPIO.LOW)


def on_connect(client, userdata, flags, rc):
    print("Connected to broker")
    client.subscribe("Frig1/fan")
    client.subscribe("Frig2/fan")


def on_message(client, userdata, msg):
    message = msg.payload.decode()

    print(msg.topic + " " + message)

    if msg.topic == "Frig1/fan":
        if message == "ON":
            GPIO.output(FAN1, GPIO.HIGH)
        else:
            GPIO.output(FAN1, GPIO.LOW)

    if msg.topic == "Frig2/fan":
        if message == "ON":
            GPIO.output(FAN2, GPIO.HIGH)
        else:
            GPIO.output(FAN2, GPIO.LOW)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)

client.loop_forever()