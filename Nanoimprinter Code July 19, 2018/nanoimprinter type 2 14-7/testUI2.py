
	# =========================================================================
	# FILE NAME :  testUI2.py
	# AUTHOR :     Nicolas Tarino
	# PURPOSE :    This file contains the NanoUI class to handle nanoUI.ui GUI
	#              Sectioned into: Initializers
	# 							   Exit, File Save and Data Log Functions
	# 							   Edit Mode/ Sequence-Log Adjust Functions
	# 							   Run Mode/ Functions
	# 							   Other General Functions
	# 			Memory:
	# 			   Default Sequence Template is contained in tabsInit, as self.seq and self.number_of_phase
	# 			   Items on tabs are saved and can be controlled from stored arrays:
	# 					self.buttonArray, self.settingsArray, self.labelsArray
	# 			   All save-able Information is maintained in dataLogClass class self.log
	# 			   RunTime Actions Information is maintained in processMemory class self.process
	# 			   RunTime Monitor Information is maintained in monitorClass class self.monitor
	# 			   Default Sequence Template is contained in tabsInit, as self.seq and self.number_of_phase
				   
	# 			Action:
	# 			   There are 3 modes this UI can be at:
	# 			   1. Inactive = Ready to start. Monitor and Log active thruout
	# 			   2. Run = Activates Process
	# 			   3. Edit Mode = Alters Sequence tab

	# 			   Classes dataLogClass, processMemory and monitorClass are NOT fixed to this UI
	# 			   The three classes only demand 'displayMessage' function from UI to be accessible
	# 			   The only work this UI do, aside from showing info, is twofold:
	# 			   1. Management of sequences during run, passing each sequence individually to the processMemory
	# 			   2. Handle output files
	# 			   Other jobs are delegated to the three classes
				   
	# =========================================================================


#import QT classes
# from os import path	
import sys
from PyQt5 import QtWidgets,QtCore, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

#Import non-QT classes
import time
import numpy as np
import threading
import traceback

# Import original classes/functions
from processMemory import processMemory
from monitorClass import monitorClass
from dataLogClass import dataLogClass


# Edit this to change the default opening tabs
global DEFAULTSEQUENCE, DEFAULTNOOFPHASE, DEFAULTTAB

DEFAULTSEQUENCE = [['Heating   ',1,0,80,0,0,100,2,2,5,1,1],
					['Maintain T',3,2.5,80,35,2,0,1,1,1,1,1]]

DEFAULTNOOFPHASE = 2

DEFAULTTAB = ['Default Message',1,0,80,0,0,100,2,2,5,1,1]

class locker:
	# This class is used for signalling between functions that they can work/ need to stop
	# I should've put (NanoUI)self.modeNow here but hey this is implemented later
	can_Measure = False
	can_Process = False

	is_moving_phase = False
	is_moving_phase_when = 0
	new_phase = False
	target_phase = 0

	is_Emergency = False
	is_exiting = False

	# Threading conditions, as a way to control whether threads open or close
	# cMeasure = threading.Condition()	#Used when you want several running UI, so they do work alternately

def afterTimeout():
	# print to stderr, unbuffered in Python 2.
	print('{0} took too long'.format(fn_name), file=sys.stderr)
	sys.stderr.flush() # Python 3 stderr is likely buffered.
	thread.interrupt_main() # raises KeyboardInterrupt
	
# Timeout decorator
def exit_after(s):
	'''
	use as decorator to exit process if 
	function takes longer than s seconds
	'''
	def outer(fn):
		def inner(*args, **kwargs):
			timer = threading.Timer(s, afterTimeout, args=[fn.__name__])
			timer.start()
			try:
				result = fn(*args, **kwargs)
			finally:
				timer.cancel()
			return result
		return inner
	return outer

class NanoUI(QtWidgets.QMainWindow):
	threads = []
	modeNow = 'Inactive'

	buttonArray = []
	settingsArray = []
	labelsArray = []

	seq = []

	def __init__(self):

		QtWidgets.QMainWindow.__init__(self)
		# absdir = path.dirname(path.abspath(__file__))
		# uic.loadUi(absdir+'\\nanoUI.ui',self)
		uic.loadUi('nanoUI.ui',self)
		self.begin()
		self.mainMenuInit()
		self.buttonsInit()
		self.tabsInit()
		self.threadsInit()
		self.graphInit()
		#self.logInit()

		self.endInit()
		self.show()

	def begin(self):
		self.start_time = time.time()
	#DataLog
		self.log = dataLogClass(self.graph_widget)
	#Monitor
		self.monitor = monitorClass(self.log,self.displayMessage)
	#Process
		self.process = processMemory(self.log,self.displayMessage,self.monitor)
	#Description
		self.modeNow = 'Inactive'
		self.displayMessage('====================================')
		self.displayMessage('      Welcome.')
		self.displayMessage('      Program Version: testUI2.py, 2018-7-16 connected')
		self.displayMessage('       - Process Ready')
		self.displayMessage('       - Resizing issue not solved')
		self.displayMessage('       - Use testUI.py to test loading UI')
		self.displayMessage('       - Use testUI3.py to test loading Process and Monitor')
		self.displayMessage('      Please Use buttons on the \'Quick Controls\'')
		self.displayMessage('====================================')
		self.shownow()
		self.displayMessage('Loading Default Sequence...')



	def mainMenuInit(self):
		self.actionNew.triggered.connect(self.fileNew)
		self.actionNew.setStatusTip('Create New Blank Sequence')
		self.actionOpen.triggered.connect(self.fileOpen)
		self.actionOpen.setStatusTip('Open Log and Graph')
		self.actionSave.triggered.connect(self.fileSave)
		self.actionSave.setStatusTip('Save current Log and Graph')
		self.actionExit_2.triggered.connect(self.fileExit)
		self.actionExit_2.setStatusTip('Stop All and Quit')
		self.actionAdjust_Run_Settings.triggered.connect(self.adjustSettings)
		self.actionAdjust_Run_Settings.setStatusTip('Change Sequence')
		self.actionAdjust_Record_Settings.triggered.connect(self.adjustRecord)
		self.actionAdjust_Record_Settings.setStatusTip('Change what shows in log')
		self.actionSave_Template_Sequence.triggered.connect(self.adjustSaveSettings)
		self.actionSave_Template_Sequence.setStatusTip('Save Sequence')
		self.actionBegin_Run_2.triggered.connect(self.runBegin)
		self.actionBegin_Run_2.setStatusTip('Start Process')
		self.actionStop_2.triggered.connect(self.runSTOP)
		self.actionStop_2.setStatusTip('STOP ALL IMMEDIATELY')

	def buttonsInit(self):
		self.push_adjust.clicked.connect(self.adjustSettings)
		self.push_adjust.setStatusTip('Change Sequence')
		self.push_adjust.setEnabled(True)
		self.push_run.clicked.connect(self.runBegin)
		self.push_run.setStatusTip('Start Process')
		self.push_run.setEnabled(True)
		self.push_changeP.clicked.connect(self.runChangeP)
		self.push_changeP.setStatusTip('At current Phase, override Pressure setting')
		self.push_changeP.setEnabled(False)
		self.push_changeT.clicked.connect(self.runChangeT)
		self.push_changeT.setStatusTip('At current Phase, override Temperature setting')
		self.push_changeT.setEnabled(False)
		self.push_next.clicked.connect(self.runNext)
		self.push_next.setStatusTip('Next Phase')
		self.push_next.setEnabled(False)
		self.push_goto.clicked.connect(self.runGoto)
		self.push_goto.setStatusTip('Select and Move to Phase')
		self.push_goto.setEnabled(False)
		self.push_prev.clicked.connect(self.runPrev)
		self.push_prev.setStatusTip('Previous Phase')
		self.push_prev.setEnabled(False)
		self.push_stop.clicked.connect(self.runSTOP)
		self.push_stop.setStatusTip('STOP ALL IMMEDIATELY')
		self.push_stop.setEnabled(False)

	def tabsInit(self):
	#Initialize non tab settings
		self.number_of_phase = DEFAULTNOOFPHASE
		self.line_phase.setText(self.modeNow)
		self.label_runtime.setText('00:00')
		self.checkBox_detailed.setChecked(True)
		self.checkBox_detailed.setEnabled(True)
		self.checkBox_detailed.stateChanged.connect(self.showDetails)
	#Create Sequence Data Array
		#seq refers to entirety of sequence files, in otder
		self.seq = DEFAULTSEQUENCE
		self.buttonArray = []
		self.settingsArray = []
		self.labelsArray = []
	#Create Tabs from scratch
		currentTab = 0
		while (currentTab < self.number_of_phase):
			self.functNewSequence(currentTab,*self.seq[currentTab])
			currentTab = currentTab + 1
	#Disable/Enable Buttons and Settings
		for row in range(len(self.buttonArray)):
			for col in range(len(self.buttonArray[row])):
				self.buttonArray[row][col].setEnabled(False)
			for col in range(len(self.settingsArray[row])):
				self.settingsArray[row][col].setEnabled(False)

	def threadsInit(self):
		#Create a global set of locks
		self.locks = locker()

		# Build the threads, this lets multiple programs run concurrently
		a = threading.Thread(target = self.monitorCheck)
		self.threads.append(a)
		a.start()

		b = threading.Thread(target = self.updateGraph)
		self.threads.append(b)
		b.start()

	def graphInit(self):
	#Graph
		self.log.createGraphs()

	def logInit(self):
		self.checkBox_log1.setChecked(True)
		self.checkBox_log2.setChecked(False)
		self.checkBox_log3.setChecked(False)

	def endInit(self):
		self.displayMessage('Now on standby')

	# EXIT, and File Saving functions
	# ==========================================================

	# NOT DONE
	def fileNew(self):
		asknew = self.generateMessageBox('New File','Your current progress will be removed upon creating new file. Confirm?')
		if asknew == QMessageBox.Ok:
			#add warning message as files will be unsaved
			#Then Reset memory, create from template
			print('FileNew')
		else:
			return

	def fileOpen(self):
		#add warning message as files will be unsaved
		#then find a way to look up directory for data file
		openname, _ = QFileDialog.getOpenFileName(self,"Open File")
		if openname:
			assert(self.log.loadData(openname))
		self.shownow()
		self.displayMessage("Loaded from file {}".format(savename))

	def fileSave(self):
		savename = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
		if savename:
			assert(self.log.saveData(savename))
		self.shownow()
		self.displayMessage("File saved as {}".format(savename))

	def fileExit(self):
		self.close()
		

	# Sequence and Log Adjust functions
	# ==========================================================

	# NOT DONE. Adjust differently for Heating Profile
	def showDetails(self):
		#Function of pressing "Show/Hide Details of Sequence"
		if self.checkBox_detailed.isChecked() == False:
			for tab in range(self.number_of_phase):
				for i in range(6,10):
					self.labelsArray[tab][i].setHidden(True)
				for i in range(9,17):
					self.settingsArray[tab][i].setHidden(True)
				endcon = self.seq[tab][1]
				if endcon != 3:
					self.labelsArray[tab][2].setHidden(True)
					self.settingsArray[tab][2].setHidden(True)
					self.settingsArray[tab][3].setHidden(True)
				else:
					pass
				heat_profile = self.seq[tab][5]
				if (heat_profile == 0) or (heat_profile == 2):
					pass
				else:
					self.labelsArray[tab][6].setHidden(True)
					self.settingsArray[tab][9].setHidden(True)
					self.settingsArray[tab][10].setHidden(True)
				# PID
				if (heat_profile == 1):
					pass
				else:
					self.labelsArray[tab][7].setHidden(True)
					self.labelsArray[tab][8].setHidden(True)
					self.labelsArray[tab][9].setHidden(True)
					self.settingsArray[tab][11].setHidden(True)
					self.settingsArray[tab][12].setHidden(True)
					self.settingsArray[tab][13].setHidden(True)
					self.settingsArray[tab][14].setHidden(True)
					self.settingsArray[tab][15].setHidden(True)
					self.settingsArray[tab][16].setHidden(True)
		elif self.checkBox_detailed.isChecked() == True:
			for tab in range(self.number_of_phase):
				for i in range(6,10):
					self.labelsArray[tab][i].setHidden(False)
				for i in range(9,17):
					self.settingsArray[tab][i].setHidden(False)
				endcon = self.seq[tab][1]
				if endcon != 3:
					pass
				else:
					self.labelsArray[tab][2].setHidden(False)
					self.settingsArray[tab][2].setHidden(False)
					self.settingsArray[tab][3].setHidden(False)
				heat_profile = self.settingsArray[tab][8]
				if (heat_profile == 0) or (heat_profile == 2):
					self.labelsArray[tab][6].setHidden(False)
					self.settingsArray[tab][9].setHidden(False)
					self.settingsArray[tab][10].setHidden(False)
				else:
					pass
				# PID
				if (heat_profile == 1):
					self.labelsArray[tab][7].setHidden(False)
					self.labelsArray[tab][8].setHidden(False)
					self.labelsArray[tab][9].setHidden(False)
					self.settingsArray[tab][11].setHidden(False)
					self.settingsArray[tab][12].setHidden(False)
					self.settingsArray[tab][13].setHidden(False)
					self.settingsArray[tab][14].setHidden(False)
					self.settingsArray[tab][15].setHidden(False)
					self.settingsArray[tab][16].setHidden(False)
				else:
					pass
		else:
			raise #Error

	def adjustSettings(self):
		if self.modeNow == 'Edit':
			self.modeNow = 'Inactive'
			self.displayMessage("")
			self.displayMessage("Sequence Changed into:")
			for row in range(self.number_of_phase):
				self.displayMessage(str(row+1) + ":  " + "".join(str(self.seq[row])))

			self.displayMessage('Now on standby')
			self.displayMessage('==')
			self.line_phase.setText(self.modeNow)
			self.push_adjust.setText('Adjust Sequence')
			self.push_run.setEnabled(True)
			for row in range(len(self.buttonArray)):
				for col in range(len(self.buttonArray[row])):
					self.buttonArray[row][col].setEnabled(False)
				for col in range(len(self.settingsArray[row])):
					self.settingsArray[row][col].setEnabled(False)

		elif self.modeNow == 'Inactive':
			self.modeNow = 'Edit'
			self.displayMessage('==')
			self.shownow()
			self.displayMessage('Entering Editing Mode')
			self.line_phase.setText(self.modeNow)
			self.label_runtime.setText('--:--')
			self.push_adjust.setText('Lock Sequence')
			self.push_run.setEnabled(False)
			for row in range(len(self.buttonArray)):
				for col in range(len(self.buttonArray[row])):
					self.buttonArray[row][col].setEnabled(True)
				for col in range(len(self.settingsArray[row])):
					self.settingsArray[row][col].setEnabled(True)
		elif self.modeNow == 'Run':
			return #Error
		else:
			return #Error

	def adjustRecord(self):
		self.displayMessage('adjustRecord')

	def adjustSaveSettings(self):
		self.displayMessage('adjustSaveSettings')

	def functNewSequence(self, number_of_phas,sdesc,sendc,stime,stemp,spres,sheat
						,shout,skp,ski,skd,svacu,scool):	#shout is s-Heat-out
	#Create Buttons placed in layout2
		buttons_text = ['Delete Phase','Insert New Phase','Move Phase']
		buttons_name = ['delete','new','move']
		layout2 = QHBoxLayout()
		smallbuttonArray = []
		for countz,tex,nam in zip(range(3),buttons_text,buttons_name):
			layoutbutton = QPushButton(tex)
			strung = ['push_',nam,'_',str(number_of_phas)]
			layoutbutton.setObjectName("".join(strung))
			layoutbutton.setStatusTip(layoutbutton.objectName())
			layout2.addWidget(layoutbutton)
			smallbuttonArray.append(layoutbutton)
		self.buttonArray.append(smallbuttonArray)
		for col in range(len(self.buttonArray[number_of_phas])):
			self.buttonArray[number_of_phas][col].clicked.connect(self.templambda1(number_of_phas,col))
	#Create labels placed in column 0 of layout3
		label_name = ['descr', 'endcon', 'time', 'T', 'P', 'heat','heatput','kp',
					'ki','kd','vacuum', 'cool']
		label_text = ['Description','End Condition', ' - Time Waited (mins)',
					'Target Temp (+- 0.1 C)', 'Target Pressure (+- 0.1 bar)',
					'Heating Profile',' - Constant Heat Output (%)',' - Kp',' - Ki',' - Kd',
					'Vacuum', 'Cool Air']
		layout3 = QGridLayout()
		smallLabelArray = []
		for countz,tex,nam in zip(range(12),label_text,label_name):
			layoutlabel = QLabel(tex)
			strung = ['label_',nam,'_',str(number_of_phas)]
			layoutlabel.setObjectName("".join(strung))
			layoutlabel.setStatusTip(layoutlabel.objectName())
			layout3.addWidget(layoutlabel,countz,0)
			smallLabelArray.append(layoutlabel)
			if (sendc != 3) and (nam == 'time'):
					layoutlabel.setHidden(True)
		self.labelsArray.append(smallLabelArray)
	#Create widgets placed in column 1 of layout3
		smallwidgetArray = []
		for countz,tex,nam in zip(range(12),label_text,label_name):
			#Creating objects and connections
			if countz == 0:
				layoutWidg = QTextEdit(sdesc)
				layoutWidg.textChanged.connect(self.templambda2(number_of_phas,0))
			elif countz == 1:
				layoutWidg = QComboBox()
				layoutWidg.addItem('Click Next')
				layoutWidg.addItem('Reach Temperature')
				layoutWidg.addItem('Reach Pressure')
				layoutWidg.addItem('Wait Timer')
				layoutWidg.addItem('= Immediately Skip =')
				layoutWidg.setCurrentIndex(sendc)
				layoutWidg.currentIndexChanged.connect(self.templambda2(number_of_phas,1))
			elif countz == 2:
				layoutWidg = QLabel(str(stime))
				layoutWidg2 = QPushButton('Set Time')
				layoutWidg2.clicked.connect(self.templambda2(number_of_phas,3))
				if sendc != 3:
					layoutWidg.setHidden(True)
					layoutWidg2.setHidden(True)
			elif countz == 3:
				layoutWidg = QLabel(str(stemp))
				layoutWidg2 = QPushButton('Set Temperature')
				layoutWidg2.clicked.connect(self.templambda2(number_of_phas,5))
			elif countz == 4:
				layoutWidg = QLabel(str(spres))
				layoutWidg2 = QPushButton('Set Pressure')
				layoutWidg2.clicked.connect(self.templambda2(number_of_phas,7))
			elif countz == 5:
				layoutWidg = QComboBox()
				layoutWidg.addItem('Rapid')
				layoutWidg.addItem('PID Controlled')
				layoutWidg.addItem('Off')
				layoutWidg.addItem('PWM (0-100)')
				layoutWidg.addItem('Custom')
				layoutWidg.setCurrentIndex(sheat)
				layoutWidg.currentIndexChanged.connect(self.templambda2(number_of_phas,8))
			elif countz == 6:
				layoutWidg = QLabel(str(shout))
				layoutWidg2 = QPushButton('Set Output')
				layoutWidg2.clicked.connect(self.templambda2(number_of_phas,10))
			elif countz == 7:
				layoutWidg = QLabel(str(skp))
				layoutWidg2 = QPushButton('Set Kp')
				layoutWidg2.clicked.connect(self.templambda2(number_of_phas,12))
			elif countz == 8:
				layoutWidg = QLabel(str(ski))
				layoutWidg2 = QPushButton('Set Ki')
				layoutWidg2.clicked.connect(self.templambda2(number_of_phas,14))
			elif countz == 9:
				layoutWidg = QLabel(str(skd))
				layoutWidg2 = QPushButton('Set Kd')
				layoutWidg2.clicked.connect(self.templambda2(number_of_phas,16))
			elif countz == 10:
				layoutWidg = QComboBox()
				layoutWidg.addItem('Yes')
				layoutWidg.addItem('No')
				layoutWidg.setCurrentIndex(svacu)
				layoutWidg.currentIndexChanged.connect(self.templambda2(number_of_phas,17))
			elif countz == 11:
				layoutWidg = QComboBox()
				layoutWidg.addItem('Yes')
				layoutWidg.addItem('No')
				layoutWidg.setCurrentIndex(scool)
				layoutWidg.currentIndexChanged.connect(self.templambda2(number_of_phas,18))
			else:
				layoutWidg = QTextEdit()

			#Designating object names
			strung = ['settings_',nam,'_',str(number_of_phas)]
			layoutWidg.setObjectName("".join(strung))
			layoutWidg.setStatusTip(layoutWidg.objectName())
			#Boxing objects into layouts
			if countz in range(2,5):
				strung = ['settings_button',nam,'_',str(number_of_phas)]
				layoutWidg2.setObjectName("".join(strung))
				layoutWidg2.setStatusTip(layoutWidg2.objectName())
				layout4 = QHBoxLayout()
				layout4.addWidget(layoutWidg)
				layout4.addWidget(layoutWidg2)
				smallwidgetArray.append(layoutWidg)
				smallwidgetArray.append(layoutWidg2)
				layout3.addLayout(layout4,countz,1)
			elif countz in range(6,10):
				strung = ['settings_button',nam,'_',str(number_of_phas)]
				layoutWidg2.setObjectName("".join(strung))
				layoutWidg2.setStatusTip(layoutWidg2.objectName())
				layout4 = QHBoxLayout()
				layout4.addWidget(layoutWidg)
				layout4.addWidget(layoutWidg2)
				smallwidgetArray.append(layoutWidg)
				smallwidgetArray.append(layoutWidg2)
				layout3.addLayout(layout4,countz,1)
			else:
				layout3.addWidget(layoutWidg,countz,1)
				smallwidgetArray.append(layoutWidg)
		self.settingsArray.append(smallwidgetArray)
	#Bring the layouts together
		layout1 = QVBoxLayout()
		layout1.addSpacing(1)
		layout1.addLayout(layout3)
		layout1.addLayout(layout2)
		box = QWidget()
		box.setLayout(layout1)
		self.phase_tabs.addTab(box,str(number_of_phas+ 1))

	def buttonPressed(self,tab,buttonCode):

		if buttonCode == 0:
			askdel = self.generateMessageBox('Confirmation','Are you sure you want to delete phase?')
			if askdel == QMessageBox.Ok:
				del self.settingsArray[tab]
				del self.labelsArray[tab]
				del self.buttonArray[tab]
				del self.seq[tab]
				self.phase_tabs.removeTab(tab)
				self.number_of_phase = self.number_of_phase - 1
				for currentTab in range(tab,self.number_of_phase):
					self.reindexTab(currentTab)
			elif askdel == QMessageBox.Cancel:
				return
			else:
				return #Error
		elif buttonCode == 1:
			defNewTab = DEFAULTTAB
			self.seq.append(defNewTab)
			self.functNewSequence(self.number_of_phase,*defNewTab)
			self.number_of_phase = self.number_of_phase + 1
		elif buttonCode == 2:
			print('move not yet implemented')
		else:
			self.displayMessage(" ".join((str(tab),str(buttonCode))),'X')
			return #Error

	def reindexTab(self,row):
		# Function to "shift tabs" when a tab at about the center is being deleted
		self.phase_tabs.setTabText(row,str(row+1))
		for col in range(len(self.settingsArray[row])):
			prevName = self.settingsArray[row][col].objectName()
			prevName = "".join([prevName[:-1],str(row)])
			self.settingsArray[row][col].setObjectName(prevName)
			self.settingsArray[row][col].setStatusTip(prevName)
			self.settingsArray[row][col].disconnect()
			if col == 0:
				self.settingsArray[row][col].textChanged.connect(self.templambda2(row,col))
			elif col == 1:
				self.settingsArray[row][col].currentIndexChanged.connect(self.templambda2(row,col))
			elif col == 3:
				self.settingsArray[row][col].clicked.connect(self.templambda2(row,col))
			elif col == 5:
				self.settingsArray[row][col].clicked.connect(self.templambda2(row,col))
			elif col == 7:
				self.settingsArray[row][col].clicked.connect(self.templambda2(row,col))
			elif col == 8:
				self.settingsArray[row][col].currentIndexChanged.connect(self.templambda2(row,col))
			elif col == 10:
				self.settingsArray[row][col].clicked.connect(self.templambda2(row,col))
			elif col == 12:
				self.settingsArray[row][col].clicked.connect(self.templambda2(row,col))
			elif col == 14:
				self.settingsArray[row][col].clicked.connect(self.templambda2(row,col))
			elif col == 16:
				self.settingsArray[row][col].clicked.connect(self.templambda2(row,col))
			elif col == 17:
				self.settingsArray[row][col].currentIndexChanged.connect(self.templambda2(row,col))
			elif col == 18:
				self.settingsArray[row][col].currentIndexChanged.connect(self.templambda2(row,col))
			else:
				return
		for col in range(len(self.buttonArray[row])):
			prevName = self.buttonArray[row][col].objectName()
			prevName = "".join([prevName[:-1],str(row)])
			self.buttonArray[row][col].setObjectName(prevName)
			self.buttonArray[row][col].setStatusTip(prevName)
			self.buttonArray[row][col].disconnect()
			self.buttonArray[row][col].clicked.connect(self.templambda1(row,col))


	def settingsChanged(self,tab,widgCode):
		if widgCode == 0:
			self.seq[tab][0] = self.settingsArray[tab][0].toPlainText()
		elif widgCode == 1:
			self.seq[tab][1] = self.settingsArray[tab][1].currentIndex()
			if self.settingsArray[tab][1].currentIndex() != 3:
				self.labelsArray[tab][2].setHidden(True)
				self.settingsArray[tab][2].setHidden(True)
				self.settingsArray[tab][3].setHidden(True)
			else:
				self.labelsArray[tab][2].setHidden(False)
				self.settingsArray[tab][2].setHidden(False)
				self.settingsArray[tab][3].setHidden(False)
		elif widgCode == 2:
			return
		elif widgCode == 3:
			a = self.generateInputBox("Set Time","Input Time in minutes",2.5,0,30,2)
			if a != None:
				self.settingsArray[tab][2].setText(str(a))
				self.seq[tab][2] = a
		elif widgCode == 4:
			return
		elif widgCode == 5:
			a = self.generateInputBox("Set Temp","Input Temperature (+- 0.1 C)",80,30,170,1)
			if a != None:
				self.settingsArray[tab][4].setText(str(a))
				self.seq[tab][3] = a
		elif widgCode == 6:
			return
		elif widgCode == 7:
			a = self.generateInputBox("Set Pressure","Input Pressure (+- 0.1 bar)",35,0,35,1)
			if a != None:
				self.settingsArray[tab][6].setText(str(a))
				self.seq[tab][4] = a
		elif widgCode == 8:
			# Heating Profile
			b = self.settingsArray[tab][8].currentIndex()
			self.seq[tab][5] = b
			# Rapid, Off or PWM
			if (b == 0) or (b == 2):
				self.labelsArray[tab][6].setHidden(False)
				self.settingsArray[tab][9].setHidden(False)
				self.settingsArray[tab][10].setHidden(False)
			else:
				self.labelsArray[tab][6].setHidden(True)
				self.settingsArray[tab][9].setHidden(True)
				self.settingsArray[tab][10].setHidden(True)
			# PID
			if (b == 1):
				self.labelsArray[tab][7].setHidden(False)
				self.labelsArray[tab][8].setHidden(False)
				self.labelsArray[tab][9].setHidden(False)
				self.settingsArray[tab][11].setHidden(False)
				self.settingsArray[tab][12].setHidden(False)
				self.settingsArray[tab][13].setHidden(False)
				self.settingsArray[tab][14].setHidden(False)
				self.settingsArray[tab][15].setHidden(False)
				self.settingsArray[tab][16].setHidden(False)
			else:
				self.labelsArray[tab][7].setHidden(True)
				self.labelsArray[tab][8].setHidden(True)
				self.labelsArray[tab][9].setHidden(True)
				self.settingsArray[tab][11].setHidden(True)
				self.settingsArray[tab][12].setHidden(True)
				self.settingsArray[tab][13].setHidden(True)
				self.settingsArray[tab][14].setHidden(True)
				self.settingsArray[tab][15].setHidden(True)
				self.settingsArray[tab][16].setHidden(True)
		elif widgCode == 9:
			return
		elif widgCode == 10:
			a = self.generateInputBox("Set Heat Output","Input Heat Output",50,0,100,1)
			if a != None:
				self.settingsArray[tab][9].setText(str(a))
				self.seq[tab][6] = a
		elif widgCode == 11:
			return
		elif widgCode == 12:
			a = self.generateInputBox("Set Kp","Input Kp",2,-1024,1024,1)
			if a != None:
				self.settingsArray[tab][11].setText(str(a))
				self.seq[tab][7] = a
		elif widgCode == 13:
			return
		elif widgCode == 14:
			a = self.generateInputBox("Set Ki","Input Ki",2,-1024,1024,1)
			if a != None:
				self.settingsArray[tab][13].setText(str(a))
				self.seq[tab][8] = a
		elif widgCode == 15:
			return
		elif widgCode == 16:
			a = self.generateInputBox("Set Kd","Input Kd",2,-1024,1024,1)
			if a != None:
				self.settingsArray[tab][15].setText(str(a))
				self.seq[tab][9] = a
		elif widgCode == 17:
			self.seq[tab][10] = self.settingsArray[tab][17].currentIndex()
		elif widgCode == 18:
			self.seq[tab][11] = self.settingsArray[tab][18].currentIndex()
		else:
			return #Error

	# Monitor Functions
	# ==========================================================
	#Called once upon Thread creation. Repeats until lock is deactivated
	def monitorCheck(self):
		self.locks.can_Measure = True
		try:
			while self.locks.can_Measure and (not self.locks.is_Emergency):
				self.monitor.readval()
				self.monit_Tc.setText("{0:.03f}".format(self.monitor.T))
				self.monit_Te.setText("{0:.03f}".format(self.monitor.T2))
				self.monit_P.setText("{0:.01f}".format(self.monitor.P))
				if self.locks.can_Process:
					print(self.process.pwm_center)
					self.monit_powc.setText("{:3d}%".format(self.process.pwm_center))
					self.monit_powe.setText("{:3d}%".format(self.process.pwm_edge))
				else:
					self.monit_powc.setText("-")
					self.monit_powe.setText("-")
				time.sleep(0.1)
		except Exception as err:
			traceback.print_tb(err.__traceback__)	
			# Activate Emergency flag if any error occur
			self.locks.is_Emergency = True
		finally:
			self.locks.can_Measure = False


	#Called once upon Thread creation. Repeats until lock is deactivated
	def updateGraph(self):
		self.locks.can_Measure = True
		try:
			while self.locks.can_Measure and (not self.locks.is_Emergency):
				self.monitor.sendval()
				time.sleep(1)
		except Exception as err:
			traceback.print_tb(err.__traceback__)
			# Activate Emergency flag if any error occur
			self.locks.is_Emergency = True
		finally:
			self.locks.can_Measure = False


	def displayTime(self):
		# Check for time of phase reset
		if self.locks.new_phase:
			self.start_time_of_phase = time.time()

		# Create a counting clock indicating time from start of run
		time_elapsed = round(time.time() - self.start_time_of_run - 0.5)
		timetext = "{:02d}:{:02d}".format(time_elapsed // 60,time_elapsed%60)
		self.label_runtime.setText(timetext)
		self.monit_time.setText(timetext)

		# Create a clock from start of only one phase
		number_phase = round(time.time() - self.start_time_of_phase - 0.5)
		timetext2 = "{:02d}:{:02d}".format(time_elapsed_phase // 60,time_elapsed_phase%60)
		self.monit_timephase.setText(timetext2)



	# Run functions
	# ==========================================================

	def runBegin(self):

		if self.modeNow == 'Edit':
			return #Error

		elif self.modeNow == 'Inactive':
			self.displayMessage('=====')
			self.shownow()
			self.displayMessage('Run Begins')
			self.line_phase.setText(self.modeNow)
			self.label_runtime.setText('--:--')
			self.monit_time.setText('00:00')
			self.monit_timephase.setText('00:00')
			self.push_run.setEnabled(False)
			self.push_adjust.setEnabled(False)
			self.push_prev.setEnabled(True)
			self.push_goto.setEnabled(True)
			self.push_next.setEnabled(True)
			self.push_stop.setEnabled(True)
			self.push_changeT.setEnabled(True)
			self.push_changeP.setEnabled(True)
			self.phase_tabs.setCurrentIndex(0)

		# =====================================
		# THIS IS WHERE THE PROGRAM RUNS
		# Everytime phase changes, (due to job finish, or runPrev or runNext or runSTOP)
		# 	ALWAYS INVOKE runPhaseInterrupt first
		# runOnce is used conversely to begin run cycles
		# =====================================
			try:
				self.currentPhase = 0
				self.process.setup()
				self.process.loadData(self.seq[self.currentPhase])

				self.locks.new_phase = False
				self.start_time_of_run = time.time()
				self.start_time_of_phase = 0
				
				a = threading.Thread(target = self.runThread)
				self.threads.append(a)
				a.start()

				self.modeNow = 'Run'

			except Exception as arr:
				traceback.print_tb(err.__traceback__)

		elif self.modeNow == 'Run':
			return #Error
		else:
			raise #Error		

	def runThread(self):
		self.locks.can_Process = True
		try:
			while self.locks.can_Process and (not self.locks.is_Emergency):
				self.displayTime()
				self.runCheck()
				if self.locks.new_phase:
					self.runPhaseInterrupt()
				else:
					self.runOnce()
		except Exception as err:
			traceback.print_tb(err.__traceback__)
			self.locks.is_Emergency = True
		finally:
			self.can_Process = False
			self.runEnd()

	# This decorator gives a (n) second timer before it will be forcefully stopped
	@exit_after(5)
	def runOnce(self):
		self.process.run()

	@exit_after(5)
	def runPhaseInterrupt(self):
	# Transition to next Phase
		# self.log.updateVerticalLine(self.process.asktime())
		self.locks.new_phase = False
		if self.locks.target_phase in range(self.number_of_phase):
			# Move to a particular phase
			self.displayMessage("Moving to phase {}".format(self.locks.target_phase))
			self.currentPhase = self.locks.target_phase
			self.phase_tabs.setCurrentIndex(self.locks.target_phase)
			self.process.loadData(self.seq[self.currentPhase])
			return
		else:
			# Exit
			self.displayMessage("Exiting run...")
			self.locks.can_Process = False
			return

	def runCheck(self):
		# [!] WARNING spike in T or P can trigger end of phase forcefully
		# [!] Will need some time before being sure that the change in T or P is not transient
		self.checkDelay = 1 	# 1 second worth of re-check
		if self.locks.is_moving_phase:
			if time.time() - self.locker.is_moving_phase_when < self.checkDelay:
				return
			seqcp = self.seq[self.currentPhase]
			if seqcp[1] == 1:
				#Reach T
				if self.monitor.T >= self.seq[self.currentPhase][3]:
					self.locks.new_phase = True
					self.locks.target_phase = self.currentPhase + 1
					self.locks.is_moving_phase = False
					return
			if seqcp[1] == 2:
				#Reach P
				if self.monitor.P >= self.seq[self.currentPhase][4]:
					self.locks.new_phase = True
					self.locks.target_phase = self.currentPhase + 1
					self.locks.is_moving_phase = False
					return
			# Dismiss previous result as a spike
			self.locks.is_moving_phase = False
			self.displayMessage("Change phase ignored due to spike")

		# From seqcp:
		# [1] Endcondition '1'
		#		(0) Click to Proceed/ Will not stop automaticallu
		#		(1) Reach Temp
		#		(2) Reach Pressure
		#		(3) Wait for time to pass
		#		(4) Immediately skip/ Temporarily 'delete' a phase
		#Check if end condition is fulfilled
		seqcp = self.seq[self.currentPhase]
		if seqcp[1] == 1:
			#Reach T
			if self.monitor.T >= seqcp[3]:
				self.locks.is_moving_phase = True
				self.locks.is_moving_phase_when = time.time()
				self.displayMessage("Detected Temperature crossed target {:.2f}".format(seqcp[3]))
				return
		elif seqcp[1] == 2:
			#Reach P
			if self.monitor.P >= seqcp[4]:
				self.locks.is_moving_phase = True
				self.locks.is_moving_phase_when = time.time()
				self.displayMessage("Detected Pressure crossed target {:.2f}".format(seqcp[4]))
				return
		elif seqcp[1] == 3:
			#Check phasetime
			time_elapsed_phase = round(time.time() - self.start_time_of_phase - 0.5)
			if time_elapsed_phase >= self.seq[self.currentPhase][2]:
				self.locks.new_phase = True
				self.locks.target_phase = self.currentPhase + 1
				self.displayMessage("{} seconds has elapsed in phase {}".format(self.seq[self.currentPhase][2],self.currentPhase))
				return
		elif seqcp[1] == 4:
			self.locks.new_phase = True
			self.locks.target_phase = self.currentPhase + 1
			self.displayMessage("Skipping phase {}".format(self.currentPhase))
			return
		else:
			return

	def runEnd(self):
		self.displayMessage('Closing...')
		self.process.close()

		self.modeNow = 'Inactive'
		self.line_phase.setText(self.modeNow)
		self.push_run.setEnabled(True)
		self.push_adjust.setEnabled(True)
		self.push_prev.setEnabled(False)
		self.push_goto.setEnabled(False)
		self.push_next.setEnabled(False)
		self.push_stop.setEnabled(False)
		self.push_changeT.setEnabled(False)
		self.push_changeP.setEnabled(False)

		self.displayMessage('Run Stopped. Now on Standby')
		self.displayMessage('=====')

		return

	# in-UI Run functions
	# ==========================================================

	def runChangeT(self):
		self.displayMessage('RunChangeT')
		a = self.generateInputBox("Title","Input Pressure in bars",0,0,35,1)
		if a != None:
			self.seq[self.currentPhase][3] = a
			self.settingsArray[self.currentPhase][4].setText(str(a))
			self.locks.target_phase = self.currentPhase
			self.locks.new_phase = True

	def runChangeP(self):
		self.displayMessage('RunChangeP')
		a = self.generateInputBox("Title","Input Pressure in bars",30,0,200,1)
		if a != None:
			self.seq[self.currentPhase][4] = a
			self.settingsArray[self.currentPhase][6].setText(str(a))
			self.locks.target_phase = self.currentPhase
			self.locks.new_phase = True

	def runNext(self):
		thisTab = self.currentPhase
		self.displayMessage("{} {}".format("Requesting Move to Next Phase :",str(thisTab+2)))
		a = self.generateMessageBox("Confirm Next","Continue to Next Phase?")
		if a == QMessageBox.Ok:
			if thisTab == self.currentPhase:
				self.locks.target_phase = self.currentPhase + 1
				self.locks.new_phase = True
			else:
				self.displayMessage("Error. Moving to Next Tab Aborted")

	def runPrev(self):
		thisTab = self.currentPhase
		self.displayMessage("{} {}".format("Requesting Move to Previous Phase :",str(thisTab)))
		a = self.generateMessageBox("Confirm Return","Return to Previous Phase?")
		if a == QMessageBox.Ok:
			if thisTab == self.currentPhase:
				self.locks.target_phase = self.currentPhase - 1
				self.locks.new_phase = True
			else:
				self.displayMessage("Error. Moving to Previous Tab Aborted")

	def runGoto(self):
		thisTab = self.currentPhase
		self.displayMessage("Requesting Goto Phase")
		a = self.generateInputBox("Select Tab","Return to Previous Phase?",thisTab+1,0,self.number_of_phase,0)
		if a != None:
			if a == thisTab+1:
				self.displayMessage("Please enter a different tab")
			elif thisTab == self.currentPhase:
				self.locks.target_phase = a - 1
				self.locks.new_phase = True
			else:
				self.displayMessage("Error. Moving to Tab Aborted")

	def runSTOP(self):
		if self.modeNow == 'Edit':
			return #Error
		elif self.modeNow == 'Inactive':
			return #Error
		elif self.modeNow == 'Run':
			self.shownow()
			self.displayMessage('Signalling End of Run...')
			# Flags an exit, waiting for runThread to stop
			self.locks.can_Process = False
		else:
			return #Error


	# The functions below are for miscellaneous purposes
	# ==========================================================

	def generateMessageBox(self, title = "title", msg = "message"):
		#Function thatt generates a dialog box
		msgBox = QMessageBox()
		msgBox.setIcon(QMessageBox.Information)
		msgBox.setWindowTitle(title)
		msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
		msgBox.setText(msg)
		ret = msgBox.exec_()
		return ret

	def generateInputBox(self, title = "title", msg = "message",defau = 0,minim = 0,maxim = 10,steps = 1):
		#Function thatt generates a dialog box
		i, okPressed = QInputDialog.getDouble(self,title,msg,defau,minim,maxim,steps)
		if okPressed:
			return i

	def displayMessage(self, msg = "An empty message", purpose = 'G'):
		curr_time = time.time() - self.start_time
		#By default/None sent to General. Purpose Flags available are 'G', 'P', 'M', 'X'
		#G = General, P = Process, M = Monitor, X = Error
		if purpose == 'G':
			self.text_log.append(msg)
			print(msg)
		#Sends this to three logs managed by dataLogClass
		self.log.saveMsg(msg,curr_time,purpose)
		QCoreApplication.processEvents()

	def shownow(self):
		return self.displayMessage(time.strftime("Current Time is %Y-%m-%d %H:%M:%S", time.gmtime()))

	def templambda1(self,row,col):
		#Use of lambda to create an instance of function, SO connect can now call functions WITH inputs
		#I think there is a better way to do it with *args or decorator or something, but this works too
		return lambda: self.buttonPressed(row,col)

	def templambda2(self,row,col):
		#Similar to above
		return lambda: self.settingsChanged(row,col)

	# Automatically loaded functions 
	# ==========================================================

	def closeEvent(self, event):
		# Generate 'question' dialog on clicking 'X' button in title bar.
		# Reimplement the closeEvent() event handler to include a 'Question'
		# dialog with options on how to proceed - Save, Close, Cancel buttons

		reply = QMessageBox.question(
			self, "Message",
			"Are you sure you want to quit? Any unsaved work will be lost.",
			QMessageBox.Save | QMessageBox.Close | QMessageBox.Cancel,
			QMessageBox.Save)

		if reply == QMessageBox.Close:
			self.locks.is_exiting = True
			self.locks.is_Emergency = True
			event.accept()
		else:
			event.ignore()

	def keyPressEvent(self, event):
		# Close application from escape key.
		# results in QMessageBox dialog from closeEvent, good but how/why?
		if event.key() == Qt.Key_Escape:
			print('exiting via keyPressEvent')
			self.close()
		

if __name__ == '__main__':

	app = QApplication(sys.argv)
	window = NanoUI()
	sys.exit(app.exec_())
