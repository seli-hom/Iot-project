import paho.mqtt.subscribe as subscribe
import json
from imap_tools import MailBox
import smtplib
import paho.mqtt.publish as publish
import paho.mqtt.publish as publish

msg = publish.single("room/temperature",payload="read", hostname="192.168.2.163",qos=0)

print("message sent")



def get_temp():
    sub = subscribe.simple("Temperature/Kitchen", hostname="192.168.2.163")
    kitchen = sub.payload.decode('utf-8')
    kitchen = json.loads(kitchen)

    sub = subscribe.simple("Temperature/Room", hostname="192.168.2.163")
    room = sub.payload.decode('utf-8')
    room = json.loads(room)

    data = kitchen | room
    data = json.dumps(data)
    return  json.loads(data)
    

get_temp()

