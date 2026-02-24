import time


#can import scripts from the same folder in order to use their methods (like flutter/php slim)
import rpi_led_buzzer as rpi
import database as db


db.create_database() #database created

db.create_customer_table() #customer added to db


def add_customer():
    fname = input("Please enter your first name: ")
    lname = input("Please enter your last name: ")
    email = input("Please enter your email: ")
    phone = input("Please enter your phone number: ")
    address = input("Please enter your address: ")
    try:
        if db.add_customer(fname, lname, email, phone, address):
            rpi.new_customer_success()
            print("Customer added successfully!")
        else:
            rpi.new_customer_fail()
            print("Failed to add customer. Please check the database for errors.")