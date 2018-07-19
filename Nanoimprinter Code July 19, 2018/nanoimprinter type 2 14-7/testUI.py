'''
	This is a trial UI controller to test out loading of UI
	
'''

import os
import sys
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication, Qt

class testUI(QtWidgets.QMainWindow):

	def __init__(self):
		absdir = os.path.dirname(os.path.abspath(__file__))
		QtWidgets.QMainWindow.__init__(self)
		uic.loadUi(absdir+'\\nanoUI.ui',self)
		self.show()

		
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
			event.accept()
		else:
			event.ignore()

	def keyPressEvent(self, event):
		# Close application from escape key.
		# results in QMessageBox dialog from closeEvent, good but how/why?
		
		if event.key() == Qt.Key_Escape:
			self.close()


if __name__ == '__main__':
	
	app = QtWidgets.QApplication(sys.argv)
	window = testUI()
	sys.exit(app.exec_())
