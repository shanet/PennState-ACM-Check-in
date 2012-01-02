#! /usr/bin/python
# Shane Tully
# 09.18.11
# Card swipe check-in system for PSU-ACM

import sys
from PyQt4 import QtGui

from uiUtil import UI
import dbUtil


# Constants
VERSION = 2.0

# Globals
<<<<<<< HEAD
dbHost = "acm.psu.edu"
dbUser = "points"
dbTable = "points"


def connectToDatabase(dbPass=""):
   # If a password was not given, ask for it
   if dbPass == "":
      dbPass = getDbPass()

   sys.stdout.write("Connecting to database...")
   try:
      # Connect to the DB!
      dbConn = MySQLdb.connect(host=dbHost, user=dbUser, passwd=dbPass, db=dbTable)
      print "done."
      return dbConn
   except MySQLdb.Error, e:
      # Offer to re-enter password if bad password error
      if "Access denied" in e.args[1]:
         print "\nError connecting to database. Bad password."
         return connectToDatabase(getDbPass())
      # Other error, print and die
      else:
         print "\nError connecting to database.\n%s\nExiting." % (e.args[1])
         sys.exit(1)


def getDbPass():
   return sanitizeInput(getpass.getpass("Database Password: "))


def invalidInput():
   print "Invalid option. Try again."


def cleanUp():
   print "\nCleaning up..."
   dbConn.close()


def showDatabaseError(error):
   # Print a generic database error
   print "\nWARNING! Database error:\n%s" % (error.args[1])


def sanitizeInput(input):
   # Keep a copy of the possibly mixed-case input
   origInput = input
   input.upper()

   # The reserved words to check for
   # There are many more, of course, but these should thwart the most dangerous attacks
   keywords = ["DELETE", "UPDATE", "DROP", "CREATE", "SELECT", "INSERT", "ALTER"]

   # Check for a match
   for i in keywords:
      if i in input:
         return ""
   
   # If no match, return the original input
   return origInput


def insertCard(dbConn, cardID, initialPoints):
   # Get a cursor to the DB
   cursor = dbConn.cursor()
   
   try:
      # Get the access ID associated with this card ID
      accessID = sanitizeInput(raw_input("Access ID: "))
      
      # Add the new record into the DB
      cursor.execute("INSERT INTO points (cardID, accessID, points) values (\'" + cardID + "\', \'" + accessID + "\', " + initialPoints + ");")

      # Print a confirmation message
      print "\n" + accessID + " added to database"
   except MySQLdb.Error, e:
      showDatabaseError(e)
   finally:
      cursor.close()

=======
textMode = 0
>>>>>>> 6ca7733c6414b114550d45f064eddf6033d032b0


def main(args):
   print "Penn State ACM Check-in System Version" , VERSION,"."

   # TODO: accomodate text only mode
   try:
      if textMode == 0:
         global app
         app = UI(args)
         app.exec_()
      else:
         pass

   # Catch keyboard interuppts so that the db connection may be closed
   # in cleanUp function
   except KeyboardInterrupt:
      pass
   finally:
      pass
      #cleanUp()

   # Exit normally
   sys.exit(0)


if __name__ == '__main__':
   main(sys.argv)
