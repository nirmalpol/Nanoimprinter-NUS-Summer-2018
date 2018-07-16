'''
	************************************************************************
	*   FILE NAME:      heater.py
	*   AUTHOR:         Dylan Vogel, Yu Dong (Peter) Feng
	*   PURPOSE:        This file contains the code for setting up the heaters
	************************************************************************
'''

import RPi.GPIO as GPIO
import thmcouple as thm
global PWM_PIN_1, PWM_PIN_2, freq

# GPIO, not board pins on the RPi
PWM_PIN_1 = 23      # Center
PWM_PIN_2 = 24      # Edge

# PWM frequency in Hz
freq = 500

def setup1():

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(PWM_PIN_1, GPIO.OUT)

	pwm_1 = GPIO.PWM(PWM_PIN_1, freq)

	# Start both PWM channels at 0% duty cycle.
	pwm_1.start(0)

	return pwm_1

def setup2():

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(PWM_PIN_2, GPIO.OUT)

	pwm_2 = GPIO.PWM(PWM_PIN_2, freq)

	# Start both PWM channels at 0% duty cycle.
	pwm_2.start(0)

	return pwm_2

# def calc_kp(work_temp):

# 	kp = 0.2 * ((work_temp / 100.0) * (work_temp / 100.0))
# 	kp = clamp(kp, 0.2, 1)

# 	return kp

# def update_temp(temp_avg, temp):
# 	# Simple weighting scheme to smooth out large variations.
# 	new_temp = ((temp_avg * 2.0) + temp) / 3.0
# 	return new_temp

def change_duty(pwm,new_dutycycle):
	pwm.ChangeDutyCycle(new_dutycycle)

def clamp(n, minn, maxn):
	return max(min(n, maxn), minn)

def close(pwm):
	pwm.stop()
