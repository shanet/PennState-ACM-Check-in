import sys
from PyQt4 import QtGui, QtCore

from dbUtil import DbUtil
import constants as c


class LoginWnd(QtGui.QWidget):

   def __init__(self):
      super(LoginWnd, self).__init__()
        
      self.initUI()
        
   def initUI(self):
      # Add username label and text edit
      self.userLabel = QtGui.QLabel("Username:", self)
      self.userEdit = QtGui.QLineEdit(self)

      self.passLabel = QtGui.QLabel("Password:", self)
      self.passEdit = QtGui.QLineEdit(self)

      # Add login and exit buttons
      self.loginBtn = QtGui.QPushButton("Login", self)
      self.exitBtn = QtGui.QPushButton("Exit", self)
      
      self.loginBtn.setToolTip("Log in to MySQL server")
      self.exitBtn.setToolTip("Exit")

      self.loginBtn.resize(self.loginBtn.sizeHint())
      self.exitBtn.resize(self.exitBtn.sizeHint())

      # Set callbacks for login and exit buttons
      self.loginBtn.clicked.connect(self.login)
      self.exitBtn.clicked.connect(QtCore.QCoreApplication.instance().quit)

      # Configure the grid layout
      grid = QtGui.QGridLayout()
      grid.setSpacing(10)

      # Add username widgets
      grid.addWidget(self.userLabel, 0, 0)
      grid.addWidget(self.userEdit, 0, 1)

      # Add password widgets
      grid.addWidget(self.passLabel, 1, 0)
      grid.addWidget(self.passEdit, 1, 1)

      # Add login and exit buttons
      grid.addWidget(self.exitBtn, 2, 0)
      grid.addWidget(self.loginBtn, 2, 1)

      # Add grid to the hbox layout for horizontal centering
      hbox = QtGui.QHBoxLayout()
      hbox.addStretch(1)
      hbox.addLayout(grid)
      hbox.addStretch(1)

      # Add grid to vbox layout for vertical centering
      vbox = QtGui.QVBoxLayout()
      vbox.addStretch(1)
      vbox.addLayout(hbox)
      vbox.addStretch(1)
        
      # Add the completeted layout to the window
      self.setLayout(vbox)   

      # Center the window
      # setGeometry args are x, y, width, height
      self.setGeometry(0, 0, 500, 200)
      geo = self.frameGeometry()
      centerPt = QtGui.QDesktopWidget().availableGeometry().center()
      geo.moveCenter(centerPt)
      self.move(geo.topLeft())
      
      # Title and icon
      self.setWindowTitle("ACM Login")
      #self.setWindowIcon(QtGui.QIcon('web.png'))        
    
      self.show()


   def login(self):
      dbUser = str(self.userEdit.text())
      dbPass = str(self.passEdit.text())

      # Check if user or pass are empty
      if dbUser == "":
         QtGui.QMessageBox.warning(self, "Error", "User field cannot be empty", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
         return
      elif dbPass == "":
         QtGui.QMessageBox.warning(self, "Error", "Password field cannot be empty", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
         return

      # Create a new dbUtil object and have it connect to the database
      self.db = DbUtil("acm.psu.edu", "points", dbUser, dbPass)

      # TODO: Connecting dialog
      #connDialog = QDialog()
      #connLabel = QtGui.QLabel("Connecting...", connDialog)
      #connDialog.show()

      self.dbConn = self.db.connect()

      # If we failed to connect to the server just return to allow for re-entry of credentials
      if self.dbConn == c.BAD_PASSWD:
         QtGui.QMessageBox.critical(self, "Database Error", "Bad username or password", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
         return
      elif self.dbConn == c.FAILURE:
         QtGui.QMessageBox.critical(self, "Database Error", "Error connecting to database", QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)
         return

      # Connected to server. Launch the main window and hide the login window
      self.mainWnd = MainMenuWnd(None)
      self.close()



class MainMenuWnd(QtGui.QMainWindow):

   def __init__(self, dbConn):
      super(MainMenuWnd, self).__init__()

      self.dbConn = dbConn
      self.initUI()

        
   def initUI(self):
      centralWidget = QtGui.QWidget()
      logoPix = QtGui.QPixmap("images/logo.png")
      logoImg = QtGui.QLabel(self)
      checkinBtn = QtGui.QPushButton("Check-in", self)
      showPointsBtn = QtGui.QPushButton("Show Points", self)
      exitBtn = QtGui.QPushButton("Exit", self)

      logoImg.setPixmap(logoPix)

      # Define button callbacks
      #checkinBtn.clicked.connect(self.login)
      #showPointsBtn.clicked.connect()
      exitBtn.clicked.connect(QtCore.QCoreApplication.instance().quit)

      # Configure the grid layout
      grid = QtGui.QGridLayout()
      grid.setSpacing(10)

      # Add username widgets
      grid.addWidget(checkinBtn, 1, 0)
      grid.addWidget(showPointsBtn, 1, 1)
      grid.addWidget(exitBtn, 1, 2)

      # Add grid to the hbox layout for horizontal centering
      imgHBox = QtGui.QHBoxLayout()
      imgHBox.addStretch(1)
      imgHBox.addWidget(logoImg)
      imgHBox.addStretch(1)


      btnHBox = QtGui.QHBoxLayout()
      btnHBox.addStretch(1)
      btnHBox.addLayout(grid)
      btnHBox.addStretch(1)

      # Add grid to vbox layout for vertical centering
      vbox = QtGui.QVBoxLayout()
      vbox.addStretch(1)
      vbox.addLayout(imgHBox)
      vbox.addLayout(btnHBox)
      vbox.addStretch(1)
        
      # Add the completeted layout to the window
      centralWidget.setLayout(vbox)
      self.setCentralWidget(centralWidget)

      # Center the window
      # setGeometry args are x, y, width, height
      self.setGeometry(0, 0, 600, 250)
      geo = self.frameGeometry()
      centerPt = QtGui.QDesktopWidget().availableGeometry().center()
      geo.moveCenter(centerPt)
      self.move(geo.topLeft())
      
      # Title, icon, and statusbar
      self.setWindowTitle("ACM Points Check-in")
      #self.setWindowIcon(QtGui.QIcon('web.png'))
      self.statusBar().showMessage("Connected to server")

      self.show()