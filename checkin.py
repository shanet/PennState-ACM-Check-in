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
textMode = 0


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