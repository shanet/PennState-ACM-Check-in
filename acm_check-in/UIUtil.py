# Shane Tully
# 09.18.11
# Magnetic card check-in application for Penn State ACM

import re
import sys
import time

from PySide.QtGui import *
from PySide.QtCore import *

from DBUtil import DB
from Threads import *
import SharedUtils
import Constants as c
import Utils


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
      logoPix = QPixmap(Utils.getAbsoluteResourcePath("images/login_logo.png"))
      self.logoImg = QLabel(self)
      self.logoImg.setPixmap(logoPix)

      # Create host label and text edit
      self.hostLabel = QLabel("Host:", self)
      self.hostEdit = QLineEdit(c.DEFAULT_HOST, self)

      # Create table label and table edit
      self.tableLabel = QLabel("Table:", self)
      self.tableEdit = QLineEdit(c.DEFAULT_TABLE, self)

      # Create username label and text edit
      self.userLabel = QLabel("Username:", self)
      self.userEdit = QLineEdit("points", self)

      self.passLabel = QLabel("Password:", self)
      self.passEdit = QLineEdit(self)
      # It's a password field; hide the input.
      self.passEdit.setEchoMode(QLineEdit.Password)
      self.passEdit.returnPressed.connect(self.preLogin)

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

      # Add table widgets
      grid.addWidget(self.tableLabel, 1, 0)
      grid.addWidget(self.tableEdit, 1, 1)

      # Add username widgets
      grid.addWidget(self.userLabel, 2, 0)
      grid.addWidget(self.userEdit, 2, 1)

      # Add password widgets
      grid.addWidget(self.passLabel, 3, 0)
      grid.addWidget(self.passEdit, 3, 1)

      # Add login and exit buttons
      grid.addWidget(self.exitBtn, 4, 0)
      grid.addWidget(self.loginBtn, 4, 1)

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
      self.setWindowIcon(QIcon(Utils.getAbsoluteResourcePath("images/login_logo.png")))
      self.statusBar().showMessage("Not connected to server  |  Penn State ACM Chceck-in System Version " + str(c.VERSION))



   def preLogin(self):
      dbHost = str(self.hostEdit.text())
      dbTable = str(self.tableEdit.text())
      dbUser = str(self.userEdit.text())
      dbPass = str(self.passEdit.text())

      # Check if user or pass are empty
      if dbHost == "":
         QMessageBox.warning(self, "Error", "Host field cannot be empty", QMessageBox.Ok, QMessageBox.Ok)
         return
      elif dbTable == "":
         QMessageBox.warning(self, "Error", "Table field cannot be empty", QMessageBox.Ok, QMessageBox.Ok)
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
      self.loginThread = LoginThread(dbHost, c.DEFAULT_DATABASE, dbTable, dbUser, dbPass, self.postLogin)
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
      self.regex = re.compile(";([0-9]+)=[0-9]+\?")

      # Declare sleepThread
      self.sleepThread = SleepThread(c.TIME_BETWEEN_CHECKINS, self.resetCheckinWidget)

      self.initUI()

        
   def initUI(self):
      # Center the window
      # setGeometry args are x, y, width, height
      self.setGeometry(0, 0, 550, 100)
      geo = self.frameGeometry()
      centerPt = QDesktopWidget().availableGeometry().center()
      geo.moveCenter(centerPt)
      self.move(geo.topLeft())
      
      # Title, icon, and statusbar
      self.setWindowTitle("ACM Points Check-in")
      self.setWindowIcon(QIcon(Utils.getAbsoluteResourcePath("images/login_logo.png")))
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
      self.centralWidget.addWidget(self.pointsWidget)

      # Show the main menu first
      self.showMainMenuWidget()

   
   def keyPressEvent(self, event):
      # Only look for card swipes if the checkin widget is currently shown
      if self.centralWidget.currentWidget() == self.checkinWidget:
         try:
            # Try to match the input to the card ID regex
            r =  self.regex.search(self.cardInput)
            cardID = r.groups()[0]

            # A match was made so reset cardInput for the next card
            self.cardInput = ""

            # Set the card ID and start the checkin thread
            # cardID is going into an SQL query; don't forget to sanitize the input
            if not (self.checkinThread.isRunning() and self.sleepThread.isRunning()):
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

      checkinButton = QImageButton("Check-in", Utils.getAbsoluteResourcePath('images/magnetic_card.png'), self.showCheckinWidget, 100, self)
      showPointsButton = QImageButton("Show Points", Utils.getAbsoluteResourcePath('images/trophy.png'), self.showPointsWidget, 100, self)

      hbox = QHBoxLayout()
      hbox.addStretch(1)
      hbox.addWidget(checkinButton)
      hbox.addSpacing(45)
      hbox.addWidget(showPointsButton)
      hbox.addStretch(1)

      self.mainMenuWidget.setLayout(hbox)

   
   def initCheckinWidget(self):
      self.checkinWidget = QWidget()

      # Init widgets
      self.cardPix = QPixmap(Utils.getAbsoluteResourcePath("images/magnetic_card.png"))
      self.greenPix = QPixmap(Utils.getAbsoluteResourcePath("images/green_check_mark.png"))
      self.redPix = QPixmap(Utils.getAbsoluteResourcePath("images/red_x_mark.png"))
      self.checkinImg = QLabel(self)
      self.checkinLabel = QLabel("Waiting for card swipe...")
      self.checkinBackBtn = QPushButton("Back", self)

      # Size the images properly
      self.cardPix = self.cardPix.scaledToHeight(175, Qt.SmoothTransformation)
      self.greenPix = self.greenPix.scaledToHeight(175, Qt.SmoothTransformation)
      self.redPix = self.redPix.scaledToHeight(175, Qt.SmoothTransformation)

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
      self.pointsWidget = QWidget()

      self.checkinThread = None

      # Init widgets
      self.pointsTitle = QLabel("Current Points Standings")
      self.pointsTextArea = QTextEdit()
      self.pointsBackBtn = QPushButton("Back", self)

      # Set the font for the checkin label
      self.pointsTitle.setFont(QFont("Sans Serif", 12, QFont.Bold))

      # Add signals to buttons
      self.pointsBackBtn.clicked.connect(self.closeShowPointsScreen)

      # Create the layout for the points scroll area
      self.pointsTextArea.setFont(QFont("Monospace", 8, QFont.Normal))

      # Add widgets to vbox layout for vertical centering
      vbox = QVBoxLayout()
      vbox.addStretch(1)
      vbox.addWidget(self.pointsTitle, alignment=Qt.AlignCenter)
      vbox.addWidget(self.pointsTextArea)
      vbox.addWidget(self.pointsBackBtn)
      vbox.addStretch(1)

      self.pointsWidget.setLayout(vbox)


   def showMainMenuWidget(self):
      self.centralWidget.setCurrentWidget(self.mainMenuWidget)


   def showCheckinWidget(self):
      self.centralWidget.setCurrentWidget(self.checkinWidget)

      # Get the point value
      while 1:
         pointValue, ok = QInputDialog.getText(self, "Point Value", "Point Value:", text=str(c.DEFAULT_POINTS))

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
      self.checkinThread = CheckinThread(self.db, SharedUtils.sanitizeInput(str(pointValue)), self.postCardSwipe)

   
   def showPointsWidget(self):
      self.pointsTextArea.clear()
      self.centralWidget.setCurrentWidget(self.pointsWidget)

      # Get the access ID to show points for or an empty string for all access ID's
      accessID, ok = QInputDialog.getText(self, "Access ID", "Access ID (blank for all access ID\'s):")

      if not ok:
         # The show points thread was not declared yet so just skip the closeShowPointsScreen function
         self.showMainMenuWidget()
      
      # Init the show points thread
      # accessID will be used in SQL queries. Sanitize it.
      self.showPointsThread = ShowPointsThread(self.db, SharedUtils.sanitizeInput(str(accessID)), self.setPoints)
      self.showPointsThread.start()


   def closeCheckinScreen(self):
      # End the checkin thread we started
      if self.checkinThread is not None:
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
      elif checkinStatus == c.ERROR_READING_CARD:
         self.checkinImg.setPixmap(self.redPix)
         self.checkinLabel.setText("Error reading card. Swipe again.")
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
         reply = QMessageBox.question(self, "Card Not in Database", "This card was not found in the database. Add it now?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

         if reply == QMessageBox.Yes:
            # If adding new card, get the accessID associated with the card
            accessID, ok = QInputDialog.getText(self, "Add New Card", "Access ID:")

            # Sanitize the accessID input and call the add card thread
            if ok and accessID != "":
               self.addCardThread = AddCardThread(self.db, cardID, SharedUtils.sanitizeInput(str(accessID)), pointValue, self.postCardSwipe)
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
      # The number of seconds is defined in the constants file
      # This must be on a separate thread since blocking the UI thread is a big no-no
      self.sleepThread.start()
      
            
   def resetCheckinWidget(self):
      # Reset the UI for a new card swipe
      self.checkinImg.setPixmap(self.cardPix)
      self.checkinLabel.setText("Waiting for card swipe...")
      self.checkinImg.update()
      self.checkinLabel.update()

   
   def setPoints(self, showPointsStatus, pointsTuple, sqlError):
      if showPointsStatus == c.NO_RESULTS:
            QMessageBox.critical(self, "Empty Query", "The specified access ID was not found in the database", QMessageBox.Ok, QMessageBox.Ok)
            return
      for i in range(len(pointsTuple)):
         accessID = str(pointsTuple[i][0])
         points = str(pointsTuple[i][1])
         self.pointsTextArea.append(accessID + "\t" + points)

      # Move the scrollbar to the top
      scrollbar = self.pointsTextArea.verticalScrollBar()
      scrollbar.setValue(scrollbar.minimum())


class ConnectingWnd(QWidget):
   def __init__(self, parent=None):
      super(ConnectingWnd, self).__init__(parent)
        
      self.initUI()
      
        
   def initUI(self):
      # Create connecting image
      connMov = QMovie(Utils.getAbsoluteResourcePath("images/loading_icon.gif"))
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


class QImageButton(QWidget):
    def __init__(self, buttonText, imagePath, buttonCallback, imageSize, parent=None):
        QWidget.__init__(self, parent)

        icon = QLabel(self)
        icon.setPixmap(QPixmap(imagePath).scaled(imageSize, imageSize, TransformationMode = Qt.SmoothTransformation))

        button = QPushButton(buttonText)
        button.clicked.connect(buttonCallback)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(icon, alignment=Qt.AlignHCenter)
        vbox.addSpacing(20)
        vbox.addWidget(button)
        vbox.addStretch(1)

        # Add some horizontal padding
        hbox = QHBoxLayout()
        hbox.addSpacing(10)
        hbox.addLayout(vbox)
        hbox.addSpacing(10)

        groupBox = QGroupBox()
        groupBox.setLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(groupBox)
        hbox.addStretch(1)

        self.setLayout(hbox)
