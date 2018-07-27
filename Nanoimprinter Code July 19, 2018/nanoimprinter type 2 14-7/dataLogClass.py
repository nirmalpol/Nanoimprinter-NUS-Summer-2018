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
import json

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
		self.temps_targets = []
		self.pressures_targets = []

		self.times3 = [] #Stores times when Phase changes occur


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
		
		self.graphic.ax1 = self.graphic.figure.add_subplot(211)
		self.graphic.ax1.set_ylabel('Pressure / bar')
		self.graphic.ax1.set_title('Pressure')
		self.graphic.ax1.grid(color='grey', linestyle='dotted', linewidth=2)

		self.graphic.ax2 = self.graphic.figure.add_subplot(212)
		self.graphic.ax2.set_xlabel('Time / second')
		self.graphic.ax2.set_ylabel('Temperature / C')
		self.graphic.ax2.set_title('Temperature')
		self.graphic.ax2.grid(color='grey', linestyle='dotted', linewidth=2)



	# Update functions
	# ==========================================================

	def updateGraph(self):
		# print('redraw all with new data {} on graph {}'.format(str(1)),str(2))
		
		timespan = [self.graphinfo[0][2],self.graphinfo[0][2]+self.graphinfo[0][0]]
		Tspan = self.graphinfo[1]
		Pspan = self.graphinfo[2]

		self.graphic.figure.clear()

		self.graphic.ax1 = self.graphic.figure.add_subplot(211)
		self.graphic.ax1.plot(self.times,self.pressures,**{'marker' : 'x','color':'black'})
		self.graphic.ax1.set_xlim(timespan)
		self.graphic.ax1.set_ylim(Pspan)
		self.graphic.ax1.set_ylabel('Pressure / bar')
		self.graphic.ax1.set_title('Pressure')
		self.graphic.ax1.grid(color='grey', linestyle='dotted', linewidth=2)
		self.graphic.canvas.draw()

		self.graphic.ax2 = self.graphic.figure.add_subplot(212)
		self.graphic.ax2.plot(self.times,self.temps_cent,**{'marker' : 'x','color':'red'})
		self.graphic.ax2.plot(self.times,self.temps_edge,**{'marker' : 'x','color':'blue'})
		self.graphic.ax2.set_xlim(timespan)
		self.graphic.ax2.set_xlim(Tspan)
		self.graphic.ax2.set_xlabel('Time / second')
		self.graphic.ax2.set_ylabel('Temperature / C')
		self.graphic.ax2.set_title('Temperature')
		self.graphic.ax2.grid(color='grey', linestyle='dotted', linewidth=2)
		self.graphic.canvas.draw()

		self.graphic.ax1.plot(self.times,self.pressures_targets,**{'color':'green'})
		for xintercept in self.times3:
			self.graphic.ax1.axvline(x=xintercept)

		self.graphic.ax2.plot(self.times,self.temps_targets,**{'color':'green'})
		for xintercept in self.times3:
			self.graphic.ax1.axvline(x=xintercept)


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
		self.updateGraph()

	def updateFromProcess(self,curr_time,pwm,pwm2,pwm3,trgtT,trgtP):
		self.times2.append(curr_time)
		self.temps_pwm_cent.append(pwm)
		self.temps_pwm_edge.append(pwm2)
		self.pressures_pwm.append(pwm3)
		self.temps_targets.append(trgtT)
		self.pressures_targets.append(trgtP)

		#Extend Span if needed
		if self.graphinfo[0][0]+self.graphinfo[0][2] < curr_time:
			self.graphinfo[0][2] += self.graphinfo[0][1]


	def updateVerticalLine(self,curr_time):
		self.times3.append(curr_time)

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

	def loadData(self,sourceFile):
		with open(sourceFile,"r") as read_file:
			data = json.load(read_file)
			combined_log = data[0]
			self.logGeneral = combined_log[0]
			self.logMonitor = combined_log[1]
			self.logProcess = combined_log[2]

			combined_graph = data[1]
			self.graphinfo = combined_graph[0]

			readings = combined_graph[1]
			self.times = readings[0]
			self.temps_cent = readings[1]
			self.temps_edge = readings[2]
			
			controls = combined_graph[2]
			self.times2 = controls[0]
			self.temps_pwm_cent = controls[1]
			self.temps_pwm_edge = controls[2]
			self.pressures_pwm = controls[3]
			self.temps_targets = controls[4]
			self.pressures_targets  = controls[5]

			phasers = combined_graph[3]
			self.times3 = phasers[0]
			
		self.updateGraph()

	def saveData(self,targetfile):
		with open(targetfile,"w") as write_file:
			combined_log = [self.logGeneral,self.logMonitor,self.logProcess]

			readings = [self.times,self.temps_cent,self.temps_edge,self.pressures]
			controls = [self.times2,self.temps_pwm_cent,self.temps_pwm_edge,self.pressures_pwm,self.temps_targets,self.pressures_targets]			
			phasers = [self.times3]

			combined_graph = [self.graphinfo,readings,controls,phasers]

			outputToFile = [combined_log,combined_graph
			json.dump(outputToFile,write_file)
