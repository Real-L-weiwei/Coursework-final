from PyQt5 import uic, QtWidgets,QtGui
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import * 

#Import the ui into the class
class ResultsWindow(QMainWindow,uic.loadUiType("results.ui")[0]):
    def __init__(self,appWindow):
        #Inheritance
        super().__init__()
        #sets up the ui
        self.setupUi(appWindow)
        self.AppWindow = appWindow
