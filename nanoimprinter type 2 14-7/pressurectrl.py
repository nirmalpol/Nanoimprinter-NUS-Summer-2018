
import time
import RPi.GPIO as GPIO

def setup(PWM_PIN_1,freq):
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(PWM_PIN_1,GPIO.OUT)
	pwm_1 = GPIO.PWM(PWM_PIN_1,freq)

	pwm_1.start(0)
	return pwm_1

def change_duty(pwm,new_dutycycle):
	pwm.ChangeDutyCycle(new_dutycycle)

def clamp(n, minn, maxn):
	return max(min(n, maxn), minn)

def close(pwm):
	pwm.stop()
	