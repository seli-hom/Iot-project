import requests
from services import email_service

response = requests.get('http://localhost:3001/context/device/c30000455da8/3')
devices = response.json()
    

def temperature_humidity():
    # Ask Pareto Anywhere for the current list of devices it sees
    print(devices)
    temperature = devices['temperature']
    temperature = round(temperature, 2)
    humidity = devices['humidity']
    humidity = round(humidity, 2)
    temperature_humidity = [
        {"temperature": temperature},
        {"humidity": humidity}
    ]
    return ltemperature_humidity

def PIR():
    # Ask Pareto Anywhere for the current list of devices it sees
    print(devices)
    PIR = devices['PIR']
    print("Motion detected:", PIR)
    return PIR

def photo_sensor():
    # Ask Pareto Anywhere for the current list of devices it sees
    print(devices)
    photo_sensor = devices['light']
    print("Light level:", photo_sensor)
    return photo_sensor
