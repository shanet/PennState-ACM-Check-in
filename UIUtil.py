# Shane Tully
# 09.18.11
# Magnetic card check-in application for Penn State ACM

import sys
import re
from PyQt4.Qt import *
import MySQLdb

from DBUtil import DB
from Threads import *
import SharedUtils
import Constants as c


class UI(QApplication):
   def __init__(self, args):
      super(UI, self).__init__(args)

      # Show the login window
      self.loginWnd = LoginWnd()
      self.loginWnd.show()



class LoginWnd(QMainWindow):
   def __init__(self):
      super(LoginWnd, self).__init__()
        
      self.initUI()
      
        
   def initUI(self):
      self.centralWidget = QWidget()

      # Create logo
      logoPix = QPixmap("images/login_logo.png")
      self.logoImg = QLabel(self)
      self.logoImg.setPixmap(logoPix)

      # Create host label and text edit
      self.hostLabel = QLabel("Host:", self)
      self.hostEdit = QLineEdit("acm.psu.edu", self)

      # Create username label and text edit
      self.userLabel = QLabel("Username:", self)
      self.userEdit = QLineEdit("points", self)

      self.passLabel = QLabel("Password:", self)
      self.passEdit = QLineEdit(self)
      # It's a password field; hide the input.
      self.passEdit.setEchoMode(QLineEdit.Password)

      # Create login and exit buttons
      self.loginBtn = QPushButton("Login", self)
      self.exitBtn = QPushButton("Exit", self)
      
      self.loginBtn.setToolTip("Log in to MySQL server")
      self.exitBtn.setToolTip("Exit")

      self.loginBtn.resize(self.loginBtn.sizeHint())
      self.exitBtn.resize(self.exitBtn.sizeHint())

      # Set callbacks for login and exit buttons
      self.loginBtn.clicked.connect(self.preLogin)
      self.exitBtn.clicked.connect(QCoreApplication.instance().quit)

      # Configure the grid layout
      grid = QGridLayout()
      grid.setSpacing(10)

      # Add host widgets
      grid.addWidget(self.hostLabel, 0, 0)
      grid.addWidget(self.hostEdit, 0, 1)

      # Add username widgets
      grid.addWidget(self.userLabel, 1, 0)
      grid.addWidget(self.userEdit, 1, 1)

      # Add password widgets
      grid.addWidget(self.passLabel, 2, 0)
      grid.addWidget(self.passEdit, 2, 1)

      # Add login and exit buttons
      grid.addWidget(self.exitBtn, 3, 0)
      grid.addWidget(self.loginBtn, 3, 1)

      # Add grid to the hbox layout for horizontal centering
      hbox = QHBoxLayout()
      hbox.addStretch(1)
      hbox.addWidget(self.logoImg)
      hbox.addLayout(grid)
      hbox.addStretch(1)

      # Add grid to vbox layout for vertical centering
      vbox = QVBoxLayout()
      vbox.addStretch(1)
      vbox.addLayout(hbox)
      vbox.addStretch(1)
        
      # Add the completeted layout to the window
      self.centralWidget.setLayout(vbox)
      self.setCentralWidget(self.centralWidget)  

      # Center the window
      # setGeometry args are x, y, width, height
      self.setGeometry(0, 0, 500, 200)
      geo = self.frameGeometry()
      centerPt = QDesktopWidget().availableGeometry().center()
      geo.moveCenter(centerPt)
      self.move(geo.topLeft())
      
      # Title and icon
      self.setWindowTitle("ACM Login")
      self.setWindowIcon(QIcon("images/login_logo.png"))
      self.statusBar().showMessage("Not connected to server  |  Penn State ACM Chceck-in System Version " + str(c.VERSION))



   def preLogin(self):
      dbHost = str(self.hostEdit.text())
      dbUser = str(self.userEdit.text())
      dbPass = str(self.passEdit.text())

      # Check if user or pass are empty
      if dbHost == "":
         QMessageBox.warning(self, "Error", "Host field cannot be empty", QMessageBox.Ok, QMessageBox.Ok)
         return
      elif dbUser == "":
         QMessageBox.warning(self, "Error", "User field cannot be empty", QMessageBox.Ok, QMessageBox.Ok)
         return
      elif dbPass == "":
         QMessageBox.warning(self, "Error", "Password field cannot be empty", QMessageBox.Ok, QMessageBox.Ok)
         return

      # Display the connecting window
      self.connWnd = ConnectingWnd()
      self.connWnd.show()

      # Create a new dbUtil object and have it connect to the database
      self.loginThread = LoginThread(dbHost, c.DEFAULT_TABLE, dbUser, dbPass)

      self.connect(self.loginThread, SIGNAL("postLogin(PyQt_PyObject, PyQt_PyObject)"), self.postLogin)

      self.loginThread.start()


   def postLogin(self, loginStatus, db):
      # Close the connecting window
      self.connWnd.close()

      # If we failed to connect to the server just return to allow for re-entry of credentials
      if loginStatus == c.BAD_PASSWD:
         QMessageBox.critical(self, "Database Error", "Bad username or password", QMessageBox.Ok, QMessageBox.Ok)
         return
      elif loginStatus == c.FAILURE:
         QMessageBox.critical(self, "Database Error", "Error connecting to database", QMessageBox.Ok, QMessageBox.Ok)
         return

      # Connected to server. Launch the main window and hide the login window
      self.mainWnd = MainWnd(db)
      self.mainWnd.show()
      self.close()



class MainWnd(QMainWindow):
   def __init__(self, db):
      super(MainWnd, self).__init__()

      self.db = db

      # Init card input so it can be appended to later
      self.cardInput = ""

      # Compile the regex for pulling the card ID from all the data on a card
      self.regex = re.compile(";(.+)=")

      self.initUI()

        
   def initUI(self):
      # Center the window
      # setGeometry args are x, y, width, height
      self.setGeometry(0, 0, 500, 100)
      geo = self.frameGeometry()
      centerPt = QDesktopWidget().availableGeometry().center()
      geo.moveCenter(centerPt)
      self.move(geo.topLeft())
      
      # Title, icon, and statusbar
      self.setWindowTitle("ACM Points Check-in")
      self.setWindowIcon(QIcon("images/login_logo.png"))
      self.statusBar().showMessage("Connected to server  |  Penn State ACM Chceck-in System Version " + str(c.VERSION))

      # Init all the central widgets
      self.initMainMenuWidget()
      self.initCheckinWidget()
      self.initShowPointsWidget()

      # Init the central stacked widget and set it as the central widget
      # This allows us to change the central widget easily
      self.centralWidget = QStackedWidget()
      self.setCentralWidget(self.centralWidget)
      
      # Add the widgets to the main central stacked widget
      self.centralWidget.addWidget(self.mainMenuWidget)
      self.centralWidget.addWidget(self.checkinWidget)
      self.centralWidget.addWidget(self.showPointsWidget)

      # Show the main menu first
      self.showMainMenuWidget()

   
   def keyPressEvent(self, event):
      # Only look for card swipes if the checkin widget is currently shown
      if self.centralWidget.currentWidget() == self.checkinWidget:
         try:
            # Try to match the input to the card ID regex
            cardID = self.regex.search(self.cardInput).group(1)

            # A match was made so reset cardInput for the next card
            self.cardInput = ""

            # Set the card ID and start the checkin thread
            # cardID is going into an SQL query; don't forget to sanitize the input
            if not self.checkinThread.isRunning():
                  self.checkinThread.setCardID(SharedUtils.sanitizeInput(str(cardID)))
                  self.checkinThread.start()

         except AttributeError:
            # If a match was not made append the current text to card input
            self.cardInput += event.text()


   def closeEvent(self, closeEvent):
      print "Cleaning up and exiting..."
      if self.db is not None:
         self.db.close()
      closeEvent.accept();


   def initMainMenuWidget(self):
      self.mainMenuWidget = QWidget()

      logoPix = QPixmap("images/main_logo.png")
      self.logoImg = QLabel(self)
      self.checkinBtn = QPushButton("Check-in", self)
      self.showPointsBtn = QPushButton("Show Points", self)
      self.exitBtn = QPushButton("Exit", self)

      # Size the images properly
      logoPix = logoPix.scaledToWidth(450)
      self.logoImg.setPixmap(logoPix)

      # Define button callbacks
      self.checkinBtn.clicked.connect(self.showCheckinWidget)
      self.showPointsBtn.clicked.connect(self.showShowPointsWidget)
      self.exitBtn.clicked.connect(self.close)

      # Configure the grid layout
      grid = QGridLayout()
      grid.setSpacing(10)

      # Add username widgets
      grid.addWidget(self.checkinBtn, 1, 0)
      grid.addWidget(self.showPointsBtn, 1, 1)
      grid.addWidget(self.exitBtn, 1, 2)

      # Add grid to the hbox layout for horizontal centering
      imgHbox = QHBoxLayout()
      imgHbox.addStretch(1)
      imgHbox.addWidget(self.logoImg)
      imgHbox.addStretch(1)

      btnHbox = QHBoxLayout()
      btnHbox.addStretch(1)
      btnHbox.addLayout(grid)
      btnHbox.addStretch(1)

      # Add grid to vbox layout for vertical centering
      vbox = QVBoxLayout()
      vbox.addStretch(1)
      vbox.addLayout(imgHbox)
      vbox.addLayout(btnHbox)
      vbox.addStretch(1)
        
      # Add the completeted layout to the main menu widget
      self.mainMenuWidget.setLayout(vbox)

   
   def initCheckinWidget(self):
      self.checkinWidget = QWidget()

      # Init widgets
      self.cardPix = QPixmap("images/magnetic_card.png")
      self.greenPix = QPixmap("images/green_check_mark.png")
      self.redPix = QPixmap("images/red_x_mark.png")
      self.checkinImg = QLabel(self)
      self.checkinLabel = QLabel("Waiting for card swipe...")
      self.checkinBackBtn = QPushButton("Back", self)

      # Size the images properly
      self.cardPix = self.cardPix.scaledToHeight(175)
      self.greenPix = self.greenPix.scaledToHeight(175)
      self.redPix = self.redPix.scaledToHeight(175)

      # Add the card image to image widget
      self.checkinImg.setPixmap(self.cardPix)

      # Set the font for the checkin label
      font = QFont("Sans Serif", 16, QFont.Bold)
      self.checkinLabel.setFont(font)

      # Add signals to buttons
      self.checkinBackBtn.clicked.connect(self.closeCheckinScreen)

      # Center the image
      imgHbox = QHBoxLayout()
      imgHbox.addStretch(1)
      imgHbox.addWidget(self.checkinImg)
      imgHbox.addStretch(1)

      # Add widgets to vbox layout for vertical centering
      vbox = QVBoxLayout()
      vbox.addStretch(1)
      vbox.addLayout(imgHbox)
      vbox.addWidget(self.checkinLabel)
      vbox.addWidget(self.checkinBackBtn)
      vbox.addStretch(1)

      # Add grid to the hbox layout for horizontal centering
      hbox = QHBoxLayout()
      hbox.addStretch(1)
      hbox.addLayout(vbox)
      hbox.addStretch(1)

      # Add the completeted layout to the overall check-in widget
      self.checkinWidget.setLayout(hbox)

   
   def initShowPointsWidget(self):
      self.showPointsWidget = QWidget()

      # Init widgets
      self.pointsTitle = QLabel("Current Points Standings")
      self.pointsScrollArea = QScrollArea()
      self.pointsScrollWidget = QWidget()
      self.pointsAccessIDLabel = QLabel()
      self.pointsPointsLabel = QLabel()
      self.pointsBackBtn = QPushButton("Back", self)

      # Set the font for the checkin label
      self.pointsTitle.setFont(QFont("Sans Serif", 12, QFont.Bold))

      # Add signals to buttons
      self.pointsBackBtn.clicked.connect(self.closeShowPointsScreen)

      # Create the layout for the points scroll area
      self.pointsAccessIDLabel.setFont(QFont("Monospace", 8, QFont.Normal))
      self.pointsPointsLabel.setFont(QFont("Monospace", 8, QFont.Normal))

      self.pointsAccessIDLabel.setMinimumSize(60, 700)
      self.pointsPointsLabel.setMinimumSize(50, 700)
      
      self.pointsScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

      pointsHbox = QHBoxLayout()
      pointsHbox.addStretch(1)
      pointsHbox.addWidget(self.pointsAccessIDLabel)
      pointsHbox.addWidget(self.pointsPointsLabel)
      pointsHbox.addStretch(1)

      pointsVbox = QVBoxLayout()
      pointsVbox.addLayout(pointsHbox)
      pointsVbox.addStretch(1)

      self.pointsScrollWidget.setLayout(pointsVbox)
      self.pointsScrollArea.setWidget(self.pointsScrollWidget)

      # Center the title label
      titleHbox = QHBoxLayout()
      titleHbox.addStretch(1)
      titleHbox.addWidget(self.pointsTitle)
      titleHbox.addStretch(1)

      # Add widgets to vbox layout for vertical centering
      vbox = QVBoxLayout()
      vbox.addStretch(1)
      vbox.addLayout(titleHbox)
      vbox.addWidget(self.pointsScrollArea)
      vbox.addWidget(self.pointsBackBtn)
      vbox.addStretch(1)

      # Add grid to the hbox layout for horizontal centering
      hbox = QHBoxLayout()
      hbox.addStretch(1)
      hbox.addLayout(vbox)
      hbox.addStretch(1)

      # Add the completeted layout to the overall show points widget
      self.showPointsWidget.setLayout(hbox)


   def showMainMenuWidget(self):
      self.centralWidget.setCurrentWidget(self.mainMenuWidget)


   def showCheckinWidget(self):
      self.centralWidget.setCurrentWidget(self.checkinWidget)

      # Get the point value
      while 1:
         pointValue, ok = QInputDialog.getText(self, "Point Value", "Point Value:")

         if ok:
            if str(pointValue).isdigit():
               break
            else:
               QMessageBox.critical(self, "Input Error", "Invalid input", QMessageBox.Ok, QMessageBox.Ok)
         else:
            self.closeCheckinScreen()
            return
      
      # Init the checkin thread
      # pointValue will be used in SQL queries. Sanitize it.
      self.checkinThread = CheckinThread(self.db, SharedUtils.sanitizeInput(str(pointValue)))
      self.connect(self.checkinThread, SIGNAL("postCardSwipe(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), 
                  self.postCardSwipe)

   
   def showShowPointsWidget(self):
      self.centralWidget.setCurrentWidget(self.showPointsWidget)

      # Get the access ID to show points for or an empty string for all access ID's
      accessID, ok = QInputDialog.getText(self, "Access ID", "Access ID (blank for all access ID\'s):")

      if not ok:
         # The show points thread was not declared yet so just skip the closeShowPointsScreen function
         self.showMainMenuWidget()
      
      # Init the show points thread
      # accessID will be used in SQL queries. Sanitize it.
      self.showPointsThread = ShowPointsThread(self.db, SharedUtils.sanitizeInput(str(accessID)))
      self.connect(self.showPointsThread, SIGNAL("setPoints(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), 
                  self.setPoints)
      self.showPointsThread.start()


   def closeCheckinScreen(self):
      # End the checkin thread we started
      self.checkinThread.terminate()

      self.showMainMenuWidget()

   
   def closeShowPointsScreen(self):
      # End the show points thread we started
      self.showPointsThread.terminate()

      self.showMainMenuWidget()


   def postCardSwipe(self, checkinStatus, accessID, cardID, sqlError, pointValue):
      if checkinStatus == c.SQL_ERROR:
         QMessageBox.critical(self, "Database Error", "WARNING! Database error: " + sqlError.args[1], QMessageBox.Ok, QMessageBox.Ok)
         # Don't bother to change UI elements or start the sleep thread, just wait for the next card
         return
      elif checkinStatus == c.BAD_CHECKIN_TIME:
         self.checkinImg.setPixmap(self.redPix)
         self.checkinLabel.setText("You may only check-in once per hour.")
      elif checkinStatus == c.FUTURE_CHECKIN_TIME:
         self.checkinImg.setPixmap(self.redPix)
         self.checkinLabel.setText("Previous check-in time was in the future. Check your local system time.")
      elif checkinStatus == c.SUCCESS:
         self.checkinImg.setPixmap(self.greenPix)
         self.checkinLabel.setText(str(accessID) + " +" + str(pointValue) + " points")
      elif checkinStatus == c.CARD_NOT_IN_DB:
         # If the card is not in the DB ask to add it
         reply = QMessageBox.question(self, "Card Not in Database", "This card was not found in the database. Add it now?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
         if reply == QMessageBox.Yes:
            # If adding new card, get the accessID associated with the card
            accessID, ok = QInputDialog.getText(self, "Add New Card", "Access ID:")

            # Sanitize the accessID input and call the add card thread
            if ok and accessID != "":
               self.addCardThread = AddCardThread(self.db, cardID, SharedUtils.sanitizeInput(str(accessID)), pointValue)
               self.connect(self.addCardThread, SIGNAL("postCardSwipe(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), 
                           self.postCardSwipe)
               self.addCardThread.start()
         # Don't bother to change UI elements or start the sleep thread, just wait for the next card
         return
      else:
         self.checkinImg.setPixmap(self.redPix)
         self.checkinLabel.setText("An unknown error occurred.")
         QMessageBox.critical(self, "Unknown Error", "An unknown error occurred", QMessageBox.Ok, QMessageBox.Ok)

      # Force a repaint of the UI
      self.checkinImg.update()
      self.checkinLabel.update()

      # Sleep for a few seconds before resetting the UI for the next card
      # This must be on a separate thread since blocking the UI thread is a big no-no
      self.sleepThread = SleepThread(3)
      self.connect(self.sleepThread, SIGNAL("resetCheckinWidget()"), self.resetCheckinWidget)
      self.sleepThread.start()
      
            
   def resetCheckinWidget(self):
      # Reset the UI for a new card swipe
      self.checkinImg.setPixmap(self.cardPix)
      self.checkinLabel.setText("Waiting for card swipe...")
      self.checkinImg.update()
      self.checkinLabel.update()

   
   def setPoints(self, showPointsStatus, pointsTuple, sqlError):
      accessIDs = ""
      points = ""
      
      for i in range(len(pointsTuple)):
         accessIDs += str(pointsTuple[i][0]) + "\n"
         points += "| " + str(pointsTuple[i][1]) + "\n"

      self.pointsAccessIDLabel.setText(accessIDs)
      self.pointsPointsLabel.setText(points)

      self.pointsAccessIDLabel.update()
      self.pointsPointsLabel.update()




class ConnectingWnd(QWidget):
   def __init__(self, parent=None):
      super(ConnectingWnd, self).__init__(parent)
        
      self.initUI()
      
        
   def initUI(self):
      # Create connecting image
      connMov = QMovie("images/loading_icon.gif")
      connMov.start()
      self.connImg = QLabel(self)
      self.connImg.setMovie(connMov)

      # Create host label and text edit
      self.connLabel = QLabel("Connecting...", self)
      self.connLabel.setFont(QFont("Sans Serif", 10, QFont.Bold))

      hbox = QHBoxLayout()
      hbox.addStretch(1)
      hbox.addWidget(self.connImg)
      hbox.addStretch(1)
      hbox.addWidget(self.connLabel)
      hbox.addStretch(1)

      self.setLayout(hbox)

      # Center the window
      # setGeometry args are x, y, width, height
      self.setGeometry(0, 0, 250, 100)
      geo = self.frameGeometry()
      centerPt = QDesktopWidget().availableGeometry().center()
      geo.moveCenter(centerPt)
      self.move(geo.topLeft())