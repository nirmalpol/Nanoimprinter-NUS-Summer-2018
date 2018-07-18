
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
		# PWM ranges from 0 to 100 (by heatctrl)
		self.pwm_center = 0
		self.pwm_edge = 0
		# DAC controller is used to control pressure
		# DAC input ranges from 0 to 35 (by the pressureController)
		self.dac_pres = 0

		#NOTE that only pwm_center, pwm_edge and dac_pres are proper to be used to 
		# change DutyCycle/output

		# These variables will have ONLY current temp values and targets written to them.
		self.T_center = 0
		self.T_edge = 0
		self.target_T_center = 0
		self.target_T_edge = 0
		# These variables will have ONLY current pressure values written to them
		self.P = 0
		self.target_P = 0
		# Variables used for timekeeping.
		self.start_time = time.time()
		self.curr_time = time.time()

		#Below here are the two separate methods to contol the heater:
		# Which mode to use.
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

		if self.T_mode == 'PWM':
			pass
		elif self.T_mode == 'PID':
			# Update PID Temp
			self.pid_center.update(self.target_T_center - self.T_center)
			self.pwm_center = self.pid_center.output
			self.pid_edge.update(self.target_T_edge - self.T_edge)
			self.pwm_edge = self.pid_edge.output
		elif self.T_mode == None:
			raise #Error
		else:
			raise #Error
		self.pin_1.change_duty(self.pwm_center)
		self.pin_2.change_duty(self.pwm_edge)

		# Command Pressure Temp
		self.dac_pres = self.target_P
		self.pin_3.setPressure(self.dac_pres)

	#Write to log
	def sendval(self):
		#send to log
		self.curr_time = time.time() - self.start_time
		self.logfile.updateFromProcess(self.curr_time,self.pwm_center,self.pwm_edge,self.dac_pres,self.target_T,self.target_P)


	# Data to load:
	# ===================
	# Only accepts data from ONE phase at a time.
	# To change phase, load data first before running

	#NOT DONE
	def loadData(self,seqcp):	
		#seqcp stands for SEQuence at Current Phase
		# seqcp file is organized as:	
		# Example of a seqcp file: ['Heating   ',1,0,80,0,0,100,2,2,5,1,1]
		# [0] Descriptor 'Heating'
		# [1] Endcondition '1'
		#		(0) Click to Proceed/ Will not stop automaticallu
		#		(1) Reach Temp
		#		(2) Reach Pressure
		#		(3) Wait for time to pass
		#		(4) Immediately skip/ Temporarily 'delete' a phase
		# [2] Target T '80'
		#		Has value from 30 to 170, minimum step of 0.1 C
		# [3] Target P (over Kapton) '0'
		#		Has value from 0 to 35 bars, minimum step of 0.1 bar
		# [4] Heating Profile '0'
		#		(0) Rapid/ output = 100%
		#		(1) PID Controlled
		#		(2) Off/ output = 0%
		#		(3) PWM/ constant output from 0 to 100%
		#		(4) Custom/ Space to add new controls. 
		#			E.g. to create new PID while retaining past integral sums

		#The following 5 to 8 will be hidden if the Detailed checkbox is off
		#The following 5 to 9 controls will need deciding. I don't believe PID control
		#is optimal, and I'm leaning to using LTI control
		# [5] Constant Heat Output '100'
		#		Only visible if [5] Profile == 0,2 or 3
		#		Only active if [5] Profile == 3
		# [6] Kp '2'
		#		Only active and visible if [5] Profile == 1
		# [7] Ki '2'
		# [8] Kd '5'

		# [9] (NOT CONTROLLABLE BY UI) Bottom of Kapton Vacuum '1'
		# [10] (BAD IDEA) Cool Air '1'

		self.setTarget(seqcp[2],seqcp[2],seqcp[3])
		if seqcp[4] == 1:
			self.T_mode = 'PID'
			self.setTempPID(seqcp[6],seqcp[7],seqcp[8],seqcp[6],seqcp[7],seqcp[8])
		elif seqcp[4] == 0 or seqcp[4] == 2 or seqcp[4] == 3:
			self.T_mode = 'PWM'
			self.setTempPWM(seqcp[5])
		else:
			self.T_mode = None

		self.transition()

	def setTarget(self,newTcenter=20,newTedge=20,newP=20):
		self.target_T_center = newTcenter #From seq[][]
		self.target_T_edge = newTedge #From seq[][]
		self.target_P = newP

	def setTempPID(self,a=1,b=0,c=0,d=1,e=0,f=0):
		self.pid_center.setKp(a)
		self.pid_center.setKi(b)
		self.pid_center.setKd(c)

		self.pid_edge.setKp(d)
		self.pid_edge.setKi(e)
		self.pid_edge.setKd(f)

	def setTempPWM(self,newPWM=0):
		self.pwm_center = newPWM
		self.pwm_edge = newPWM

	def transition(self):
	#Similar to self.setup where it is used to reset controls
	#But only reset past phases (e.g. past PID control)
		self.pid_edge = pid_setup.pid_setup_edge(self.temp,0,0,0)
		self.pid_center = pid_setup.pid_setup_center(self.temp,0,0,0)

	# Closing:
	# ==================
	def close(self):
		self.pin_1.change_duty(0)
		self.pin_2.change_duty(0)
		self.pin_3.setPressure(0)
		self.pin_1.close()
		self.pin_2.close()
		self.pin_3.close()

