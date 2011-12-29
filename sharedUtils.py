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
         if textMode && ("exit" in cardData or "back" in cardData):
            return "exit"
         # Else, a match wasn't found which probably means there was
         # and error reading the card or the card isn't a PSU ID card
         # but assume the former
         else:
            print "Error reading card. Swipe card again."
   return ""

      
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