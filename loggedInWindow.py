import sqlite3

from PyQt5 import uic, QtWidgets,QtGui
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import * 

#import dictfactory file for later usage
from dictfactory import *

#Import the ui into the class
class LoggedInWindow(QMainWindow,uic.loadUiType("loggedInMenu.ui")[0]):
    def __init__(self,appWindow):
        #Inheritance
        super().__init__()
        #sets up the ui
        self.setupUi(appWindow)
        self.AppWindow = appWindow
        print(self.AppWindow.userInfo)
        text = "Hello " + str(self.AppWindow.userInfo[1])
        self.user_label.setText(text)

        self.start_but.clicked.connect(self.loadQuestionWindow)
        
        #self.res_but.clicked.connect(self.loadResultsWindow)
        
        #Action for clicking on the logout button
        self.logout_but.clicked.connect(self.logout)
        
        #Action for clicking on the delete account button
        self.del_but.clicked.connect(self.delete)

    def logout(self):
        #Get confirm box, and pass in functionality
        self.launchConfirmBox("Are you sure \n you want to \n logout?","logout")
        
    def delete(self):
        #Get confirm box, and pass in functionality
        self.launchConfirmBox("Are you sure \n you want to \n delete your account?","delete")

    def loadQuestionWindow(self):
        self.AppWindow.setupQuestionWindow(self.AppWindow.userInfo)
        
    def loadResultsWindow(self):
        self.AppWindow.setupResultsWindow(self.AppWindow.userInfo)


    #Pass the text in to launch and setup the popup box
    def launchConfirmBox(self,text,_type):
        box = ConfirmBox(text,_type,self)
        box.show()

#QDialog used as the type of PyQt widget, load the file
class ConfirmBox(QDialog,uic.loadUiType("confirmBox.ui")[0]):
    def __init__(self,text,_type,parent):
        #Inheritance from loggedInWindow
        super().__init__(parent)
        #Set up the loaded UI file
        self.setupUi(self)
        #Create an attribute from the inherited class
        self.parent = parent
        print(parent)
        #Set the text of the confirm box to the passed in text parameter
        self.label.setText(text)

        
        #SQL setup
        #Load the database file with the name "playerQuetions.db"
        #Setting isolation level to None allows for the autocommit mode
        self.conn = sqlite3.connect("playerQuestions.db",isolation_level=None)
        #Enforces and switches on foreign keys
        self.conn.execute("PRAGMA foreign_keys = 1")
        #Set up the dicfactory in the SQL commands
        self.conn.row_factory = dict_factory
        
        #Actions for clicking the ok and cancel button in the confirm box
        self.cancel_but.clicked.connect(self.cancel)       
        if _type == "logout":
            self.ok_but.clicked.connect(self.okLogout)
        else:
            self.ok_but.clicked.connect(self.okDelete)
            
            

    def cancel(self):
        #Hide the confirm box then pass
        self.hide()

    def okLogout(self):
        #Hide the confirm box then navigate to the loggedOutWindow
        self.hide()
        self.parent.AppWindow.setupLoggedOutWindow()
        
    def okDelete(self):
        #Hide the confirm box 
        self.hide()
        #Navigate to logged-out window
        self.parent.AppWindow.setupLoggedOutWindow()
        #Delete relevant row from users table
        c = self.conn.cursor()
        delete = 'DELETE FROM users WHERE username = :n'
        c.execute(delete,{'n':self.parent.AppWindow.userInfo[1]})



