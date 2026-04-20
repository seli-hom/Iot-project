import threading
import time
import paho.mqtt.client as mqtt
# Import shared data and motor control from your hardware service
from services.hardware import hardware_status, motor_control, TEMP_LIMIT

def start_mqtt(broker_ip="127.0.0.1"):
    """This is the entry point called by app.py"""
    mqtt_thread = threading.Thread(target=mqtt_worker, args=(broker_ip,), daemon=True)
    mqtt_thread.start()
    print("MQTT Background Thread Started.")

def mqtt_worker(broker_ip):
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    
    # We define on_message inside or import it
    def on_message(client, userdata, message):
        try:
            topic = message.topic
            val = float(message.payload.decode())
            
            # Update the global hardware_status dictionary
            if "Frig1" in topic:
                if "temp" in topic: hardware_status["frig1"]["temp"] = val
                else: hardware_status["frig1"]["hum"] = val
            elif "Frig2" in topic:
                if "temp" in topic: hardware_status["frig2"]["temp"] = val
                else: hardware_status["frig2"]["hum"] = val
            
            # Check thresholds
            if "temp" in topic and val > TEMP_LIMIT:
                # Logic to trigger email alert would go here
                pass
        except Exception as e:
            print(f"MQTT Data Error: {e}")

    client.on_message = on_message
    try:
        client.connect(broker_ip, 1883)
        client.subscribe("Frig1/#")
        client.subscribe("Frig2/#")
        client.loop_forever()
    except Exception as e:
        print(f"MQTT Connection Error: {e}")

def start_email_checker(alerts_instance):
    """Launches the email listener in a thread"""
    email_thread = threading.Thread(target=email_worker, args=(alerts_instance,), daemon=True)
    email_thread.start()
    print("Email Checker Thread Started.")

def email_worker(alerts):
    while True:
        if alerts.waiting_for_reply:
            if alerts.check_for_yes():
                motor_control("on")
                hardware_status["last_alert"] = "Fan activated via Email Authorization."
        time.sleep(10)