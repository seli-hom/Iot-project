import requests

def get_data():
    try:
        
        response = requests.get('http://localhost:3001/context/device/c30000455da6/3')
        
        response.raise_for_status() 
        info = response.json()
        # print(info)
        devices = info["devices"]
        sensor = devices["c30000455da6/3"]
        data = sensor["dynamb"]
        print(data)
       
        temperature = data.get("temperature")
        humidity = data.get("relativeHumidity")
        light = data.get("luminousFlux", "N/A")  # Some devices might not have this
        motion_raw = data.get("isMotionDetected")
        battery = data.get("batteryPercentage")
        
        motion = motion_raw[0] if isinstance(motion_raw, list) else motion_raw
       

        
        HT = {"temperature": temperature, "humidity": humidity}

        
        send_data = {
            "HT": HT,
            "light": light,
            "motion": motion,      
            "batteryState": battery 
        }
        
        return send_data
        
    except Exception as e:
        print(f"Error fetching BLE data: {e}")
        # Return a safe default so the frontend doesn't crash
        return {
            "HT": {"temperature": 0, "humidity": 0},
            "light": 0,
            "motion": False,
            "batteryState": 0
        }