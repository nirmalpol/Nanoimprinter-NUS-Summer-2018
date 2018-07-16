	# =========================================================================
	# FILE NAME :  monitorClass.py
	# AUTHOR :     Nicolas Tarino
	# PURPOSE :    This file contains the monitorClass class to collate temperature and pressure Input reading
	#              **** Requires UI dataLogClass logfilefrommain to record info to ****
	#              **** Requires UI function displayMessage to add comment to UI log ****
	#              Passes information to dataLogClass for graph compiling (2 Hz)
	#              Reads data from thermocouple and pressure regulator (20 Hz)
	#              Main UI can read the data directly using self.T or self.P (e.g. self.monitor.T)
	#
	#              pressureread not available
	# =========================================================================

import time
from max31865 import max31865 as rtd
# import pressureread as pread
import dataLogClass as log

class monitorClass:

	def __init__(self,logfilefrommain,displayMessage):
		self.T = 0  	# CENTER
		self.T2 = 0 	# EDGE
		self.P = 0

		self.T_bfr = 0
		self.T2_bfr = 0
		self.P_bfr = 0

		# Setup thermocouple
		# =======================
		self.rtd1 = rtd(26)
		self.rtd2 = rtd(13)

		# Setup pressure control
		# =======================
		# self.pre1 = pread.setup()

		# Setup time for plotting and timekeeping
		# =======================
		self.start_time = time.time()
		self.curr_time = time.time() - self.start_time

		#Log used for graph plotting
		self.logfile = logfilefrommain
		self.displayMessage = displayMessage

	def readval(self): #Activates often at about 5 Hz / each 200 ms
		self.T_bfr = self.T
		self.T2_bfr = self.T2
		# self.P_bfr = self.P

		#Raw readings
		# self.T = self.rtd1.readTemp()
		# self.T2 = self.rtd2.readTemp()

		#Time decayed readings
		self.T = (2*self.rtd1.readTemp()+3*self.T_bfr)/5 	#Time consuming due to 100 ms sleep
		self.T2 = (2*self.rtd2.readTemp()+3*self.T2_bfr)/5
		# self.P = pread.read(pre1)

		self.curr_time = time.time() - self.start_time

	def asktime(self):
		return (time.time() - self.start_time)

	def sendval(self): #Activates less often at about 1 Hz / each 1000 ms
		self.logfile.updateFromMonitor(self.curr_time,self.T,self.T2,self.P)
		self.displayMessage("T ({0:.02f}) =  {1:.04f}".format( self.curr_time, self.T  ),'M') #Comments with M for logMonitor
		self.displayMessage("Te({0:.02f}) =  {1:.04f}".format( self.curr_time, self.T2  ),'M')#Comments with M for logMonitor
		self.displayMessage("P ({0:.02f}) =  {1:.04f}".format( self.curr_time, self.P  ),'M') #Comments with M for logMonitor


