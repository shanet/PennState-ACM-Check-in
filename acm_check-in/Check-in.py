#!/usr/bin/env python2.7

# Shane Tully
# 09.18.11
# Magnetic card check-in application for Penn State ACM

import sys

from UIUtil import UI
from TextUtil import TextUI
import Constants as c
import DBUtil


def main(args):
   print "Penn State ACM Check-in System Version" , c.VERSION

   # Init textMode
   textMode = 0

   # Process the arguments
   if len(args) > 1:
      arg = args[1].lower()
      if arg == "--help":
         showHelp()
         sys.exit(0)
      elif arg == "--version":
         showVersion()
         sys.exit(0)
      elif arg == "--nogui":
         textMode = 1
      else:
         print "Invalid argument:", args[1]

   # Start the program into either textmode or GUI mode
   if textMode == 0:
      global app
      app = UI(args)
      app.exec_()
   else:
      TextUI().start()

   # Exit normally
   sys.exit(0)


def showHelp():
   print "Supress GUI:\t--nogui\nShow Help:\t--help\nShow Version:\t--version"

def showVersion():
   print "Version", c.VERSION


if __name__ == '__main__':
   main(sys.argv)
