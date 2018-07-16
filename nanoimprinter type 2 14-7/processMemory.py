
	# =========================================================================
	# FILE NAME :  processMemory.py
	# AUTHOR :     Nicolas Tarino
	# PURPOSE :    This file contains the processMemory class to collate temperature and pressure Input reading
	#              ****Requires UI dataLogClass logfilefrommain to report info to****
	#              ****Requires UI monitorClass monitorfrommain to read data from****
	#              ****Requires UI function displayMessage to add comment to UI log****
	#              Passes information to dataLogClass for graph compiling (2 Hz)
	#              Reads data from thermocouple and pressure regulator (20 Hz)
	#              Main UI can read the data directly using self.T or self.P (e.g. self.monitor.T)
	#              
	#              Edited from Yu Dong (Peter) Feng and Dylan Vogel's heatingProcess.py
	#              Edited from Raghav and Nirmal's pressureController.py
		# **************************************************************
		# *   FILE NAME:      heatingProcess.py
		# *   AUTHOR:         Yu Dong (Peter) Feng, Dylan Vogel
		# *   PURPOSE:        This file contains the heatingProcess class, which is used for heating and temperature tests.
		# **************************************************************
	#              
	# =========================================================================


# import pid_setup
import dataLogClass as log
import monitorClass
import pressureController as pres
import heatctrl
import time

import RPi.GPIO as GPIO

class processMemory:
	def __init__(self,logfilefrommain,displayMessage,monitorfrommain):
	# Listed here are all the methods usable
		#Setup datalog
		self.logfile = logfilefrommain
		self.displayMessage = displayMessage
		self.monitorfile = monitorfrommain

	# Listed here are all the stored variables
		# The PWM duty used for the initial heating. Generally around 50% for the
		# center and 100% for the edge seems to work. Should be adjusted based on
		# changes to the thermal volume based on empirical results.
		# PWM ranges from 0 to 100
		self.pwm_center = 0
		self.pwm_edge = 0
		self.pwm_pres = 0

		# These variables will have ONLY current temp values and targets written to them.
		self.T_center = 0
		self.T_edge = 0
		self.target_T = 0
		# These variables will have ONLY current pressure values written to them
		self.P = 0
		self.target_P = 0
		# Variables used for timekeeping.
		self.start_time = time.time()
		self.curr_time = time.time()

		#Below here are the two separate methods to contol the heater:
		# Which mode to use. Yes for PWM, No for PID
		self.T_mode = None

		self.setup()

	#This function is called upon creating processMemory, or when resetting controllers
	def setup(self):
		#The following are non-direct control methods employed
		#Setup PID
		self.pid_edge = pid_setup.pid_setup_edge(self.temp,0,0,0)
		self.pid_center = pid_setup.pid_setup_center(self.temp,0,0,0)

		#The following are the direct control pins output
		#Setup heater
		self.pin_1 = heatctrl.setup1()
		self.pin_2 = heatctrl.setup2()

		#Setup Pres Regulator
		self.pin_3 = pres.pressureController()

		#Set outputs to off
		self.pin_1.change_duty(0)
		self.pin_2.change_duty(0)
		self.pin_3.setPressure(0)

	#A one-shot function, changing outputs only once
	def run(self):
		# Get Current T
		self.T_center = self.monitorfile.T
		self.T_edge = self.monitorfile.T2

		if self.T_mode == True:
			self.pwm_center = self.T_pwm
		elif self.T_mode == False:
			# Update PID Temp
			self.pid_center.update(self.target_T - self.T_center)
			self.pwm_center = self.pid_center.output
			self.pid_edge.update(self.target_T - self.T_edge)
			self.pwm_edge = self.pid_edge.output
		elif self.T_mode == None:
			return #Error
		else:
			return #Error
		self.pin_1.change_duty(self.pwm_center)
		self.pin_2.change_duty(self.pwm_edge)

		# Command Pressure Temp
		self.pwm_pres = self.target_P
		self.pin_3.setPressure(self.pwm_pres)

	#Write to log
	def sendval(self):
		#send to log
		self.curr_time = time.time() - self.start_time
		self.logfile.updateFromProcess(self.curr_time,self.pwm_center,self.pwm_edge,self.pwm_pres,self.target_T,self.target_P)


	# Data to load:
	# ===================
	def loadData(self):		
		self.setTarget()
		self.setTempPID() #not complete

	def setTempPID(self,a=1,b=0,c=0,d=1,e=0,f=0):
		self.pid_center.setKp(a)
		self.pid_center.setKi(b)
		self.pid_center.setKd(c)

		self.pid_edge.setKp(d)
		self.pid_edge.setKi(e)
		self.pid_edge.setKd(f)

	def setTarget(self,newT=20,newP=20):
		self.target_T = newT #From seq[][]
		self.target_P = newP

	# Closing:
	# ==================
	def close(self):
		self.pin_1.change_duty(0)
		self.pin_2.change_duty(0)
		self.pin_3.setPressure(0)
		self.pin_1.close()
		self.pin_2.close()
		self.pin_3.close()

