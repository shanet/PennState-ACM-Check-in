# Shane Tully
# 09.18.11
# Magnetic card check-in application for Penn State ACM

import sys
import re
import getpass

from DBUtil import DB
import SharedUtils
import Constants as c

class TextUI:
   def __init__(self):
      self.db = None


   def start(self):
      # Compile the regex for pulling the card ID from all the data on a card
      # Do this here so it isn't done multiple times in the functions below
      self.regex = re.compile(";(.+)=")

      try:
         while 1:
            # Get DB info
            self.getDbInfo()

            # Create the DB object
            self.db = DB(self.dbHost, c.DEFAULT_DATABASE, self.dbTable, self.dbUser, self.dbPass)

            # Connect to the database
            connectStatus = self.connectToDatabase()

            # If we failed to connect to the database offer to re-enter db info
            if connectStatus != c.SUCCESS:
               reenter = raw_input("Failed to connect to database. Re-enter database info? (Y,n) ")
               if reenter.lower() == "n":
                  print "Bye."
                  sys.exit(0)
            else:
               break

         # Start the main menu loop
         self.displayMenu()

      except KeyboardInterrupt:
         pass
      finally:
         print "Cleaning up and exiting..."
         if self.db is not None:
            self.db.close()


   def displayMenu(self):
      print "\nType \"back\" at any time to go up a menu level."

      while 1:
         # Display main menu
         print "\n\t1.) Check-in\n\t2.) Show Points\n\t3.) Exit"
         try:
            option = raw_input("\n>> ")

            if option == "1":
               self.checkin()
            elif option == "2":
               self.showPoints()
            elif option == "3":
               sys.exit(0)
            elif option == "back" or option == "exit":
               exit = raw_input("Exit? (y,N) ")
               if exit.lower() == "y":
                  sys.exit(0)
            else:
               self.invalidInput()

         except ValueError:
            self.invalidInput()


   def connectToDatabase(self):
      # Use stdout.write to prevent newline
      sys.stdout.write("Connecting to database...")

      # Connect to the DB!
      status = self.db.connect()

      if status == c.SUCCESS:
         print "done."
         return status
      elif status == c.BAD_PASSWD:
         print "\nError connecting to database: Bad username or password."
         return status
      else:
         print "\nUnknown Error connecting to database."
         return c.FAILURE


   def checkin(self):
      # Get and validate the point value for this check-in
      # Limited to 500 points to prevent bad typos
      while 1:
         pointValue = SharedUtils.sanitizeInput(raw_input("\nPoint Value (" + str(c.DEFAULT_POINTS) + "): "))
         
         # Validate point input
         if pointValue == "":
            pointValue = str(c.DEFAULT_POINTS)
            break
         elif (pointValue.isdigit() and int(pointValue) <= 500) or pointValue == "back":
            break
         else:
            print "Invalid input. Try again."

      while 1:
         cardID = self.getCardSwipe()

         # If the user requested to exit the loop, break
         if cardID == c.BACK:
            break
         elif cardID == c.ERROR_READING_CARD:
            print "Error reading card. Swipe card again."
            continue

         # Sanitize cardID
         cardID = SharedUtils.sanitizeInput(cardID)
         # cardID will be empty if it failed sanitization. Skip checkin if that is the case
         if cardID == "":
            continue
         
         # Do the checkin
         checkinResult = self.db.checkin(cardID, pointValue)

         if checkinResult["checkinStatus"] == c.SQL_ERROR:
            self.showDatabaseError(checkinResult["sqlError"])
         elif checkinResult["checkinStatus"] == c.BAD_CHECKIN_TIME:
            print "Error: You may only check-in once per hour."
         elif checkinResult["checkinStatus"] == c.FUTURE_CHECKIN_TIME:
            print "Error: Previous check-in time was in the future. Check your local system time."
         elif checkinResult["checkinStatus"] == c.CARD_NOT_IN_DB:
            # Ask if user wants to add the card
            addCard = raw_input("Error: Card not found in database. Add it now? (Y,n) ")
            
            if addCard == "n":
               continue
            
            # Get the accessID for the new card
            accessID = SharedUtils.sanitizeInput(raw_input("Access ID: "))

            # Add the card
            addCardResult = self.db.addCard(cardID, accessID, pointValue)

            if addCardResult["addCardStatus"] == c.SUCCESS:
               self.showCheckinConfirmation(accessID, pointValue)
            elif addCardResult["addCardStatus"] == c.SQL_ERROR:
               self.showDatabaseError(addCardResult["sqlError"])

         elif checkinResult["checkinStatus"] == c.SUCCESS:
            self.showCheckinConfirmation(checkinResult["accessID"], pointValue)
         else:
            print "Unknown error checking in."


   def showPoints(self):
      accessID = SharedUtils.sanitizeInput(raw_input("\nAccess ID (blank for all): "))
      showPointsResult = self.db.showPoints(accessID)

      if showPointsResult["showPointsStatus"] == c.SQL_ERROR:
         self.showDatabaseError(showPointsResult["sqlError"])
      elif showPointsResult["showPointsStatus"] == c.NO_RESULTS:
         print "\nThere were no results to that query."
      elif showPointsResult["showPointsStatus"] == c.SUCCESS:
         # If showing all users, display a pretty table
         if accessID == "":
            print "\n+--------------------+\n| Access ID | Points |\n+--------------------+"

            for i in range(len(showPointsResult["pointsTuple"])):
               print "|%10s | %6s |" % (showPointsResult["pointsTuple"][i][0], showPointsResult["pointsTuple"][i][1])
            print "+--------------------+"
         
         # Show a single user's points
         else:
            print "\n%s has %s points." % (accessID, str(showPointsResult["pointsTuple"][0][0]))


   def getCardSwipe(self):
      # Read the card data as a password so it doesn't show on the screen
      cardID = SharedUtils.sanitizeInput(getpass.getpass("\nWaiting for card swipe..."))
      try:
         # Return the card ID
        return self.regex.search(cardID).group(1)
      except AttributeError:
         # If exit or back, just return to go back
         if "exit" in cardID or "back" in cardID:
            return c.BACK
         # Else, a match wasn't found which probably means there was
         # and error reading the card or the card isn't a PSU ID card
         # but assume the former
         else:
            return c.ERROR_READING_CARD


   def getDbInfo(self):
      self.dbHost = raw_input("Database host: (" + c.DEFAULT_HOST + ") ")

      if self.dbHost == "":
         self.dbHost = c.DEFAULT_HOST

      self.dbTable = raw_input("Database table: (" + c.DEFAULT_TABLE + ") ")

      if self.dbTable == "":
         self.dbTable = c.DEFAULT_TABLE

      self.dbUser = raw_input("Database Username: (" + c.DEFAULT_USER + ") ")

      if self.dbUser == "":
         self.dbUser = c.DEFAULT_USER

      while 1:
         self.dbPass = getpass.getpass("Database Password: ")

         if self.dbPass == "":
            print "Database password cannot be blank."
         else:
            break


   def showCheckinConfirmation(self, accessID, pointValue):
      print "%s +%s points" % (accessID, pointValue)


   def showDatabaseError(self, error):
      print "\nWARNING! Database error:\n%s" % (error.args[1])


   def invalidInput(self):
      print "Invalid option. Try again."
