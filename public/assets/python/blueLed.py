import RPi.GPIO as GPIO
import time


LED = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)

GPIO.output(LED, GPIO.HIGH)

time.sleep(2)

GPIO.output(LED, GPIO.LOW)

time.sleep(5)
GPIO.cleanup()