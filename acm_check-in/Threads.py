# Shane Tully
# 09.18.11
# Magnetic card check-in application for Penn State ACM

from time import sleep
from PyQt4.Qt import *

from DBUtil import DB
import Constants as c


class LoginThread(QThread):
   def __init__(self, dbHost, dbDatabase, dbTable, dbUser, dbPass):
      super(LoginThread, self).__init__()
      self.dbHost = dbHost
      self.dbDatabase = dbDatabase
      self.dbTable = dbTable
      self.dbUser = dbUser
      self.dbPass = dbPass

   def __del__(self):
      # Stop the thread if it's being deleted, but still running
      self.quit()
   
   def run(self):
      # Init the db object
      db = DB(self.dbHost, self.dbDatabase, self.dbTable, self.dbUser, self.dbPass)

      # Connect to the remote database server
      loginStatus = db.connect()

      self.emit(SIGNAL("postLogin(PyQt_PyObject, PyQt_PyObject)"), loginStatus, db)


class CheckinThread(QThread):
   def __init__(self, db, pointValue):
      super(CheckinThread, self).__init__()

      self.db = db
      self.pointValue = str(pointValue)
      self.cardID = None

   def __del__(self):
      # Stop the thread if it's being deleted, but still running
      self.quit()

   def setCardID(self, cardID):
      self.cardID = cardID
   
   def run(self):
      # Warning: setCardID() must have been called before starting this thread
      checkinResult = self.db.checkin(self.cardID, self.pointValue)
      self.emit(SIGNAL("postCardSwipe(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), 
               checkinResult["checkinStatus"], checkinResult["accessID"], checkinResult["cardID"],
               checkinResult["sqlError"], self.pointValue)


class AddCardThread(QThread):
   def __init__(self, db, cardID, accessID, pointValue):
      super(AddCardThread, self).__init__()

      self.db = db
      self.pointValue = str(pointValue)
      self.cardID = cardID
      self.accessID = accessID

   def __del__(self):
      # Stop the thread if it's being deleted, but still running
      self.quit()
   
   def run(self):
      addCardResult = self.db.addCard(self.cardID, self.accessID, self.pointValue)
      self.emit(SIGNAL("postCardSwipe(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), 
               addCardResult["addCardStatus"], addCardResult["accessID"], addCardResult["cardID"],
               addCardResult["sqlError"], self.pointValue)


class ShowPointsThread(QThread):
   def __init__(self, db, accessID=""):
      super(ShowPointsThread, self).__init__()

      self.db = db
      self.accessID = accessID
   
   def __del__(self):
      # Stop the thread if it's being deleted, but still running
      self.quit()

   def setAccessID(self, accessID):
      self.accessID = accessID
   
   def run(self):
      showPointsResult = self.db.showPoints(self.accessID)
      self.emit(SIGNAL("setPoints(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), 
               showPointsResult["showPointsStatus"], showPointsResult["pointsTuple"], showPointsResult["sqlError"])


class SleepThread(QThread):
   def __init__(self, time):
      super(SleepThread, self).__init__()

      self.time = time

   def __del__(self):
      # Stop the thread if it's being deleted, but still running
      self.quit()

   def setTime(self, time):
      self.time = time

   def getTime(self):
      return self.time

   def run(self):
      sleep(self.time)
      self.emit(SIGNAL("resetCheckinWidget()"))


