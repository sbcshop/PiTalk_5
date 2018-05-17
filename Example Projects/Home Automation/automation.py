#!/usr/bin/python3

"""
This is a example code to control PiRelay from PiTalk and make Smart Home.
It will check the sender's number and message content to ON/OFF the device.

Developed By: SB components
"""

import pitalk
import pirelay
import time
import logging

# Debuging Enabled 
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

# PiTalk port and baudrate
phone = pitalk.PiTalk('/dev/ttyS0', 115200)
phone.connect()

# Empty list to store SMS
messageData = []

relay1 = pirelay.Relay("RELAY1")
relay2 = pirelay.Relay("RELAY2")
relay3 = pirelay.Relay("RELAY3")
relay4 = pirelay.Relay("RELAY4")

# SMS sender's number
My_Number = "xxxxxxxxxxxxxx"
#Replace xxxxx with the number which will be sending SMS to PiTalk

while True:
    """ Check for new SMS flag """
    if phone.flag_newSMS:
        # Make flag false
        phone.flag_newSMS = False
        messageData = phone.messageList
        print("\nNew SMS Recieved.....")

        # Check the SMS sender Number
        if messageData[0] == My_Number:
            print("\nMessage Sender - " + str(messageData[0]))

            # Check message data
            if (messageData[2].rstrip()) == "Relay 1 ON":  #You can customize this message to something else.
                #It turns relay 1 ON if the Text matches.
                relay1.on()
                # You can send message for update/notification
                # sendSMS("1234567890", "Your Message")
            elif messageData[2].rstrip() == "Relay 1 OFF":
                #It turns relay 1 OFF if the Text matches.
                relay1.off()        
            elif messageData[2].rstrip() == "Relay 2 ON":
                relay2.on()
            elif messageData[2].rstrip() == "Relay 2 OFF":
                relay2.off()
            elif messageData[2].rstrip() == "Relay 3 ON":
                relay3.on()
            elif messageData[2].rstrip() == "Relay 3 OFF":
                relay3.off()
            elif messageData[2].rstrip() == "Relay 4 ON":
                relay4.on()
            elif messageData[2].rstrip() == "Relay 4 OFF":
                relay4.off()
