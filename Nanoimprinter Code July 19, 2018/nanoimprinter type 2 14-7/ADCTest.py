#!/usr/bin/python
#MAX11100 Software Program

import time, math
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
from MAX11100 import max11100

csPin = 7
misoPin = 9
clkPin = 11
adc = max11100(csPin,misoPin,clkPin)
y = []
try:
        while True:
                val = adc.readVoltage()
                print (val)
                time.sleep(2)
                y = y + [val]  
                        
finally:
        x = range(0, len(y))
        GPIO.cleanup()
        plt.plot(x, y)
        plt.show()
        #dac.close()
        
