import sqlite3
import os

#Import the specific sub-libraries from PyQt
from PyQt5 import uic, QtWidgets,QtGui
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import * 

from dictfactory import *

#Import the UI into the class - the file name is "loggedOutMenu.ui"
#The 0th index of the uic.loadUiType function gets you the actual UI.
#QMainWindow generates a main application window (PyQt methods)
class SummaryWindow(QMainWindow,uic.loadUiType("summary.ui")[0]):
    def __init__(self,appWindow):
        #Inheritance
        super().__init__()
        #Sets up the ui
        self.setupUi(appWindow)
        self.AppWindow = appWindow
        print(self.AppWindow.userInfo)
        
        #Get userid if logged in
        if self.AppWindow.userInfo != False:
            self.userid = self.AppWindow.userInfo[0]
        
        #SQL set-up
        self.conn = sqlite3.connect("playerQuestions.db",isolation_level=None)
        self.conn.execute("PRAGMA foreign_keys = 1")
        self.conn.row_factory = dict_factory
        
        #Display the number of questions answered
        self.answeredQs = "Questions attempted: "+str(self.AppWindow.answeredQs)
        self.qs_label.setText(self.answeredQs)
        
        #Display the total number of questions
        self.totalQs = "Total number of questions: " + str(self.AppWindow.qnum)
        self.num_qs_label.setText(self.totalQs)
        
        #Display the total number of correct questions
        self.correctQs = "Total number of correct questions: " + str(self.AppWindow.correctQs)
        self.correct_qs_label.setText(self.correctQs)

        
        #SQL - get data from questions
        c = self.conn.cursor()
        select = 'SELECT word,accuracy,answered FROM userQuestion'
        c.execute(select)
        #Fetches all rows
        self.stats = c.fetchall()
        print(self.stats)
        
        #Finding the average, highest and lowest score from the data
        total = 0
        legitQs = 0
        #min and max variable are defined as [word,accuracy]
        #Unattempted words are denoted as None and so an empty string will be replaced by the first legitimate word
        #Accuracy is in the range of 0<=x<=100, 
        #so any value would be larger than -1 and any value of accuracy would be lower than 101
        maxacc = ["",-1]
        minacc = ["",101]
        #Iterate through the dictionary
        for i in range(len(self.stats)):
            #Only process if the question has been answered
            if self.stats[i].get("answered")=='true':
                legitQs = legitQs + 1
                ##print(stats[i])
                #Get accuracy for a particular question
                acc=self.stats[i].get("accuracy")
                #Add it on to the total
                total = total + acc
                ##print(acc,total)
                
                #Replace if value is greater than current max value
                if acc>maxacc[1]:
                    maxacc = [self.stats[i].get("word"),acc]
                #Replace if value is smaller than current min value
                if acc<minacc[1]:
                    minacc = [self.stats[i].get("word"),acc]
        #Work out the average
        if legitQs == 0:
            av = "N/A"
            minacc = ["","N/A"]
            maxacc = ["","N/A"]
        else:
            av = round(total/legitQs,2)
        print(av)
        print(minacc,maxacc)
        
        #Display all the information to the labels
        self.av = "Average Accuracy: " + str(av) + "%"
        self.av_acc_label.setText(self.av)
        
        self.minacc = "Worst Accuracy & Word: " + str(minacc[0]) + " - " + str(minacc[1]) + "%"
        print(self.minacc)
        self.worst_acc_label.setText(self.minacc)
        
        self.maxacc = "Best Accuracy & Word: " + str(maxacc[0]) + " - " + str(maxacc[1]) + "%"
        self.best_acc_label.setText(self.maxacc)
        
        #Actions after clicking the finish button
        self.finish_but.clicked.connect(self.finish)

            
    def finish(self):
        #Check if a guest is using the program
        if self.AppWindow.userInfo == False:
            #Move audio with high enough accuracy into dataset
            pass
        else:
            #SQL - find date info in database
            #Get today's date
            now = QDate.currentDate().toString(Qt.ISODate)
            #Fetch the dateid storing today's date
            c = self.conn.cursor()
            select = 'SELECT dateid FROM date WHERE date = :d'
            c.execute(select,{'d':now})
            #Fetches one row
            dateInfo = c.fetchone()
            #If today's date doesn't exist in the database, generate the date
            if dateInfo == None:
                insert = 'INSERT INTO date(dateid,date) VALUES(null,:d)'
                c.execute(insert,{'d':now})
                select = 'SELECT dateid FROM date WHERE date = :d'
                c.execute(select,{'d':now})
                #Fetches one row
                dateInfo = c.fetchone()
            self.dateid = dateInfo.get("dateid")
            print(dateInfo,self.dateid)
        
            #Fetch previous result information of the current person today from the database
            select = 'SELECT resultid,attempts FROM result WHERE dateid = :d AND userid = :u'
            c.execute(select,{'d':self.dateid,'u':self.userid})
            #Fetches one row
            resultInfo = c.fetchone()
            
            #If this is the first time the user has used the program today, then generate a new entry of result
            if resultInfo == None:
                insert = 'INSERT INTO result(resultid,dateid,userid,attempts) VALUES(null,:d,:u,0)'
                c.execute(insert,{'d':self.dateid,'u':self.userid})
                #Fetch it again
                select = 'SELECT resultid,attempts FROM result WHERE dateid = :d AND userid = :u'
                c.execute(select,{'d':self.dateid,'u':self.userid})
                #Fetches one row
                resultInfo = c.fetchone()
            
            print(resultInfo)
            
            #'attempts' stores the previous number of attempts, this number should be incremented
            self.attempts = resultInfo.get("attempts") + 1
            
            #Update the new value of attempts
            update = 'UPDATE result SET attempts = :a WHERE dateid = :d AND userid = :u'
            c.execute(update,{'a':self.attempts,'d':self.dateid,'u':self.userid})
            
            #Get all the picture info from the pictures table
            self.picInfo = self.fetchPic()
            #Loop over each possible word
            for i in range (len(self.picInfo)):
                word = self.picInfo[i].get("word")
                wordStats = self.getWordStats(word)
                print(word,wordStats)
                #If the word has appeared, insert all of its stats for the session into the database
                if wordStats[1] != None:
                    insert = 'INSERT INTO wordResult(wordResid,resultid,userid,picture,numAttempt,numTimes,average,best,worst) VALUES(null,:r,:u,:p,:na,:nt,:a,:b,:w)'
                    c.execute(insert,{'r':resultInfo.get("resultid"),'u':self.userid,'p':word,'na':self.attempts,'nt':wordStats[0],'a':wordStats[1],'b':wordStats[2],'w':wordStats[3]})     
                    
        
        #Get all the question numbers where the user has attempted
        c = self.conn.cursor()
        select = 'SELECT questid FROM userQuestion WHERE answered = :a'
        c.execute(select,{'a':"true"})
        #Fetches all rows
        self.deleteFiles = c.fetchall()
        print(self.deleteFiles)
        
        #get current directory
        def_data_dir = os.getcwd()
        
        #Loop through all the attempted questions
        for i in range (len(self.deleteFiles)):
            #Get the current question number
            filename = self.deleteFiles[i].get("questid")
            #Get the directory of the file
            filename1 = def_data_dir + "/" + str(filename) + ".wav"
            #Delete the file
            os.remove(filename1)
            #Delete the trimmed audio file
            filename2 = def_data_dir + "/" + str(filename) + "_trimmed.wav"
            os.remove(filename2)
            
            print(filename1,filename2)
        
        
        self.loadWindow()
        
    def fetchPic(self):
        #SQL to get all pictures from database
        c = self.conn.cursor()
        select = 'SELECT pictureid,word,jpg FROM pictures'
        c.execute(select)
        pictures = c.fetchall()
        print(pictures)
        return pictures    
    
    
    def getWordStats(self,word):
        #Initialising local variables
        counter = 0
        total = 0
        maxacc = -1
        minacc = 101
        #Determining how many time the word appeared
        for i in range(len(self.stats)):
            if self.stats[i].get("word") == word and self.stats[i].get("answered") != "false":
                counter = counter + 1
                #Get accuracy for a particular question
                acc=self.stats[i].get("accuracy")
                #Add it on to the total
                total = total + acc
                #Replace if value is greater than current max value
                if acc>maxacc:
                    maxacc = acc
                #Replace if value is smaller than current min value
                if acc<minacc:
                    minacc = acc
        #Work out the average
        if counter == 0:
            av = None
            minacc = None
            maxacc = None
        else:
            av = round(total/counter,2)
        #Store result as an array to be returned
        res = [counter,av,maxacc,minacc]
        return res
        

    #Direct back to loggedInWindow or loggedOutWindow
    def loadWindow(self):
        #If guest is using it
        if self.AppWindow.userInfo == False:
            self.AppWindow.setupLoggedOutWindow()
        #If a logged in user is using it
        else:
            self.AppWindow.setupLoggedInWindow(self.AppWindow.userInfo)


