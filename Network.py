import sys
from PyQt4.Qt import *

from dbUtil import DbUtil

import constants as c


class LoginThread(QThread):
   def __init__(self, dbHost, dbTable, dbUser, dbPass):
      super(LoginThread, self).__init__()
      self.dbHost = dbHost
      self.dbTable = dbTable
      self.dbUser = dbUser
      self.dbPass = dbPass

   
   def run(self):
      db = DbUtil(self.dbHost, self.dbTable, self.dbUser, self.dbPass)

      loginStatus = db.connect()
      #loginStatus = c.SUCCESS

      self.emit(SIGNAL("postLogin(PyQt_PyObject, PyQt_PyObject)"), loginStatus, db)


class CheckinThread(QThread):
   def __init__(self, db, pointValue):
      super(CheckinThread, self).__init__()

      self.db = db
      self.pointValue = str(pointValue)
      self.cardID = None

   def setCardID(self, cardID):
      self.cardID = cardID
   
   def run(self):
      print self.cardID
      # Warning: setCardID() must have been called before starting this thread
      checkinStatus = self.db.checkin(self.cardID, self.pointValue)
      self.emit(SIGNAL("postCardSwipe(PyQt_PyObject, PyQt_PyObject)"), checkinStatus, self.pointValue)


