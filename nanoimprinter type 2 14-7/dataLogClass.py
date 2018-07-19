	# =========================================================================
	# FILE NAME :  dataLogClass.py
	# AUTHOR :     Nicolas Tarino
	# PURPOSE :    This file contains the dataLogClass class to record input/output data, put them in graphs, 
	#				and enable loading of data from previous logs
	#              **** REQUIRES UI WIDGET graphfrommain TO CREATE UI GRAPH ****
	#              Receives data from processMemory and monitorClass (about 2 Hz)
	#              Orders Main UI how to window the graphs
	#              Manages 3 logs (General, Monitor and Process)
	#              Allows loading of previous logs/saving of current log
	#              
	#              Load/Saving not avaliable
	# =========================================================================

import numpy as np
from PyQt5.QtWidgets import *

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class dataLogClass():
	def __init__(self,graphfrommain):
		self.createVars()
		self.graphic = graphfrommain

	# Initializer functions
	# ==========================================================
	def createVars(self):
		self.logGeneral = []
		self.logMonitor = []
		self.logProcess = []

		self.times = [] # Stores x-coordinate time points, and their corresponding values
		self.temps_cent = []
		self.temps_edge = []
		self.pressures = []

		self.times2 = [] #Stores time/x-axis for 2nd graph, and the corresponding pwm outputs
		self.temps_pwm_cent = []
		self.temps_pwm_edge = []
		self.pressures_pwm = []

		self.times3 = [] #Stores times when Phase changes occur

		self.temps_targets = []
		self.pressures_targets = []

		# Hidden data used to build graphs. Graph spans 120 seconds, 
		# and scrolls left every 30 seconds nearing edge, Starts at 0 Second from start of UI
		# Initial T span is 20 to 80 C
		# Initial P span is -5 to 10 bar
		self.graphinfo = [[120,30,0],[20,80],[-5,10]] 

	def createGraphs(self):

		self.graphic.figure = plt.figure()
		self.graphic.canvas = FigureCanvas(self.graphic.figure)
		self.graphic.toolbar = NavigationToolbar(self.graphic.canvas, self.graphic)
		self.graphic.layout = QVBoxLayout()
		self.graphic.layout.addWidget(self.graphic.toolbar)
		self.graphic.layout.addWidget(self.graphic.canvas)
		self.graphic.setLayout(self.graphic.layout)
		self.graphic.canvas.draw()

		self.graphic.figure.clear()

		#Dummy Graph
		# t = np.arange(0,10,0.5)
		# y = 50* np.sin(t)
		# y2 = 50* np.cos(t)
		
		# self.graphic.ax1 = self.graphic.figure.add_subplot(211)
		# self.graphic.ax1.plot(t,y2,**{'marker' : 'x','color':'black'})
		# self.graphic.ax1.plot(t,y/25+51,**{'color':'green'})
		# self.graphic.ax1.set_xlim([0,20])
		# self.graphic.ax1.set_ylabel('Pressure / bar')
		# self.graphic.ax1.set_title('Pressure')
		# self.graphic.ax1.grid(color='grey', linestyle='dotted', linewidth=2)
		# self.graphic.canvas.draw()

		# self.graphic.ax2 = self.graphic.figure.add_subplot(212)
		# self.graphic.ax2.plot(t,y,**{'marker' : 'x','color':'red'})
		# self.graphic.ax2.plot(t,y2,**{'marker' : 'x','color':'blue'})
		# self.graphic.ax2.plot(t,y2/25+51,**{'color':'green'})
		# self.graphic.ax2.set_xlim([0,20])
		# self.graphic.ax2.set_xlabel('Time / second')
		# self.graphic.ax2.set_ylabel('Temperature / C')
		# self.graphic.ax2.set_title('Temperature')
		# self.graphic.ax2.grid(color='grey', linestyle='dotted', linewidth=2)
		# self.graphic.canvas.draw()



	# Update functions
	# ==========================================================

	def updateGraph(self):
		# print('redraw all with new data {} on graph {}'.format(str(1)),str(2))
		
		timespan = [self.graphinfo[0][2],self.graphinfo[0][2]+self.graphinfo[0][0]]
		Tspan = self.graphinfo[1]
		Pspan = self.graphinfo[2]

		self.graphic.figure.clear()

		self.graphic.ax1.plot(self.times,self.pressures,**{'marker' : 'x','color':'black'})
		self.graphic.ax1.plot(self.times,self.pressures_targets,**{'color':'green'})
		for xintercept in self.times3:
			self.graphic.ax1.axvline(x=xintercept)
		self.graphic.ax1.set_xlim(timespan)
		self.graphic.ax1.set_ylim(Pspan)
		self.graphic.ax1.set_ylabel('Pressure / bar')
		self.graphic.ax1.set_title('Pressure')
		self.graphic.ax1.grid(color='grey', linestyle='dotted', linewidth=2)
		self.graphic.canvas.draw()

		self.graphic.ax2.plot(self.times,self.temps_cent,**{'marker' : 'x','color':'red'})
		self.graphic.ax2.plot(self.times,self.temps_edge,**{'marker' : 'x','color':'blue'})
		self.graphic.ax2.plot(self.times,self.temps_targets,**{'color':'green'})
		for xintercept in self.times3:
			self.graphic.ax1.axvline(x=xintercept)
		self.graphic.ax2.set_xlim(timespan)
		self.graphic.ax2.set_xlim(Tspan)
		self.graphic.ax2.set_xlabel('Time / second')
		self.graphic.ax2.set_ylabel('Temperature / C')
		self.graphic.ax2.set_title('Temperature')
		self.graphic.ax2.grid(color='grey', linestyle='dotted', linewidth=2)
		self.graphic.canvas.draw()


	# Supply Data functions
	# ==========================================================

	def updateFromMonitor(self,curr_time,T,T2,P):
		self.times.append(curr_time)
		self.temps_cent.append(T)
		self.temps_edge.append(T2)
		self.pressures.append(P)

		if self.graphinfo[1][0] > T:
			self.graphinfo[1][0] = T
		if self.graphinfo[1][1] < T:
			self.graphinfo[1][1] = T

		if self.graphinfo[1][0] > T2:
			self.graphinfo[1][0] = T2
		if self.graphinfo[1][1] < T2:
			self.graphinfo[1][1] = T2

		if self.graphinfo[2][0] > P:
			self.graphinfo[2][0] = P
		if self.graphinfo[2][1] < P:
			self.graphinfo[2][1] = P

	def updateFromProcess(self,curr_time,pwm,pwm2,pwm3,trgtT,trgtP):
		self.times2.append(curr_time)
		self.temps_pwm_cent.append(pwm)
		self.temps_pwm_edge.append(pwm2)
		self.pressures_pwm.append(pwm3)

		#Extend Span if needed
		if self.graphinfo[0][0]+self.graphinfo[0][2] < curr_time:
			self.graphinfo[0][2] += self.graphinfo[0][1]

		self.temps_targets.append(trgtT)
		self.pressures_targets.append(trgtT)
		self.updateGraph()

	def updateVerticalLine(self,curr_time):
		self.times3.append(curr_time)

	# def resetMonitor(self):
	# 	self.times = []
	# 	self.temps_cent = []
	# 	self.temps_edge = []
	# 	self.pressures = []
	# 	self.updateGraph()
	# 	self.logMonitor = []

	# def resetProcess(self):
	# 	self.times2 = []
	#	self.times3 = []
	# 	self.temps_pwm_cent = []
	# 	self.temps_pwm_edge = []
	# 	self.pressures_pwm = []
	# 	self.updateGraph()
	# 	self.logProcess = []

	def saveMsg(self,msg,curr_time,purpose):
		if purpose == 'G':
			self.logGeneral.append([curr_time,msg])
		elif purpose == 'P':
			self.logProcess.append([curr_time,msg])
		elif purpose == 'M':
			self.logMonitor.append([curr_time,msg])
		else:
			msg = ''.join('[Error] ',msg)
			self.logGeneral.append([curr_time,msg])

	# NOT DONE
	def loadData(self,sourceFile):
		print('Loading')

	# NOT DONE
	def saveData(self,targetfile):
		print('Creating file')




