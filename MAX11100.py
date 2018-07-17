#!/usr/bin/python
#MAX11100 Software Program

import time, math
import RPi.GPIO as GPIO

class max11100(object):
    def __init__(self, csPin = 7, misoPin = 9, clkPin = 11):
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

    def recvByte(self):
        byte = 0x00
        for bit in range(8):
            GPIO.output(self.clkPin, GPIO.HIGH)
            byte <<= 1
            if GPIO.input(self.misoPin):
                byte |= 0x1
            GPIO.output(self.clkPin, GPIO.LOW)
        return byte

    def readVoltage(self):
        '''The ADC outputs the first 8 bits as leading zeros with the following
        8 bits and the last 8 bits containing the 16 bits of data'''
        GPIO.output(self.csPin, GPIO.LOW)
        leadzeros = self.recvByte()
        value1 = self.recvByte()
        value2 = self.recvByte()
        GPIO.output(self.csPin, GPIO.HIGH)
        time.sleep(0.01)
        rval = (value1 << 8) | value2
        #Convert to decimal:
        volt = (rval*10.0)/65535
        return volt
        
