import paho.mqtt.client as mqtt
import time
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from gpiozero import OutputDevice

# ---------------------------
# CONFIG
# ---------------------------
BROKER = ""

SENDER_EMAIL_ADDR = ""
SENDER_PASSWORD = ""

RECEIVER_EMAIL_ADDR = ""

SMTP_SERVER = "smtp.gmail.com"
IMAP_SERVER = "imap.gmail.com"

EMAIL_INTERVAL = 300  # 5 minutes
TEMP_THRESHOLD = 24   # °C

# ---------------------------
# GPIO SETUP (Pi 5)
# ---------------------------
Motor1 = OutputDevice(22)
Motor2 = OutputDevice(27)
Motor3 = OutputDevice(17)

Motor1.off()

# ---------------------------
# GLOBAL VARIABLES
# ---------------------------
latest_temp = None
latest_hum = None

last_email_time = 0
waiting_for_reply = False
alert_sent = False

# ---------------------------
# MOTOR CONTROL (5 SECONDS)
# ---------------------------
def motor_on_5_seconds():
    print("Motor ON (5 seconds)")
    
    Motor1.on()
    Motor2.off()
    Motor3.on()

    time.sleep(5)

    Motor1.off()
    print("Motor OFF")

# ---------------------------
# MQTT CALLBACK
# ---------------------------
def on_message(client, userdata, message):
    global latest_temp, latest_hum

    topic = message.topic
    payload = message.payload.decode()

    if topic == "esp32/temperature":
        latest_temp = payload
        print("Temperature:", latest_temp)

    elif topic == "esp32/humidity":
        latest_hum = payload
        print("Humidity:", latest_hum)

# ---------------------------
# SEND EMAIL
# ---------------------------
def send_email():
    global last_email_time, waiting_for_reply

    body = f"""
Temperature: {latest_temp}°C
Humidity: {latest_hum}%

Temperature is above {TEMP_THRESHOLD}°C.

Would you like to turn on the fan for 5 seconds? (yes/no)
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

    print("\nEmail sent\n")

    last_email_time = time.time()
    waiting_for_reply = True

# ---------------------------
# CHECK EMAIL REPLY
# ---------------------------
def check_email():
    global waiting_for_reply

    try:
        imap = imaplib.IMAP4_SSL(IMAP_SERVER)
        imap.login(SENDER_EMAIL_ADDR, SENDER_PASSWORD)
        imap.select("INBOX")

        status, messages = imap.search(
            None,
            '(UNSEEN FROM "{}")'.format(RECEIVER_EMAIL_ADDR)
        )

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

            print("\nReply preview:\n", body[:100])

            clean_body = body.strip()

            if clean_body.startswith("yes"):
                motor_on_5_seconds()
                waiting_for_reply = False

            elif clean_body.startswith("no"):
                print("Motor stays OFF")
                waiting_for_reply = False

        imap.logout()

    except Exception as e:
        print("EMAIL CHECK ERROR:", e)

# ---------------------------
# MQTT SETUP
# ---------------------------
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, 1883)

client.subscribe("esp32/temperature")
client.subscribe("esp32/humidity")

client.on_message = on_message

client.loop_start()

print("SYSTEM RUNNING\n")

# ---------------------------
# MAIN LOOP
# ---------------------------
try:
    while True:

        if latest_temp is not None and latest_hum is not None:

            temp_value = float(latest_temp)

            if temp_value >= TEMP_THRESHOLD:

                if (not alert_sent) and (time.time() - last_email_time > EMAIL_INTERVAL):
                    send_email()
                    alert_sent = True

            else:
                alert_sent = False

        if waiting_for_reply:
            check_email()

        time.sleep(5)

except KeyboardInterrupt:
    print("STOPPING PROGRAM")
    Motor1.off()