import sqlite3

#Import  PyQt modules
from PyQt5 import uic, QtWidgets,QtGui
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import * 

#import dictfactory file for later usage
from dictfactory import *

#Import the ui into the class
class LoginWindow(QMainWindow,uic.loadUiType("login.ui")[0]):
    def __init__(self,appWindow):
        #Inheritance
        super().__init__()
        #sets up the ui
        self.setupUi(appWindow)
        #Setup the appWindow as an instance so data can be passed back and methods in
        #the app class/window can be used
        self.AppWindow = appWindow

        #SQL setup
        #Load the database file with the name "playerQuetions.db"
        #Setting isolation level to None allows for the autocommit mode
        self.conn = sqlite3.connect("playerQuestions.db",isolation_level=None)
        #Enforces and switches on foreign keys
        self.conn.execute("PRAGMA foreign_keys = 1")
        #Set up the dicfactory in the SQL commands
        self.conn.row_factory = dict_factory

        #Runs the checkUser method when the "Confirm Sign Up" button is clicked
        self.login_but.clicked.connect(self.checkLogin)

    def checkLogin(self):
        self.condition = True
        #Removes pre-existing border of the username and password boxes
        self.user_le.setStyleSheet('border : 0px solid white')
        self.pass_le.setStyleSheet('border : 0px solid white')

        #Extracts the content from the username and password line edits
        username = self.user_le.text()
        password = self.pass_le.text()
        ##print(username,password)

        #SQL statement which extracts the row which has the same username as the
        #one inputtedin the username line edit
        c = self.conn.cursor()
        select = 'SELECT userid,username,password FROM users WHERE username = :n'
        c.execute(select,{'n':username})
        #Fetches one row
        userInfo = c.fetchone()
        print(userInfo)
        print(username,password)

        #Check if the line edits are blank
        if username == "" and password == "":
            #Set condition to false so action doesn't proceed
            self.condition = False
            #Launch the popUp box if empty string is detected
            self.launchPopup("Empty string entered for \n username and password")
            #Set up the red border around the line edits
            self.user_le.setStyleSheet('border : 1px solid red')
            self.pass_le.setStyleSheet('border : 1px solid red')
        elif username == "":
            self.condition = False
            self.user_le.setStyleSheet('border : 1px solid red')
            self.launchPopup("Empty string entered for username")
        elif password == "":
            self.condition = False
            self.pass_le.setStyleSheet('border : 1px solid red')
            self.launchPopup("Empty string entered for password")

        #Check if username exists
        if userInfo == None:
            if self.condition == True:
                self.condition = False
                self.user_le.setStyleSheet('border : 1px solid red')
                self.launchPopup("Incorrect username - does not exist \n Re-enter login details or \n sign up for an account")

        #Checking if the entered password for specified username has been found from the database
        if self.condition != False:   

            #If username is found, extract the valid password into a variable
            userCon = userInfo.pop("password")
            #Check if the password entered by the user is valid
            if userCon == password:
   ##             print(self.condition)
                #If valid, launch a popup box and notify the user
                self.launchPopup("You have successfully logged in!")
                self.username = username
                self.userid = userInfo.pop("userid")
                self.userInfo =[self.userid,self.username]
                #Launch the loggedInWindow if login credentials are correct
                ##self.AppWindow.setupLoggedInWindow()
                self.AppWindow.setupLoggedInWindow(self.userInfo)
                ##self.AppWindow.username = self.username
            #If not valid, halt any further procedures
            else:
                self.condition = False
                #Make the borders around the line edits red
                self.pass_le.setStyleSheet('border : 1px solid red')
                #Launch the popup box to inform user
                self.launchPopup("Incorrect password, try again")
            
    #Pass the text in to launch and setup the popup box
    def launchPopup(self,text):
        pop = Popup(text,self)
        pop.show()

#QDialog used as the type of PyQt widget, load the file
class Popup(QDialog,uic.loadUiType("popup.ui")[0]):
    def __init__(self,name,parent):
        #Inheritance
        super().__init__(parent)
        #Set the styling
        self.setStyleSheet('font-size: 20px; font-family: calibri')
        #Set up dimensions for the box
        self.resize(400,100)
        #Replace content in the label with intended content
        self.label = QLabel(name,self)




        
