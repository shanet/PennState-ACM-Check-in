# Shane Tully
# 09.18.11
# Magnetic card check-in application for Penn State ACM

from time import sleep
from PySide.QtCore import QThread
from PySide.QtCore import Signal

from DBUtil import DB
import Constants as c


class LoginThread(QThread):
   postLoginSignal = Signal(int, object)

   def __init__(self, dbHost, dbDatabase, dbTable, dbUser, dbPass, postLoginCallback):
      super(LoginThread, self).__init__()
      self.dbHost = dbHost
      self.dbDatabase = dbDatabase
      self.dbTable = dbTable
      self.dbUser = dbUser
      self.dbPass = dbPass

      self.postLoginSignal.connect(postLoginCallback)

   
   def run(self):
      # Init the db object
      db = DB(self.dbHost, self.dbDatabase, self.dbTable, self.dbUser, self.dbPass)

      # Connect to the remote database server
      loginStatus = db.connect()
   
      self.postLoginSignal.emit(loginStatus, db)


class CheckinThread(QThread):
   postCardSwipeSignal = Signal(int, str, str, object, str)

   def __init__(self, db, pointValue, postCardSwipeCallback):
      super(CheckinThread, self).__init__()

      self.db = db
      self.pointValue = str(pointValue)
      self.cardID = None

      self.postCardSwipeSignal.connect(postCardSwipeCallback)


   def setCardID(self, cardID):
      self.cardID = cardID
   
   def run(self):
      # Warning: setCardID() must have been called before starting this thread

      # At least make sure the card ID is of the right length. Not much more validation can be done.
      if len(self.cardID) != 16:
         self.postCardSwipeSignal.emit(c.ERROR_READING_CARD, '', '', object(), self.pointValue)
         return
      
      checkinResult = self.db.checkin(self.cardID, self.pointValue)

      # Don't pass nonetype's through signals expecting an object or seg faults happen
      if checkinResult["sqlError"] is None:
         checkinResult["sqlError"] = object()

      self.postCardSwipeSignal.emit(checkinResult["checkinStatus"], checkinResult["accessID"], checkinResult["cardID"], checkinResult["sqlError"], self.pointValue)


class AddCardThread(QThread):
   cardAddedSignal = Signal(int, str, str, object, str)

   def __init__(self, db, cardID, accessID, pointValue, cardAddedCallback):
      super(AddCardThread, self).__init__()

      self.db = db
      self.pointValue = str(pointValue)
      self.cardID = cardID
      self.accessID = accessID

      self.cardAddedSignal.connect(cardAddedCallback)

   
   def run(self):
      addCardResult = self.db.addCard(self.cardID, self.accessID, self.pointValue)

      # Don't send nonetype's through signals
      if addCardResult['sqlError'] is None:
         addCardResult['sqlError'] = object()

      self.cardAddedSignal.emit(addCardResult["addCardStatus"], addCardResult["accessID"], addCardResult["cardID"], addCardResult["sqlError"], self.pointValue)


class ShowPointsThread(QThread):
   showPointsSignal = Signal(int, object, object)

   def __init__(self, db, accessID, showPointsCallback):
      super(ShowPointsThread, self).__init__()

      self.db = db
      self.accessID = accessID

      self.showPointsSignal.connect(showPointsCallback)
   

   def setAccessID(self, accessID):
      self.accessID = accessID
   
   def run(self):
      showPointsResult = self.db.showPoints(self.accessID)

      # Don't send nonetype's through a signal or it gets angry and seg faults
      if showPointsResult["sqlError"] is None:
         showPointsResult["sqlError"] = object()
      if showPointsResult["pointsTuple"] is None:
         showPointsResult["pointsTuple"] = object()

      self.showPointsSignal.emit(showPointsResult["showPointsStatus"], showPointsResult["pointsTuple"], showPointsResult["sqlError"])


class SleepThread(QThread):
   wakeupSignal = Signal()

   def __init__(self, time, wakeupCallback):
      super(SleepThread, self).__init__()

      self.time = time
      self.wakeupSignal.connect(wakeupCallback)


   def setTime(self, time):
      self.time = time

   def getTime(self):
      return self.time

   def run(self):
      sleep(self.time)
      self.wakeupSignal.emit()
