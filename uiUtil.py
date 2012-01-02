import sys
from PyQt4.Qt import *
from time import sleep

from dbUtil import DbUtil
import constants as c


class UI(QApplication):
   def __init__(self, args):
      super(UI, self).__init__(args)

      # Show the login window
      self.loginWnd = LoginWnd()
      self.loginWnd.show()
      #self.connWnd = ConnectingWnd()
      #self.connWnd.show()



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
      self.loginBtn.clicked.connect(self.login)
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


   def login(self):
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

      # Create a new dbUtil object and have it connect to the database
      self.db = DbUtil(dbHost, "points", dbUser, dbPass)

      # Display the connecting window
      self.connWnd = ConnectingWnd()
      self.connWnd.show()

      # Connect to the DB
      #self.dbConn = self.db.connect()
      sleep(5)
      self.dbConn = None

      #self.connWnd.close()

      # If we failed to connect to the server just return to allow for re-entry of credentials
      """if self.dbConn == c.BAD_PASSWD:
         QMessageBox.critical(self, "Database Error", "Bad username or password", QMessageBox.Ok, QMessageBox.Ok)
         return
      elif self.dbConn == c.FAILURE:
         QMessageBox.critical(self, "Database Error", "Error connecting to database", QMessageBox.Ok, QMessageBox.Ok)
         return
      """

      # Connected to server. Launch the main window and hide the login window
      self.mainWnd = MainWnd(dbConn)
      self.mainWnd.show()
      self.close()



class MainWnd(QMainWindow):
   def __init__(self, dbConn):
      super(MainWnd, self).__init__()

      self.dbConn = dbConn
      self.initUI()

        
   def initUI(self):
      self.centralWidget = QWidget()
      logoPix = QPixmap("images/logo.png")
      self.logoImg = QLabel(self)
      self.checkinBtn = QPushButton("Check-in", self)
      self.showPointsBtn = QPushButton("Show Points", self)
      self.exitBtn = QPushButton("Exit", self)

      self.logoImg.setPixmap(logoPix)

      # Define button callbacks
      #checkinBtn.clicked.connect(self.login)
      #showPointsBtn.clicked.connect()
      self.exitBtn.clicked.connect(QCoreApplication.instance().quit)

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
        
      # Add the completeted layout to the window
      self.centralWidget.setLayout(vbox)
      self.setCentralWidget(self.centralWidget)

      # Center the window
      # setGeometry args are x, y, width, height
      self.setGeometry(0, 0, 600, 250)
      geo = self.frameGeometry()
      centerPt = QDesktopWidget().availableGeometry().center()
      geo.moveCenter(centerPt)
      self.move(geo.topLeft())
      
      # Title, icon, and statusbar
      self.setWindowTitle("ACM Points Check-in")
      #self.setWindowIcon(QIcon('web.png'))
      self.statusBar().showMessage("Connected to server")



class ConnectingWnd(QWidget):
   def __init__(self, parent=None):
      super(ConnectingWnd, self).__init__(parent)
        
      self.initUI()
      
        
   def initUI(self):
      # Create connecting image
      connPix = QPixmap("images/login_logo.png")
      self.connImg = QLabel(self)
      self.connImg.setPixmap(connPix)

      # Create host label and text edit
      self.connLabel = QLabel("Connecting...", self)

      hbox = QHBoxLayout()
      hbox.addStretch(1)
      hbox.addWidget(self.connImg)
      hbox.addWidget(self.connLabel)
      hbox.addStretch(1)

      self.setLayout(hbox)

      # Center the window
      # setGeometry args are x, y, width, height
      self.setGeometry(0, 0, 300, 150)
      geo = self.frameGeometry()
      centerPt = QDesktopWidget().availableGeometry().center()
      geo.moveCenter(centerPt)
      self.move(geo.topLeft())