#Importing the PyQt library
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

#Importing the classes from their individual python files
from questionWindow import QuestionWindow
from loggedOutWindow import LoggedOutWindow
from loggedInWindow import LoggedInWindow
from loginWindow import LoginWindow
from signUpWindow import SignUpWindow
from summaryWindow import SummaryWindow
from resultsWindow import ResultsWindow

#PyQt syntax - pass in QMainWindow as parameter for class
class App(QMainWindow):
    def __init__(self):
        #Inheritance
        super().__init__()
        #Displays loggedOutWindow initially
        self.setupLoggedOutWindow()
        self.show()
    
    def setupQuestionWindow(self,userInfo):
        self.userInfo = userInfo
        #Making it an attribute of the class
        self.QuestionWindow = QuestionWindow(self)
        #Open questionWindow when a specified button is clicked
        self.addNavigationClickHandlers(self.QuestionWindow,"QuestionWindow")

    def setupLoggedOutWindow(self):
        self.LoggedOutWindow = LoggedOutWindow(self)
        self.addNavigationClickHandlers(self.LoggedOutWindow,"LoggedOutWindow")
        
    def setupLoggedInWindow(self,userInfo):
        self.userInfo = userInfo
        self.LoggedInWindow = LoggedInWindow(self)
        self.addNavigationClickHandlers(self.LoggedInWindow,"LoggedInWindow")
        
    def setupLoginWindow(self):
        self.LoginWindow = LoginWindow(self)
        self.addNavigationClickHandlers(self.LoginWindow,"LoginWindow")

    def setupSignUpWindow(self):
        self.SignUpWindow = SignUpWindow(self)
        self.addNavigationClickHandlers(self.SignUpWindow,"SignUpWindow")

    def setupSummaryWindow(self,userInfo,answeredQs,qnum,correctQs):
        self.userInfo = userInfo
        self.answeredQs = answeredQs
        self.qnum = qnum
        self.correctQs = correctQs
        self.SummaryWindow = SummaryWindow(self)
        self.addNavigationClickHandlers(self.SummaryWindow,"SummaryWindow")
        
    def setupResultsWindow(self,userInfo):
        self.userInfo = userInfo
        self.ResultsWindow = ResultsWindow(self)
        self.addNavigationClickHandlers(self.ResultsWindow,"ResultsWindow")

    def addNavigationClickHandlers(self,window,windowName):
#         if windowName == "LoggedOutWindow" or windowName == "LoggedInWindow":
#         #When start_but is clicked, setupQuestionWindow method is run and opens the window
#             window.start_but.clicked.connect(self.setupQuestionWindow)
        if windowName == "SignUpWindow" or windowName == "LoginWindow":
            window.menu_but.clicked.connect(self.setupLoggedOutWindow)
        if windowName == "LoggedOutWindow":
            window.toLogin_but.clicked.connect(self.setupLoginWindow)
            window.toSignUp_but.clicked.connect(self.setupSignUpWindow)
            window.start_but.clicked.connect(self.setupQuestionWindow)
        if windowName == "LoginWindow":
            #window.login_but.clicked.connect(self.setupLoggedInWindow)
            window.toSignUp2_but.clicked.connect(self.setupSignUpWindow)
        if windowName == "SignUpWindow":
            window.toLogin2_but.clicked.connect(self.setupLoginWindow)


