#! /usr/bin/python
# Shane Tully
# 09.18.11
# Card swipe check-in system for PSU-ACM

import os
import re
import sys
import getpass
from datetime import datetime

# The MySQLdb module must be available
try:
   import MySQLdb
except ImportError:
   print "This script requires the MySQLdb module to be installed. Exiting."
   sys.exit(1)   

# Constants
DEFAULT_POINT_VALUE = 50

# Globals
dbHost = "psu-acm.org"
dbUser = "psuacmor_points"
dbTable = "psuacmor_points"


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


def getCardSwipe():
   # Compile the regex for pulling the card ID from all the data on a card
   regex = re.compile(";(.+)=")
   
   while 1:
      # Read the card data as a password so it doesn't show on the screen
      cardData = sanitizeInput(getpass.getpass("\nWaiting for card swipe..."))
      try:
         # Return the card ID
        return regex.search(cardData).group(1)
      except AttributeError:
         # If exit or back, just return to go back
         if "exit" in cardData or "back" in cardData:
            return "exit"
         # Else, a match wasn't found which probably means there was
         # and error reading the card or the card isn't a PSU ID card
         # but assume the former
         else:
            print "Error reading card. Swipe card again."
   return ""


def checkIn(dbConn, pointValue):
   if pointValue.lower() == "back":
      return

   # Get a cursor to the DB
   cursor = dbConn.cursor()

   while 1:
      try:
         # Get the card ID from the card 
         cardID = getCardSwipe()
         if cardID == "exit":
            return
         
         # Get the last check-in time
         cursor.execute("SELECT last_checkin FROM points WHERE cardID=\'" + cardID + "\';")

         # Ensure that the card is in the database
         if cursor.rowcount == 0:
            # Offer to add it
            addCard = raw_input("\nError: Card not in database. Add it? (y,n) ")
            if addCard.lower() == "y":
               insertCard(dbConn, cardID, pointValue)
            continue
         else:
            result = cursor.fetchone()

         # Verify the check-in times
         curDate = datetime.now()
         lastCheckin = result[0];

         # The last_checkin column was added after the DB was populated meaning it could be a NoneType
         # Only check the dates if this is not the case
         if lastCheckin and datetime.date(curDate) == datetime.date(lastCheckin):
            # The DB server is on mountain time. Adjust the local time (eastern),to mountain
            if datetime.time(curDate).hour == 1 or datetime.time(curDate).hour == 0:
               tmzAdjust = 22
            else:
               tmzAdjust = -2
            
            # Check that the current system time is at least one hour greater than the last check-in time
            if (datetime.time(curDate).hour+tmzAdjust == datetime.time(lastCheckin).hour or
                (datetime.time(curDate).hour+tmzAdjust == datetime.time(lastCheckin).hour+1 and
                 datetime.time(curDate).minute < datetime.time(lastCheckin).minute)):
               print "You can only check in once per hour."
               continue
            # If the current system time is before the check-in time, do not allow check-in
            elif datetime.time(curDate).hour+tmzAdjust < datetime.time(lastCheckin).hour:
               print "Last checkin time was in the future. Not allowing check-in. Check your system time."
               continue
         # If the current system date is before the check-in date, do not allow check-in
         elif lastCheckin and datetime.date(curDate) < datetime.date(lastCheckin):
            print "Last checkin time was in the future. Not allowing check-in. Check your system time."
            continue
         
         # Update the database with the new points         
         cursor.execute("UPDATE points SET points=points+" + pointValue + " WHERE cardID=\'" + cardID + "\';")
         # Grab the access ID that just checked-in to print confirmation
         cursor.execute("SELECT accessID FROM points WHERE cardID=\'" + cardID + "\';")

         result = cursor.fetchone()
         print result[0] + " +" + pointValue + " points"
      except MySQLdb.Error, e:
         showDatabaseError(e)
   
   cursor.close()


def showPoints(dbConn, accessID=""):
   if accessID.lower() == "back":
      return

   # Get a cursor to the DB
   cursor = dbConn.cursor()

   try:
      # Either get all access ID's and points from DB or just one access ID
      if accessID.lower() == "all":
         cursor.execute("SELECT accessID, points FROM points ORDER BY points DESC;")
      else:
         cursor.execute("SELECT points FROM points WHERE accessID=\'" + accessID + "\';")
      
      # Show error if not results (access ID is not in database)
      if cursor.rowcount == 0:
         print "\nQuery returned no results."
      else:
         result = cursor.fetchall()

         # If showing all users, display a pretty table
         if accessID.lower() == "all":
            print "\n+--------------------+\n| Access ID | Points |\n+--------------------+"
            for i in range(cursor.rowcount):
               print "|%10s | %6s |" % (result[i][0], result[i][1])
            print "+--------------------+"
         # Show a single user's points
         else:
            print "\n" + accessID + " has " + str(result[0][0]) + " points"
   except MySQLdb.Error, e:
         showDatabaseError(e)
   finally:
      cursor.close()


def addCard(dbConn, continuous):
   if continuous.lower() == "back":
      return

   while 1:
      # Get the card ID
      cardID = getCardSwipe()
      if cardID == "exit":
         return
      
      # Add the new card
      insertCard(dbConn, cardID,str(DEFAULT_POINT_VALUE))
      
      # If not adding multiple cards, end loop
      if continuous.lower() == "n":
         break




# Main

os.system("clear")
print "PSU-ACM Check-in System Version 1.5"

# Connect to the database
dbConn = connectToDatabase(getDbPass())

print "\nType \"back\" at any time to go up a menu level."

try:
   while 1:
      # Display main menu
      print "\n\t1.) Check-in\t\t2.) Show Points\n\t3.) Add New Card\t4.) Exit"
      try:
         option = raw_input("\n>> ")

         if option == "1":
            # Get and validate the point value for this check-in
            # Limited to 500 points to prevent bad typos
            while 1:
               pointValue = sanitizeInput(raw_input("\nPoint Value (" + str(DEFAULT_POINT_VALUE) + "): "))
               
               # Validate point input
               if pointValue == "":
                  pointValue = str(DEFAULT_POINT_VALUE)
                  break
               elif (pointValue.isdigit() and int(pointValue) <= 500) or pointValue == "back":
                  break
               else:
                  print "Invalid input. Try again."
            checkIn(dbConn, pointValue)

         elif option == "2":
            showPoints(dbConn, sanitizeInput(raw_input("\nAccess ID (\"all\" for all): ")))
         elif option == "3":
            addCard(dbConn, sanitizeInput(raw_input("\nAdd multiple cards? (y,n) ")))
         elif option == "4" or option == "back" or option == "exit":
            break
         else:
            invalidInput()

      except ValueError:
         invalidInput()

# Catch keyboard interuppts so that the db connection may be close
# in cleanUp function
except KeyboardInterrupt:
   pass
finally:
   cleanUp()

# Exit normally
sys.exit(0)
