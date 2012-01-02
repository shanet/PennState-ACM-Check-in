import sys
import getpass

from dbUtil import DbUtil

# Constants
SUCCESS = 0

class TextUI:

   def __init__(self, dbHost, dbTable, dbUser, dbPass):
      db = DbUtil(dbHost, dbTable, dbUser, dbPass)

   def displayMenu(self):
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


   def connectToDatabase(self):
      # Use stdout.write to prevent newline
      sys.stdout.write("Connecting to database...")

      # Connect to the DB!
      status = db.connect()
      if status == SUCCESS:
         print "done."
      else if status = BAD_PASS:
         # Offer to re-enter password if bad password error
         print "\nError connecting to database. Bad password."
            return connectToDatabase(getDbPass())
      else:
         # Other error, print and die
         print "\nError connecting to database.\n%s\nExiting." % (e.args[1])
         sys.exit(1)


   def showDatabaseError(error):
      # Print a generic database error
      print "\nWARNING! Database error:\n%s" % (error.args[1])


   def getDbPass():
      return sanitizeInput(getpass.getpass("Database Password: "))


   def invalidInput():
      print "Invalid option. Try again."