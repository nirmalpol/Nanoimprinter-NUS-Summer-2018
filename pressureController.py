#!/usr/bin/python

import time
import RPi.GPIO as GPIO
from AD5760 import ad5760

def setPressure(press):
        if (press > 35):
            press = 35
        if (press < 0):
            press = 0

        step = int((press/35)*65535)

        dac = ad5760()
        dac.setup()
        dac.setVoltage(step)
        dac.update()
        GPIO.cleanup()

def setPressureStep(press, stepSize, delay):
        if (press > 35):
            press = 35
        if (press < 0):
            press = 0

        step = int((press/35)*65535)

        dac = ad5760()
        dac.setup()

        for i in range(0, step, stepSize):
                dac.setVoltage(i)
                time.sleep(delay)
                dac.update()

        dac.setVoltage(step)
        dac.update()
        GPIO.cleanup()


        
