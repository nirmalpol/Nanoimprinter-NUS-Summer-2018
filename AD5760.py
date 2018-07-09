#!/usr/bin/python
#AD5760 Software Program
'''
File Name: AD5760.py
Authors: Nirmal Pol and Raghav Srinivasan
Date: July 09, 2018
Description: This code allows someone to manipulate the AD5760 Digital to Analog converter (DAC) using a 
Raspberry Pi. This code was tested using the evaluation board for this specific DAC, and with the following connections:
Note: The numbering system uses the GPIO.BCM mode as reference
SYNC connected to CE0 (GPIO pin 8)
CLK connected to SCLC (GPIO pin 11)
SDIN connected to MOSI (GPIO pin 10)
SDO connected to MISO (GPIO pin 9)
LDAC connected to GPIO pin 19 (for update purposes)
In addition, the Digital supply Vcc was connected to the Raspberry Pi 3.3 V DC Power supply (Pin 01 in GPIO.BOARD mode), and 
DGND is connected to the ground of the Raspberry Pi.

The Analog supply has Vdd (positive supply) at 13 V and Vss (negative supply) at -7.5 V, with a common ground AGND between them.

Overall, this code allows the user to control the output analog voltage from 0-10V using numbers from 0-65535.

'''
import time, math
import RPi.GPIO as GPIO

class ad5760(object):
        def __init__(self, csPin = 8, misoPin = 9, mosiPin = 10, clkPin = 11, ldac = 19):
                #Initializes the ad5760 object and sets all the parameters and GPIO values:
                
                #Creates constants for all the pins being used:
                self.csPin = csPin
                self.misoPin = misoPin
                self.mosiPin = mosiPin
                self.clkPin = clkPin
                self.ldac = ldac
                
                #Sets the GPIO mode and sets the different pins to input or output:
                GPIO.setwarnings(False)
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.csPin, GPIO.OUT)
                GPIO.setup(self.misoPin, GPIO.IN)
                GPIO.setup(self.mosiPin, GPIO.OUT)
                GPIO.setup(self.clkPin, GPIO.OUT)
                GPIO.setup(self.ldac, GPIO.OUT)
                
                GPIO.output(self.csPin, GPIO.HIGH)
                GPIO.output(self.clkPin, GPIO.LOW)
                GPIO.output(self.mosiPin, GPIO.LOW)

        def setVoltage(self, value):
                """  This method takes in a value from 0 to 65535 (as this DAC is 16 bits) and outputs the corresponding voltage.
                     Example: Sending a value of 0 causes DAC to output 0V
                              Sending a value of 65535 causes DAC to output 10V
                """
                GPIO.output(self.csPin, GPIO.LOW)
                
                output = 0x100000   #R/W = 0 for writing; Address is 001; These set the first 4 bits (MSB), with rest set by the user
                if value > 65535:
                        value = 65535
                if value < 0:
                        value = 0
                        
                #The last 4 bits for the 24 bit "word" we write don't matter,
                output |= (value << 4) 
                
                #So we have 4 bits for the preface, 16 databits, and 4 bits at the end (LSB side) that don't matter
                #Split the output into the 3 bytes it is made of, and send them separately to the DAC with the sendByte method:
                highByte = (output >> 16) & 0xff
                midByte = (output >> 8) & 0xff
                lowByte = (output) & 0xff
                self.sendByte(highByte)
                self.sendByte(midByte)
                self.sendByte(lowByte)
                
                GPIO.output(self.csPin, GPIO.HIGH)
                
        def sendByte(self,byte):
                '''This function causes the MOSI pin to turn 1 or 0 at each iteration of the loop'''

                for bit in range(8):
                        GPIO.output(self.clkPin, GPIO.HIGH)
                        if (byte & 0x80):
                                GPIO.output(self.mosiPin, GPIO.HIGH)
                        else:
                                GPIO.output(self.mosiPin, GPIO.LOW)
                        byte <<= 1
                        GPIO.output(self.clkPin, GPIO.LOW)

        def setup(self):
                '''
                GPIO.output(self.csPin, GPIO.LOW)
                softreg = 0x400006              #0100...0110
                highB = (softreg >> 16) & 0xff
                midB = (softreg >> 8) & 0xff
                lowB = (softreg) & 0xff
                self.sendByte(highB)
                self.sendByte(midB)
                self.sendByte(lowB)
                GPIO.output(self.csPin, GPIO.HIGH)
                time.sleep(2)
                '''
                GPIO.output(self.csPin, GPIO.LOW)
                softreg = 0x400000              #0100...0000
                highB = (softreg >> 16) & 0xff
                midB = (softreg >> 8) & 0xff
                lowB = (softreg) & 0xff
                self.sendByte(highB)
                self.sendByte(midB)
                self.sendByte(lowB)
                GPIO.output(self.csPin, GPIO.HIGH)
                
                output = 0x200012                       #0010...0001 0010
                GPIO.output(self.csPin, GPIO.LOW)
                highByte = (output >> 16) & 0xff
                midByte = (output >> 8) & 0xff
                lowByte = (output) & 0xff
                self.sendByte(highByte)
                self.sendByte(midByte)
                self.sendByte(lowByte)
                GPIO.output(self.csPin, GPIO.HIGH)

        def reset(self):
                GPIO.output(self.csPin, GPIO.LOW)
                softreg = 0x400007              #0100...0111
                highB = (softreg >> 16) & 0xff
                midB = (softreg >> 8) & 0xff
                lowB = (softreg) & 0xff
                print(highB,',',midB,',',lowB)
                self.sendByte(highB)
                self.sendByte(midB)
                self.sendByte(lowB)
                GPIO.output(self.csPin, GPIO.HIGH)

                time.sleep(5)
                
                GPIO.output(self.csPin, GPIO.LOW)
                softreg = 0x400000              #0100...0111
                highB = (softreg >> 16) & 0xff
                midB = (softreg >> 8) & 0xff
                lowB = (softreg) & 0xff
                print(highB,',',midB,',',lowB)
                
                self.sendByte(highB)
                self.sendByte(midB)
                self.sendByte(lowB)
                GPIO.output(self.csPin, GPIO.HIGH)

        def update(self):
                GPIO.output(self.ldac, GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(self.ldac, GPIO.LOW)



if __name__ == "__main__":

        csPin = 8
        misoPin = 9
        mosiPin = 10
        clkPin = 11
        ldac = 19
        dac = ad5760(csPin,misoPin,mosiPin,clkPin, ldac)
        dac.setup()
        a = 0
        try:
                while True:
                        dac.setVoltage(0)
                        time.sleep(0.2)
                        print('repeat')
                        dac.update()
                        a = (a + 100) % (66000)
                        print(a)
                        
        finally:
                GPIO.cleanup()
                #dac.close()
