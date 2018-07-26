#!/usr/bin/python
#MAX11100 Software Program
'''
File Name: MAX11100.py
Authors: Nirmal Pol and Raghav Srinivasan
Date: July 17, 2018
Description: This software allows the user to read voltage from the MAX11100 ADC using a Raspberry Pi. 
It was tested using the evaluation board, Fresno (MAXREFDES11#), found from the following link:
https://pdfserv.maximintegrated.com/en/an/REFD5563.pdf 

Note: The numbering system uses the GPIO.BCM mode as reference
CS (MAX pin 1) connected to CE1 (GPIO pin 7)
SCLK (Max pin 4) connected to SCLK (GPIO pin 11)
MISO (Max pin 3) connected to MISO (GPIO pin 9)

The MAX11100 GND is connected to the GND of the Raspberry Pi and the 3.3V requirement is also connected to Raspberry Pi's 3.3V signal.
Overall, this code allows the user to read analog voltage from 0-10V and correspond it to the digital numbers from 0-65535.
'''

import time, math
import RPi.GPIO as GPIO

class max11100(object):
    def __init__(self, csPin = 7, misoPin = 9, clkPin = 11):
        ''' Initializes the <MAX11100 object and sets all the parameters and GPIO values
        '''
        
        self.csPin = csPin
        self.misoPin = misoPin
        self.clkPin = clkPin

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.csPin, GPIO.OUT)
        GPIO.setup(self.misoPin, GPIO.IN)
        GPIO.setup(self.clkPin, GPIO.OUT)

        GPIO.output(self.csPin, GPIO.HIGH)
        GPIO.output(self.clkPin, GPIO.LOW)

    def readVoltage(self):
        '''
            The MAX11100 outputs the first 8 bits as leading zeros with the following
            8 bits and the last 8 bits containing the 16 bits of data
        '''
        
        GPIO.output(self.csPin, GPIO.LOW)
        leadzeros = self.recvByte()
        value1 = self.recvByte()
        value2 = self.recvByte()
        GPIO.output(self.csPin, GPIO.HIGH)
        time.sleep(0.01)
        rval = (value1 << 8) | value2
        
        #Convert to decimal:
        volt = (rval*10.0)/65535
        volt = (volt - 0.0001)/0.97675 #Fudge factors as ADC is slightly off
        return volt
    
    def recvByte(self):
        '''
            This method causes the MISO pin to turn 1 or 0 at each iteraation of the loop. It 
            writes one byte of data to the DAC
        '''
        
        byte = 0x00
        for bit in range(8):
            GPIO.output(self.clkPin, GPIO.HIGH)
            byte <<= 1
            if GPIO.input(self.misoPin):
                byte |= 0x1
            GPIO.output(self.clkPin, GPIO.LOW)
        return byte
        
