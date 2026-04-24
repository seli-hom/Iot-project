# import RPi.GPIO as GPIO
# # from gpiozero import LED
# import time

# LED_BLUE = 24
# LED_RED = 23
# BUZZER = 20

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(LED_BLUE, GPIO.OUT)
# GPIO.setup(LED_RED, GPIO.OUT)   
# GPIO.setup(BUZZER, GPIO.OUT)

# #No issues customer is able to register into the database successfulyy
# # @app.route('customerRegistration/success')
# def new_customer_success():
#     GPIO.output(LED_BLUE, GPIO.HIGH)
#     GPIO.output(LED_RED, GPIO.LOW)
#     GPIO.output(BUZZER, GPIO.LOW)
#     time.sleep(4)
#     GPIO.output(LED_BLUE, GPIO.LOW)
#     return 

# #DB error happens and customer is unable to register
# # @app.route('customerRegistration/fail')
# def new_customer_fail():
#     GPIO.output(LED_RED, GPIO.HIGH)
#     GPIO.output(LED_BLUE, GPIO.LOW)
#     GPIO.output(BUZZER, GPIO.HIGH)
#     time.sleep(2)
#     GPIO.output(LED_RED, GPIO.LOW)
#     GPIO.output(BUZZER, GPIO.LOW)
#     return 

from gpiozero import LED
from gpiozero import Buzzer
import time
import os

# Update these to your actual BCM pin numbers
BLUE_PIN = 24 
RED_PIN = 23
BUZZER_PIN = 20

# We wrap the initialization so it only runs once and logs success
try:
    # Only initialize if the LEDs aren't already set up
    blue_led = LED(BLUE_PIN)
    red_led = LED(RED_PIN)
    buzzer = Buzzer(BUZZER_PIN)
    print(f"--- HARDWARE LOG: LEDs initialized on BCM {BLUE_PIN} & {RED_PIN} and Buzzer ({BUZZER_PIN}) ready ---")
except Exception as e:
    print(f"--- HARDWARE LOG: Initialization Error: {e} ---")
    blue_led = None
    red_led = None
    buzzer = None

def blink_blue():
    if blue_led:
        print("--- HARDWARE LOG: Blinking BLUE LED (Success) ---")
        blue_led.on()
        time.sleep(1.0) # Longer sleep for testing
        blue_led.off()
        print("--- HARDWARE LOG: BLUE LED Off ---")
    else:
        print("--- HARDWARE LOG: Cannot blink BLUE, LED not initialized ---")

def blink_red():
    if red_led and buzzer:
        print("--- HARDWARE LOG: Failure Signal (RED + BUZZER) ---")
        red_led.on()
        buzzer.on()
        time.sleep(0.1)
        red_led.off()
        buzzer.off()
        print("--- HARDWARE LOG: RED LED Off ---")
    else:
        print("--- HARDWARE LOG: Cannot blink RED, LED not initialized ---")