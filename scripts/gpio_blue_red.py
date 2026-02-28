import RPi.GPIO as GPIO
import time

LED_BLUE = 24
LED_RED = 23
BUZZER = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_BLUE, GPIO.OUT)
GPIO.setup(LED_RED, GPIO.OUT)   
GPIO.setup(BUZZER, GPIO.OUT)

#No issues customer is able to register into the database successfulyy
# @app.route('customerRegistration/success')
def new_customer_success():
    GPIO.output(LED_BLUE, GPIO.HIGH)
    GPIO.output(LED_RED, GPIO.LOW)
    GPIO.output(BUZZER, GPIO.LOW)
    time.sleep(4)
    GPIO.output(LED_BLUE, GPIO.LOW)
    return {status: 'success'}

#DB error happens and customer is unable to register
# @app.route('customerRegistration/fail')
def new_customer_fail():
    GPIO.output(LED_RED, GPIO.HIGH)
    GPIO.output(LED_BLUE, GPIO.LOW)
    GPIO.output(BUZZER, GPIO.HIGH)
    time.sleep(4)
    GPIO.output(LED_RED, GPIO.LOW)
    GPIO.output(BUZZER, GPIO.LOW)
    return {status: 'fail'}
