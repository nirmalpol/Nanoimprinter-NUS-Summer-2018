#!/usr/bin/python
'''
File Name: pressureController.py
Authors: Nirmal Pol and Raghav Srinivasan
Date: July 10, 2018
Description: This program uses the AD5760 DAC and code to control the Equilibar QBV Electronic Pressure Regulator
that has a pressure range of 0-35 bar, to set the pressure inside of the nanoimprinter. 
'''
import time
import RPi.GPIO as GPIO
from AD5760 import ad5760

def setPressure(press):
        #This function sets the pressure of the pressure regulator immediately, by changing the output
        #voltage of the DAC directly to the voltage corresponding to the desired pressure
        if (press > 35): #Confirming inputs
            press = 35
        if (press < 0):
            press = 0
        #Converting pressure into the step for the DAC:
        step = int((press + 0.3/35)*65535) #Adjustment of 0.3 bar as there is an offset in the actual pressure regulator in practice
        #Set the desired voltage on the DAC: 
        dac = ad5760()
        dac.setup()
        dac.setVoltage(step)
        dac.update()
        GPIO.cleanup()

def setPressureStep(press, stepSize, delay):
        #This function sets the pressure of the pressure regulator gradually, rather than immediately by the 
        #setPressure method. This function inputs stepSize, the amount of steps skipped when ramping up the pressure (more
        #results in less time to increase pressure), and delay, the time delay between each step increase (more results in more
        #time to increase pressure)
        
        if (press > 35):
            press = 35
        if (press < 0):
            press = 0

        step = int((press/35)*65535)

        dac = ad5760()
        dac.setup()
        #For loop to gradually increase pressure: 
        for i in range(0, step, stepSize):
                dac.setVoltage(i)
                time.sleep(delay)
                dac.update()

        dac.setVoltage(step)
        dac.update()
        GPIO.cleanup()


        
