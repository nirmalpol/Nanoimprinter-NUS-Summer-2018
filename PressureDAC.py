#!/usr/bin/python

"""
Python Library for MCP4922 DAC using Raspberry Pi 3 Model B+
2 Channels, 12 Bit
Currently only supports Hardware SPI
Requires: RPi.GPIO & spidev libraries
Wiring:
MCP4922    =======>   Raspberry Pi
CS         ------->   GPIO08 Physical Pin 24 (SPI0 CE0) => Can be changed
SDI        ------->   GPIO10 Physical Pin 19 (SPI0 MOSI) => cannot be changed in hardware SPI MODE
SCK        ------->   GPIO11 Physical Pin 23 (SPI0 SCLK) => cannot be changed in hardware SPI MODE
MIT License
Copyright (c) 2017 mrwunderbar666
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
**************************************************************************************
*This File is Modified By: Raghav Srinivasan and Nirmal Pol
*File Name: PressureDAC.py
*Purpose: To control the DAC that will be used to manipulate the Equilibar
          pressure regulator for the nanoimprinter project. The code written
          for the MCP4922 will be modified to suit the AD5760 DAC from Analog
          Devices, that is being used for this project. This DAC is 1 channel and 16 bits.
          
***************************************************************************************
"""
 
import RPi.GPIO as GPIO
import spidev


class AD5760(object):
    """ Class for the Microchip AD5760 digital to analog converter
    """
    spi = spidev.SpiDev()

    def __init__(self,
                 spibus=None,
                 spidevice=None,
                 cs=None
                 ):
        """ Initialize AD5760 device with hardware SPI
            Chipselect default value is BCM Pin 8 (Physical Pin: 24)
            Select the bus and device number. Default values are:
            Bus = 0 ; Device = 1
            If you're not sure, just leave it default
        """
        mode = GPIO.getmode()
        if mode == GPIO.BOARD:
            default_cs = 24
        elif mode == GPIO.BCM:
            default_cs = 8
        else:
            raise ValueError(
                "You haven't selected a GPIO Mode? Use: e.g. GPIO.setmode(GPIO.BCM)")

        if cs is None:
            self.cs = default_cs
        else:
            self.cs = cs

        if spibus is None:
            self.spibus = 0
        else:
            self.spibus = spibus

        if spidevice is None:
            self.spidevice = 0
        else:
            self.spidevice = spidevice

        GPIO.setup(self.cs, GPIO.OUT)
        GPIO.output(self.cs, 1)
        # As soon as AD5760 object is created spidev bus and device are opened
        # otherwise causes memory leak and creates Errno 24
        self.spi.open(self.spibus, self.spidevice)

    def setVoltage(self, value):
        """
        Regular setVoltage Function
        Select Voltage value 0 to 65535
        """
        output = 0x100000   #For this DAC: R/W = 0 for writing; Address is 001; These set the first 4 bits (MSB), with the rest set by the user
        
        if value > 65535:
            value = 65535
        if value < 0:
            value = 0
        output |= (value << 4) #For the AD5760, the last 4 bits for the 24 bit "word" we write don't matter, as we only have 16 data bits: 4 for the preface, 16 databits, and 4 at the end (LSB side) that don't matter
        highByte = (output >> 16) & 0xff
        midByte = (output >> 8) & 0xff
        lowByte = (output) & 0xff
          
       
        GPIO.output(self.cs, 0)
        self.spi.writebytes([highByte, midByte, lowByte])
        GPIO.output(self.cs, 1)
  
        return

    def setup(self):
        output = 0x20001e
     
        highByte = (output >> 16) & 0xff
        midByte = (output >> 8) & 0xff
        lowByte = (output) & 0xff

       
        GPIO.output(self.cs, 0)
        self.spi.writebytes([highByte, midByte, lowByte])
        GPIO.output(self.cs, 1)
        return

    def close(self):
        """
        Closes the device
        """
        self.spi.close
        return

    def open(self):
        """
        Manually Open the device
        """
        self.spi.open(self.spibus, self.spidevice)
        return
