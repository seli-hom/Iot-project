import RPi.GPIO as GPIO
import time 

LED_BLUE = 24
LED_RED = 23
BUZZER = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_BLUE, GPIO.OUT)
GPIO.setup(LED_RED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

#customer is able to sucessfully add themselves to the database
def new_customer_success():
    GPIO.output(LED_BLUE, GPIO.HIGH)
    
    time.sleep(1.5)
    GPIO.output(LED_BLUE, GPIO.LOW)

#Database error happens and customer cannot add to db
def new_customer_fail():
    GPIO.output(LED_RED, GPIO.HIGH)
    GPIO.output(BUZZER, GPIO.HIGH)
    
    time.sleep(1.5)
    GPIO.output(LED_RED, GPIO.LOW)
    GPIO.output(BUZZER, GPIO.LOW)
   