import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
import time
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
import json


# ---------------------------
# CONFIG
# ---------------------------
BROKER = "172.20.10.7"

SENDER_EMAIL_ADDR = "taliamuro3@gmail.com"
SENDER_PASSWORD = "hapc ypha dcwh ewbc"

RECEIVER_EMAIL_ADDR = "nwantolyLuke@gmail.com"
RECEIVER_PASSWORD = "dwjiapckhjltbxre"

SMTP_SERVER = "smtp.gmail.com"
IMAP_SERVER = "imap.gmail.com"

EMAIL_INTERVAL = 300  # 5 minutes

# ---------------------------
# GLOBAL VARIABLES
# ---------------------------
latest_temp = None
latest_hum = None

last_email_time = 0
waiting_for_reply = False

# ---------------------------
# MQTT CALLBACK
# ---------------------------
def on_message(client, userdata, msg):
    global latest_temp, latest_hum

    if msg.topic == "esp32/temperature":
        latest_temp = msg.payload.decode()

    elif msg.topic == "esp32/humidity":
        latest_hum = msg.payload.decode()

# ---------------------------
# SEND EMAIL
# ---------------------------
def send_email():
    global last_email_time, waiting_for_reply

    body = f"""
Temperature: {latest_temp}°C
Humidity: {latest_hum}%

Would you like to turn on the fan? (yes/no)
"""

    msg = MIMEText(body)
    msg["Subject"] = "Temperature Alert - Fan Control"
    msg["From"] = SENDER_EMAIL_ADDR
    msg["To"] = RECEIVER_EMAIL_ADDR

    smtp = smtplib.SMTP(SMTP_SERVER, 587)
    smtp.starttls()
    smtp.login(SENDER_EMAIL_ADDR, SENDER_PASSWORD)
    smtp.send_message(msg)
    smtp.quit()

    print("✅ Email sent")

    last_email_time = time.time()
    waiting_for_reply = True

# ---------------------------
# CHECK EMAIL REPLY
# ---------------------------
def check_email(client):
    global waiting_for_reply

    imap = imaplib.IMAP4_SSL(IMAP_SERVER)
    imap.login(RECEIVER_EMAIL_ADDR, RECEIVER_PASSWORD)
    imap.select("INBOX")
    

    # ONLY unread emails (prevents duplicates)
    status, messages = imap.search(None, '(UNSEEN SUBJECT "Temperature Alert")')

    email_ids = messages[0].split()

    for e_id in email_ids:
        status, data = imap.fetch(e_id, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])

        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode("utf-8", errors="ignore").lower()
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode("utf-8", errors="ignore").lower()

        print("📩 Reply:", body)
        # return ("Reply :" + body)

        if "yes" in body:
            print("🟢 Turning fan ON")
            client.publish("esp32/fan", "on")
            waiting_for_reply = False

        elif "no" in body:
            print("🔴 Fan stays OFF")
            waiting_for_reply = False

    imap.logout()

# ---------------------------
# MQTT SETUP
# ---------------------------
client = mqtt.Client()
client.connect(BROKER, 1883)

client.subscribe("esp32/temperature")
client.subscribe("esp32/humidity")

client.on_message = on_message

client.loop_start()

# ---------------------------
# MAIN LOOP
# ---------------------------
while True:

    sub = subscribe.simple("esp32/humidity", hostname=BROKER)
    json_data = json.loads(sub.payload)
    print(json_data)

    # Wait until we actually have data
    if latest_temp is not None and latest_hum is not None:

        # Send email only if:
        # 1. Not waiting for reply
        # 2. Enough time passed
        if (not waiting_for_reply) and (time.time() - last_email_time > EMAIL_INTERVAL):
            send_email()

    # Always check for replies
    if waiting_for_reply:
        check_email(client)
        # print("Client Reply: " + check_email(client))

    time.sleep(5)