#!/usr/bin/python
#MAX11100 Software Program

import time, math
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
from MAX11100 import max11100
from AD5760 import ad5760
import numpy as np
import csv

csPin = 7
misoPin = 9
mosiPin = 10
clkPin = 11
ldac = 19
adc = max11100(csPin,misoPin,clkPin)
dac = ad5760(8, misoPin, mosiPin, clkPin, ldac)
dac.setup()
x = []
y = []
e = []
a = 0
actual = 0
for i in range(0, 100):
        dac.setVoltage(int(a))
        dac.update()
        time.sleep(0.05)
        val = adc.readVoltage()
        print (val)
        x = x + [actual]
        y = y + [val]
        e = e + [abs(val - actual)]
        actual = (actual + 1)%11
        a = actual*(6553.5)
                        
GPIO.cleanup()
plt.plot(x, e, 'ro')
plt.xlabel("DAC Voltage (V)")
plt.ylabel("Absolute Value of ADC Error (V)")
plt.title("ADC Error Values with Increasing Voltage")
(m, b) = np.polyfit(x, e, 1)
equation = 'y = ' + str(round(m, 4)) + 'x + ' + str(round(b, 4))
plt.text(1, 0, equation)
stdev = np.std(e)
stdevp = 'Standard Deviation: ' + str(round(stdev, 4))
plt.text(5, 0, stdevp)
plt.show()
        
