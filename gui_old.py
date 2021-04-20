import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QIcon, QColor, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QAction, QMessageBox, QLabel, QVBoxLayout
from PyQt5.QtWidgets import QCalendarWidget, QFontDialog, QColorDialog, QTextEdit, QFileDialog
from PyQt5.QtWidgets import QCheckBox, QProgressBar, QComboBox, QLabel, QStyleFactory, QLineEdit, QInputDialog

station_id_dict = {'R.K. Puram':33,'Mandir Marg':21,'Anand Vihar':2,'Punjabi Bagh':40 }

STATION_ID = 0

class window(QMainWindow):

    def __init__(self):
        super(window, self).__init__()
        self.setGeometry(50, 50, 1080, 800)
        self.setWindowTitle('FRAMEWORK')
        # self.setWindowIcon(QIcon('EyantraLogoLarge.png'))
        self.home()


    def home(self):
       
        self.screen1()


        self.show()

    def screen1(self):
    	helloMsg = QLabel('<h1>Selection 1</h1>', self)
    	helloMsg.setGeometry(480,50,200,100)


    	self.styleChoise = QLabel('<h2>Choose Station</h2>', self)
    	comboBox = QComboBox(self)
    	comboBox.addItem('R.K. Puram')
    	comboBox.addItem('Mandir Marg')
    	comboBox.addItem('Anand Vihar')
    	comboBox.addItem('Punjabi Bagh')
    	comboBox.setGeometry(460,440,200,50)
    	self.styleChoise.setGeometry(455,400,200,50)
    	comboBox.activated[str].connect(self.style_choise)
    	
    	btn_ref_file = QPushButton('NEXT', self)
    	btn_ref_file.resize(500, 80)
    	btn_ref_file.move(100, 200)
    	btn_ref_file.clicked.connect(self.nextScreen)

    def nextScreen(self):
    	screens.setCurrentIndex(screens.currentIndex()+1)


    def style_choise(self, text):
    	global  STATION_ID
    	STATION_ID = (station_id_dict[text])


    def screen2(self):
    	helloMsg = QLabel('<h1>Selection 2</h1>', self)
    	helloMsg.setGeometry(480,50,200,100)

    	self.styleChoise = QLabel('<h2>Choose Something else</h2>', self)
    	comboBox = QComboBox(self)
    	comboBox.addItem('R.K. Puram')
    	comboBox.addItem('Mandir Marg')
    	comboBox.addItem('Anand Vihar')
    	comboBox.addItem('Punjabi Bagh')
    	comboBox.setGeometry(450,440,200,50)
    	self.styleChoise.setGeometry(455,400,200,50)
    	# comboBox.activated[str].connect(self.style_choise)


def run():
    app = QApplication(sys.argv)

    screens = QtWidgets.QStackedWidget()

    screens.addWidget(window.screen1)
    screens.addWidget(window.screen2)

    Gui = window()

    sys.exit(app.exec_())

run()