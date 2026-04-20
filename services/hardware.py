from gpiozero import OutputDevice

# Shared state across the app
hardware_status = {
    "frig1": {"temp": 0.0, "hum": 0.0},
    "frig2": {"temp": 0.0, "hum": 0.0},
    "fan_on": False,
    "last_alert": ""
}

try:
    Motor1 = OutputDevice(22, initial_value=False)
    Motor2 = OutputDevice(27, initial_value=False)
    Motor3 = OutputDevice(17, initial_value=False)
    print("GPIO Pins initialized to OFF state.")
except Exception as e:
    print(f"GPIO Error: {e}. Try running 'sudo pkill -9 python' or rebooting.")
    Motor1 = Motor2 = Motor3 = None

def motor_control(state):
    # Only function that can control the DC Motor pins based on the desired state
    if Motor1 is None:
        return

    if state == "on":
        Motor1.on()
        Motor2.off()
        Motor3.on()
        hardware_status["fan_on"] = True
        print("Hardware: Fan Turned ON")
    else:
        Motor1.off()
        Motor2.off()
        Motor3.off()
        hardware_status["fan_on"] = False
        print("Hardware: Fan Turned OFF")