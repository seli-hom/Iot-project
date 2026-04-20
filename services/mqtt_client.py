import paho.mqtt.client as mqtt
from services.hardware import hardware_status

def on_message(client, userdata, message):
    global store_data
    try:
        topic = message.topic
        payload = message.payload.decode()
        val = float(payload)
        
        print(f"MQTT Data -> Topic: {topic} | Value: {val}")

        # Update data dictionary based on topic
        if "Frig1" in topic:
            if "temp" in topic: store_data["frig1"]["temp"] = val
            else: store_data["frig1"]["hum"] = val
        elif "Frig2" in topic:
            if "temp" in topic: store_data["frig2"]["temp"] = val
            else: store_data["frig2"]["hum"] = val
        
        # Threshold Check
        if "temp" in topic and val > TEMP_LIMIT:
            # Check if an email has been sent in the last 5 minutes (to avoid spam)
            if time.time() - alerts.last_email_time > 300:
                f_name = topic.split('/')[0]
                alerts.send_alert(val, f_name)
                store_data["last_alert"] = f"Critical Alert: {f_name} is {val}°C"
    except Exception as e:
        print(f"MQTT Processing Error: {e}")

def start_mqtt():
    # Setup client and loop_start()
    pass