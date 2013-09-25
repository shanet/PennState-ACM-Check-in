# Shane Tully
# 09.18.11
# Magnetic card check-in application for Penn State ACM


# Even though MySQLdb performs input sanitization internally, 
# it doesn't hurt to do it oursevles just to be on the safe side
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