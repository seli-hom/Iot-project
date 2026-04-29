import requests
from services import email_service

def count_people_in_store():
    # Ask Pareto Anywhere for the current list of devices it sees
    response = requests.get('http://localhost:3001/devices')
    info = response.json()
    devices = info["devices"]
    # Each key in the 'devices' dictionary is a unique MAC address
    number_of_people = len(devices)
    if number_of_people == 0:
        print("No devices detected nearby.")
    elif number_of_people >50:
        print(f"Warning: High number of devices detected! ({number_of_people} devices)")
        email_service.customer_count_alert(number_of_people)
    print(f"There are currently {number_of_people} devices nearby.")
    return list(devices.keys())

count_people_in_store()
