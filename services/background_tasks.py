# services/background_tasks.py
import threading
import time
import paho.mqtt.client as mqtt
from services import hardware
from services.hardware import motor_control

# Temperature threshold to trigger alerts
TEMP_LIMIT = 21.0

def mqtt_worker(broker_ip, mail_manager):
    """
    Background worker that listens for MQTT messages from ESP32 sensors.
    """
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

    def on_message(client, userdata, message):
        # Log to terminal so you can see data arriving in real-time
        print(f"DEBUG: Received message on {message.topic}: {message.payload.decode()}")
        
        try:
            # Normalize topic to lowercase to avoid case-sensitivity issues
            topic = message.topic.lower()
            val = float(message.payload.decode())
            
            # 1. Update Global Status using the module reference
            if "frig1" in topic:
                if "temp" in topic: 
                    hardware.hardware_status["frig1"]["temp"] = val
                else: 
                    hardware.hardware_status["frig1"]["hum"] = val
            
            elif "frig2" in topic:
                if "temp" in topic: 
                    hardware.hardware_status["frig2"]["temp"] = val
                else: 
                    hardware.hardware_status["frig2"]["hum"] = val
            
            # 2. Check for Overheating & Send Alerts
            if "temp" in topic and val > TEMP_LIMIT:
                # Rate limit: Only send one email every 5 minutes (300 seconds)
                if time.time() - mail_manager.last_email_time > 300:
                    fridge_name = "Fridge 1" if "frig1" in topic else "Fridge 2"
                    mail_manager.send_alert(val, fridge_name)
                    hardware.hardware_status["last_alert"] = f"Alert: {fridge_name} is {val}°C"

        except Exception as e:
            print(f"MQTT Processing Error: {e}")

    client.on_message = on_message
    
    try:
        client.connect(broker_ip, 1883)
        # Subscribing to wildcards for both fridges
        client.subscribe("Frig1/#")
        client.subscribe("Frig2/#")
        client.loop_forever()
    except Exception as e:
        print(f"MQTT Connection Error: {e}")

def start_mqtt(broker_ip, mail_manager):
    """Starts the MQTT listener in a non-blocking background thread."""
    mqtt_thread = threading.Thread(target=mqtt_worker, args=(broker_ip, mail_manager), daemon=True)
    mqtt_thread.start()
    print("MQTT Background Thread Launched.")

def start_email_checker(mail_manager):
    """Starts the IMAP email listener in a non-blocking background thread."""
    email_thread = threading.Thread(target=email_worker, args=(mail_manager,), daemon=True)
    email_thread.start()
    print("Email Checker Thread Launched.")

def email_worker(mail_manager):
    """
    Background worker that checks the inbox for 'YES' replies 
    to activate the fan hardware.
    """
    while True:
        try:
            if mail_manager.waiting_for_reply:
                if mail_manager.check_for_yes():
                    motor_control("on")
                    hardware.hardware_status["last_alert"] = "Fan activated via Email Authorization."
        except Exception as e:
            print(f"Email Worker Error: {e}")
            
        # Check every 10 seconds to avoid Gmail IMAP rate limits
        time.sleep(10)