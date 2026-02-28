import time


#can import scripts from the same folder in order to use their methods (like flutter/php slim)
import rpi_led_buzzer as rpi
import datatbase as db


db.create_database() #database created

db.create_customer_table() #customer added to db


def add_customer():
    fname = input("Please enter your first name: ")
    lname = input("Please enter your last name: ")
    email = input("Please enter your email: ")
    phone = input("Please enter your phone number: ")
    address = input("Please enter your address: ")
    
    db.add_customer(fname, lname, email, phone, address)
      
      
def main_menu():
    while True:
        print("Hwllo, Please choose one of the options!")
        print("1. Add new customer")
        print("2. View all customers")
        print("3. Finish and leave")
        
        choice = input("Selection: ")
        
        if choice == '1':
            add_customer()
        elif choice == '2':
            rpi.new_customer_fail()
            # customers = db.select_customersss()
            # for customer in customers:
                # print(customer)
        elif choice == '3':
            print("Bye bye!")
            break
        else:
            print("Invalid, option not supported. Please try again.")

main_menu()
