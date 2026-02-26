import RPi.GPIO as GPIO
import time


LED_RED = 23
BUZZER = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_RED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)


GPIO.output(LED_RED, GPIO.HIGH)
GPIO.output(BUZZER, GPIO.HIGH)

time.sleep(1.8)
GPIO.output(LED_RED, GPIO.LOW)
GPIO.output(BUZZER, GPIO.LOW)

time.sleep(5)
GPIO.cleanup()
   