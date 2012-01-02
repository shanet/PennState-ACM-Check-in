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








         def connect(self):
      # If a password was not given, ask for it
      if self.dbPass == "":
         self.dbPass = getDbPass()

      sys.stdout.write("Connecting to database...")
      try:
         # Connect to the DB!
         self.dbConn = MySQLdb.connect(host=self.dbHost, user=self.dbUser, passwd=self.dbPass, db=self.dbTable)
         print "done."
         return self.dbConn
      except MySQLdb.Error, e:
         # Offer to re-enter password if bad password error
         if "Access denied" in e.args[1]:
            print "\nError connecting to database. Bad password."
            return self.connect(getDbPass())
         # Other error, print and die
         else:
            print "\nError connecting to database.\n%s\nExiting." % (e.args[1])
            sys.exit(1)