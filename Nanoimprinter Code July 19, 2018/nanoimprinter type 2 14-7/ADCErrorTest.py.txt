#!/usr/bin/python
#MAX11100 Software Program
'''
File Name: ADCErrorTest.py
Authors: Nirmal Pol and Raghav Srinivasan
Date: July 18, 2018

Description: This code allows the user to plot the error that is produced by the MAX11100 ADC. It also provides the user with the
standard deviation and an equation that models the error. This way, the user can adjust the output of the MAX11100 to remove the 
error that is produced.

Note: The Raspberry Pi is connected to the AD5760 DAC which uses the AD5760.py file. The AD5760's output voltage is connected to
the MAX11100 ADC input which utilizes the MAX11100.py file. Finally, the output of the MAX111000's output digital signal is 
connected back to the Raspberry Pi for reading and producing the graph.
'''


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
actual = 0            #Start at 0V
for i in range(0, 100):
        #Configure the DAC to output voltage values that start at 0V and increment by 1V until it reaches 10V.
        
        dac.setVoltage(int(a))
        dac.update()
        time.sleep(0.05)
        val = adc.readVoltage()
        print (val)
        x = x + [actual]
        y = y + [val]
        e = e + [abs(val - actual)]            #Calculate the error
        actual = (actual + 1)%11               #Increment the voltage by 1V
        a = actual*(6553.5)     

#Plot and produce an equation along with the standard deviation.

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
        
