#!/bin/bash

sudo apt update
sudo apt upgrade -y

# Install Mosquitto
sudo apt install mosquitto mosquitto-clients -y

# Enable service
sudo systemctl enable mosquitto

# Start Mosquitto
sudo systemctl start mosquitto

# Check status
sudo systemctl status mosquitto

# Allow remote connections
sudo nano /etc/mosquitto/mosquitto.conf

# ti be added at the bottom of mosquitto.conf
# listener 1883
# allow_anonymous true

#* make sure to check the IP address: user 'hostname -I'
#* use the output IP in the script before you run the file