import sys
import re
from csv import DictWriter
from PyQt5.QtWidgets import QWidget, QLabel, QApplication
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QIcon, QColor, QPixmap, QFont, QIntValidator
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QAction, QMessageBox, QLabel, QVBoxLayout
from PyQt5.QtWidgets import QCalendarWidget, QFontDialog, QColorDialog, QTextEdit, QFileDialog
from PyQt5.QtWidgets import QCheckBox, QProgressBar, QComboBox, QLabel, QStyleFactory, QLineEdit, QInputDialog

import data_load_proxy,missing_values,features,model

# screen variable for the screen widget
screens = ''

#### VARIABLES THAT ARE NEEDED FOR FRAMEWORK ####

## STATION_ID

station_id_dict = {'R.K. Puram':33,'Mandir Marg':21,'Anand Vihar':2,'Punjabi Bagh':40 }
STATION_ID = 33 ## THIS VALUE WILL GET SET IN def station_select() in Screen1

## TIME INTERVAL ( 15 minutes,30 minutes,1 hour,4 hour,8 hour,12 hour,24 hour)

INTERVAL = '30 minutes'

## MISSING VALUES:

#1. TEMPERATURE
TEMP_NA = 0
temp_na_dict = {'Wunderground data':0,'3 Nearest Stations':1, "Don't fill (Drop NA)":2}

#2. PM10 & PM2.5
PM_NA = 0
pm_na_dict = {'Previous Avg Values':0,'3 Nearest Stations':1, "Don't fill (Drop NA)":2}

#3. OTHER POLLUTANTS
POLL_NA = 0
poll_na_dict = {'Previous Avg Values':0,'3 Nearest Stations':1, "Don't fill (Drop NA)":2}

#4. METERIOLOGICAL PARAMETERS
MET_NA = 0
met_na_dict = {'Use Wunderground Values':0,'Previous Avg Values':1,'3 Nearest Stations':2, "Don't fill (Drop NA)":3}

## FEATURE ENGINEERING:

features_dict = {'PM10_yest':0,'PM10_week':0,'PM10_month':0,'PM2_yest':0,'PM2_week':0,'PM2_month':0, 'PM10_last_yest':0,'PM10_last_week':0,'PM10_last_month':0,'PM2_last_yest':0,'PM2_last_week':0,'PM2_last_month':0,'seasons':0,'weekends':0,'all_pollutants':0,'all_met':0}

## LAG:
LAG_TARGET = 0
LAG_POLL = 0

## MODEL:
target_dict = {'PM 2.5':0,'PM 10':1}
TARGET = 0

standard_dict = {'No Standardization':0, 'Standard Scaling':1,'Min Max Scaling':2}
STANDARDIZATION = 0

SPLIT_PERC = 20

model_dict = {'Linear Regression':0,'Ridge Regression':1,'Lasso Regression':2,
     'Elastic Net Regression':3,'SGD Regression':4,
      'Decision Tree':5,'Random Forest':6,'Ada Boost':7,
     'Bagging':8,'Gradient Boost':9,'XGBoost':10,'Extra Trees':11,'SVR':12,
     'HistGradientBoosting':13,'LGBMRegressor':14,'CatBoostRegressor':15}
MODEL = 0

metrics_dict = {'RMSE':1,'R2 score':1,'MAE':1,'MAPE':1}

df = []

result = ''

## Screen1: Station select and Interval setting
class Screen1(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        helloMsg = QLabel('<h1>Selection 1: Choose Station and Interval</h1>', self)
        helloMsg.setGeometry(320,50,600,100)


        self.station = QLabel('<h2>Choose Station</h2>', self)
        station_choice = QComboBox(self)
        station_choice.addItem('R.K. Puram')
        station_choice.addItem('Mandir Marg')
        station_choice.addItem('Anand Vihar')
        station_choice.addItem('Punjabi Bagh')
        station_choice.setGeometry(460,290,200,50)
        self.station.setGeometry(485,250,200,50)
        station_choice.activated[str].connect(self.station_select)

        show_process = QLabel('(Pressing on Continue will start the processing)', self)
        show_process.setGeometry(410,530,500,100)

        self.interval = QLabel('<h2>Choose Time Interval</h2>', self)
        interval_choice = QComboBox(self)
        interval_choice.addItem('15 minutes')
        interval_choice.addItem('30 minutes')
        interval_choice.addItem('1 hour')
        interval_choice.addItem('4 hours')
        interval_choice.addItem('8 hours')
        interval_choice.addItem('12 hours')
        interval_choice.addItem('24 hours')
        interval_choice.setGeometry(460,390,200,50)
        self.interval.setGeometry(460,350,200,50)
        interval_choice.activated[str].connect(self.interval_select)
        
        btn_next_screen = QPushButton('Continue', self)
        btn_next_screen.resize(500, 80)
        btn_next_screen.move(300, 500)
        btn_next_screen.clicked.connect(self.nextScreen)
        #self.show()


    def nextScreen(self):
        ## Go to next screen on clicking Continue Button

        s2 = Screen2()
        screens.addWidget(s2)
        screens.setCurrentIndex(screens.currentIndex()+1)


    def station_select(self,text):
        global  STATION_ID
        STATION_ID = station_id_dict[text]

    def interval_select(self,text):
        global INTERVAL
        INTERVAL = text
        #print(INTERVAL)

## SCREEN 1 is done here


## SCREEN 2 has display labels for showing what all processing has been done
class Screen2(QWidget): 

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        print('In Screen 2')
        processMsg = QLabel('<h1>File Processed</h1>', self)
        processMsg.setGeometry(400,50,300,100)

        stats = data_load_proxy.start_load(STATION_ID,INTERVAL)
        #stats = {'ok':True, 'process':'Done a lot!'}
        statsMsg = QLabel(stats['process'],self)
        statsMsg.setGeometry(200,150,600,300)


        if stats['ok'] == True:

            btn_next_screen = QPushButton('Continue', self)
            btn_next_screen.resize(500, 80)
            btn_next_screen.move(300, 500)
            btn_next_screen.clicked.connect(self.nextScreen)

        else: 
            errMsg = QLabel('<h3>Some error occured. Please try another configuration</h3>',self)
            errMsg.setGeometry(400,500,300,100)

        btn_back = QPushButton('Back', self)
        btn_back.resize(80, 50)
        btn_back.move(50, 20)
        btn_back.clicked.connect(self.backScreen)

    def backScreen(self):

        screens.setCurrentIndex(screens.currentIndex()-1)


    def nextScreen(self):

        s3 = Screen3()
        screens.addWidget(s3)
        screens.setCurrentIndex(screens.currentIndex()+1)

## Filling Missing Values
class Screen3(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        print('In Screen 3')
        helloMsg = QLabel('<h1>Selection 2: How to fill missing values?</h1>', self)
        helloMsg.setGeometry(340,50,500,100)


        self.temp = QLabel('<h2>Fill Temperature column using</h2>', self)
        temp_choice = QComboBox(self)
        temp_choice.addItem('Wunderground data')
        temp_choice.addItem('3 Nearest Stations')
        temp_choice.addItem("Don't fill (Drop NA)")
        temp_choice.setGeometry(140,240,200,50)
        self.temp.setGeometry(100,200,300,50)
        temp_choice.activated[str].connect(self.temp_select)


        self.pm = QLabel('<h2>Fill PM2.5 & PM10 column using</h2>', self)
        pm_choice = QComboBox(self)
        pm_choice.addItem('Previous Avg Values')
        pm_choice.addItem('3 Nearest Stations')
        pm_choice.addItem("Don't fill (Drop NA)")
        pm_choice.setGeometry(690,240,200,50)
        self.pm.setGeometry(650,200,300,50)
        pm_choice.activated[str].connect(self.pm_select)


        self.pollutants = QLabel('<h2>Fill other Pollutants columns using</h2>', self)
        pollutants_choice = QComboBox(self)
        pollutants_choice.addItem('Previous Avg Values')
        pollutants_choice.addItem('3 Nearest Stations')
        pollutants_choice.addItem("Don't fill (Drop NA)")
        pollutants_choice.setGeometry(140,410,200,50)
        self.pollutants.setGeometry(80,370,400,50)
        pollutants_choice.activated[str].connect(self.pollutants_select)


        self.met = QLabel('<h2>Fill other Meteriological columns using</h2>', self)
        met_choice = QComboBox(self)
        met_choice.addItem('Use Wunderground Values')
        met_choice.addItem('Previous Avg Values')
        met_choice.addItem('3 Nearest Stations')
        met_choice.addItem("Don't fill (Drop NA)")
        met_choice.setGeometry(690,410,200,50)
        self.met.setGeometry(650,370,400,50)
        met_choice.activated[str].connect(self.met_select)
        
        btn_ref_file = QPushButton('CONTINUE', self)
        btn_ref_file.resize(500, 80)
        btn_ref_file.move(300, 500)
        btn_ref_file.clicked.connect(self.nextScreen)
        #self.show()

        btn_back = QPushButton('Back', self)
        btn_back.resize(80, 50)
        btn_back.move(50, 20)
        btn_back.clicked.connect(self.backScreen)


    def backScreen(self):

        screens.setCurrentIndex(screens.currentIndex()-1)


    def nextScreen(self):

        s4 = Screen4()
        screens.addWidget(s4)
        screens.setCurrentIndex(screens.currentIndex()+1)

    def temp_select(self,text):
        global TEMP_NA
        TEMP_NA = temp_na_dict[text]

    def pm_select(self,text):
        global PM_NA
        PM_NA = pm_na_dict[text]

    def pollutants_select(self,text):
        global POLL_NA
        POLL_NA = poll_na_dict[text]  

    def met_select(self,text):
        global MET_NA
        MET_NA = met_na_dict[text]       


## Feature Engineering: What all features are needed in Dataframe
class Screen4(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        print('In Screen 4')
        processMsg = QLabel('<h1>Selection 3: Feature Engineering</h1>', self)
        processMsg.setGeometry(350,50,450,100)

        ## CHECKBOXES
## 1st column

        checkBox_pm_10_yest = QCheckBox(self)
        checkBox_pm_10_yest.setText('Average PM10 yesterday')
        checkBox_pm_10_yest.setGeometry(120, 180, 200, 20)
        checkBox_pm_10_yest.stateChanged.connect(self.checked_pm_10_yest)

        checkBox_pm_10_week = QCheckBox(self)
        checkBox_pm_10_week.setText('Average PM10 this week')
        checkBox_pm_10_week.setGeometry(120, 230, 200, 20)
        checkBox_pm_10_week.stateChanged.connect(self.checked_pm_10_week)

        checkBox_pm_10_month = QCheckBox(self)
        checkBox_pm_10_month.setText('Average PM10 this month')
        checkBox_pm_10_month.setGeometry(120, 280, 200, 20)
        checkBox_pm_10_month.stateChanged.connect(self.checked_pm_10_month)

        checkBox_pm_2_yest = QCheckBox(self)
        checkBox_pm_2_yest.setText('Average PM2.5 yesterday')
        checkBox_pm_2_yest.setGeometry(120, 330, 200, 20)
        checkBox_pm_2_yest.stateChanged.connect(self.checked_pm_2_yest)

        checkBox_pm_2_week = QCheckBox(self)
        checkBox_pm_2_week.setText('Average PM2.5 this week')
        checkBox_pm_2_week.setGeometry(120, 380, 200, 20)
        checkBox_pm_2_week.stateChanged.connect(self.checked_pm_2_week) 

        checkBox_pm_2_month = QCheckBox(self)
        checkBox_pm_2_month.setText('Average PM2.5 this month')
        checkBox_pm_2_month.setGeometry(120, 430, 200, 20)
        checkBox_pm_2_month.stateChanged.connect(self.checked_pm_2_month) 


## 2nd column
        checkBox_pm_10_last_yest = QCheckBox(self)
        checkBox_pm_10_last_yest.setText('Average PM10 last year this day')
        checkBox_pm_10_last_yest.setGeometry(420, 180, 300, 20)
        checkBox_pm_10_last_yest.stateChanged.connect(self.checked_pm_10_last_yest)

        checkBox_pm_10_last_week = QCheckBox(self)
        checkBox_pm_10_last_week.setText('Average PM10 last year this week')
        checkBox_pm_10_last_week.setGeometry(420, 230, 300, 20)
        checkBox_pm_10_last_week.stateChanged.connect(self.checked_pm_10_last_week)

        checkBox_pm_10_last_month = QCheckBox(self)
        checkBox_pm_10_last_month.setText('Average PM10 last year this month')
        checkBox_pm_10_last_month.setGeometry(420, 280, 300, 20)
        checkBox_pm_10_last_month.stateChanged.connect(self.checked_pm_10_last_month)

        checkBox_pm_2_last_yest = QCheckBox(self)
        checkBox_pm_2_last_yest.setText('Average PM2.5 last year this day')
        checkBox_pm_2_last_yest.setGeometry(420, 330, 300, 20)
        checkBox_pm_2_last_yest.stateChanged.connect(self.checked_pm_2_last_yest)

        checkBox_pm_2_last_week = QCheckBox(self)
        checkBox_pm_2_last_week.setText('Average PM2.5 last year this week')
        checkBox_pm_2_last_week.setGeometry(420, 380, 300, 20)
        checkBox_pm_2_last_week.stateChanged.connect(self.checked_pm_2_last_week) 

        checkBox_pm_2_last_month = QCheckBox(self)
        checkBox_pm_2_last_month.setText('Average PM2.5 last year this month')
        checkBox_pm_2_last_month.setGeometry(420, 430, 300, 20)
        checkBox_pm_2_last_month.stateChanged.connect(self.checked_pm_2_last_month) 


## 3rd column


        checkBox_poll = QCheckBox(self)
        checkBox_poll.setText('Include Pollutants')
        checkBox_poll.setGeometry(720, 180, 200, 20)
        checkBox_poll.stateChanged.connect(self.checked_poll)

        checkBox_met = QCheckBox(self)
        checkBox_met.setText('Include Meteriological Factors')
        checkBox_met.setGeometry(720, 265, 250, 20)
        checkBox_met.stateChanged.connect(self.checked_met)

        checkBox_seasons = QCheckBox(self)
        checkBox_seasons.setText('Seasons(Winter/Summer/etc)')
        checkBox_seasons.setGeometry(720, 350, 250, 20)
        checkBox_seasons.stateChanged.connect(self.checked_seasons) 

        checkBox_weekend = QCheckBox(self)
        checkBox_weekend.setText('Weekends(Weekend/Weekday)')
        checkBox_weekend.setGeometry(720, 430, 250, 20)
        checkBox_weekend.stateChanged.connect(self.checked_weekend) 


        btn_next_screen = QPushButton('Continue', self)
        btn_next_screen.resize(500, 80)
        btn_next_screen.move(300, 500)
        btn_next_screen.clicked.connect(self.nextScreen)


        btn_back = QPushButton('Back', self)
        btn_back.resize(80, 50)
        btn_back.move(50, 20)
        btn_back.clicked.connect(self.backScreen)

    def backScreen(self):

        screens.setCurrentIndex(screens.currentIndex()-1)

# 1st column's functions
    def checked_pm_10_yest(self, checked):
        global features_dict
        if checked:
            features_dict['PM10_yest']= 1
    def checked_pm_10_week(self, checked):
        global features_dict
        if checked:
            features_dict['PM10_week']= 1

    def checked_pm_10_month(self, checked):
        global features_dict
        if checked:
            features_dict['PM10_month']= 1

    def checked_pm_2_yest(self, checked):
        global features_dict
        if checked:
            features_dict['PM2_yest']= 1
    def checked_pm_2_week(self, checked):
        global features_dict
        if checked:
            features_dict['PM2_week']= 1

    def checked_pm_2_month(self, checked):
        global features_dict
        if checked:
            features_dict['PM2_month']= 1

# 2nd column's functions:
    def checked_pm_10_last_yest(self, checked):
        global features_dict
        if checked:
            features_dict['PM10_last_yest']= 1
    def checked_pm_10_last_week(self, checked):
        global features_dict
        if checked:
            features_dict['PM10_last_week']= 1

    def checked_pm_10_last_month(self, checked):
        global features_dict
        if checked:
            features_dict['PM10_last_month']= 1

    def checked_pm_2_last_yest(self, checked):
        global features_dict
        if checked:
            features_dict['PM2_last_yest']= 1
    def checked_pm_2_last_week(self, checked):
        global features_dict
        if checked:
            features_dict['PM2_last_week']= 1

    def checked_pm_2_last_month(self, checked):
        global features_dict
        if checked:
            features_dict['PM2_last_month']= 1

# 3rd column's function
    def checked_poll(self, checked):
        global features_dict
        if checked:
            features_dict['all_pollutants']= 1

    def checked_met(self, checked):
        global features_dict
        if checked:
            features_dict['all_met']= 1
    def checked_seasons(self, checked):
        global features_dict
        if checked:
            features_dict['seasons']= 1

    def checked_weekend(self, checked):
        global features_dict
        if checked:
            features_dict['weekends']= 1

    def nextScreen(self):

        s5 = Screen5()
        screens.addWidget(s5)
        screens.setCurrentIndex(screens.currentIndex()+1)


## This screen is again just for displaying status of Filling Missing values
class Screen5(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        print('In Screen 5')
        processMsg = QLabel('<h1>File Processed</h1>', self)
        processMsg.setGeometry(400,50,350,100)

        global df

        df, exists = data_load_proxy.check_file(STATION_ID,INTERVAL,TEMP_NA,PM_NA,POLL_NA,MET_NA,features_dict)

        if exists:
            statsMsg = QLabel('Fetching already available file',self)
            statsMsg.setGeometry(400,70,500,500)            
            btn_next_screen = QPushButton('Continue', self)
            btn_next_screen.resize(500, 80)
            btn_next_screen.move(300, 500)
            btn_next_screen.clicked.connect(self.nextScreen)
        else:
            stats1 = missing_values.fill_values(TEMP_NA,PM_NA,POLL_NA,MET_NA)
            #stats = {'ok':True, 'process':'Done a lot!'}
            statsMsg = QLabel(stats1['process'],self)
            statsMsg.setGeometry(400,70,500,500)

            df, stats2 = features.get_data(STATION_ID, features_dict)
            stats2Msg = QLabel(stats2['process'],self)
            stats2Msg.setGeometry(400,180,500,500)


            if stats1['ok'] == True and stats2['ok']==True:

                btn_next_screen = QPushButton('Continue', self)
                btn_next_screen.resize(500, 80)
                btn_next_screen.move(300, 500)
                btn_next_screen.clicked.connect(self.nextScreen)

            else: 
                errMsg = QLabel('<h3>Some error occured. Please try another configuration</h3>',self)
                errMsg.setGeometry(400,500,500,100)

        btn_back = QPushButton('Back', self)
        btn_back.resize(80, 50)
        btn_back.move(50, 20)
        btn_back.clicked.connect(self.backScreen)

    def backScreen(self):

        screens.setCurrentIndex(screens.currentIndex()-1)



    def nextScreen(self):

        s6 = Screen6()
        screens.addWidget(s6)
        screens.setCurrentIndex(screens.currentIndex()+1)


## Lag values for Pollutants(if chosen for PARAMS) and for TARGET variable
class Screen6(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        print('In Screen 6')
        LagMsg = QLabel('<h1>Selection 4:Choose Lag Value</h1>', self)
        LagMsg.setGeometry(350,50,450,100)

        if features_dict['all_pollutants'] == 1:
            polLagMsg = QLabel('<h3>Lag Value for Pollution Parameters</h3>', self)
            polLagMsg.setGeometry(400,250,300,50)
            e1 = QLineEdit(self)
            e1.setValidator(QIntValidator())
            e1.setMaxLength(2)
            e1.setAlignment(Qt.AlignRight)
            e1.setFont(QFont("Arial",18))
            e1.setGeometry(700,260,50,30)
            e1.textChanged.connect(self.polLag)

        tarLagMsg = QLabel('<h3>Lag Value for Target Parameter</h3>', self)
        tarLagMsg.setGeometry(400,400,300,50)
        e2 = QLineEdit(self)
        e2.setValidator(QIntValidator())
        e2.setMaxLength(2)
        e2.setAlignment(Qt.AlignRight)
        e2.setFont(QFont("Arial",18))
        e2.setGeometry(700,410,50,30)
        e2.textChanged.connect(self.tarLag)

        btn_next_screen = QPushButton('Continue', self)
        btn_next_screen.resize(500, 80)
        btn_next_screen.move(300, 500)
        btn_next_screen.clicked.connect(self.nextScreen)

        btn_back = QPushButton('Back', self)
        btn_back.resize(80, 50)
        btn_back.move(50, 20)
        btn_back.clicked.connect(self.backScreen)

    def backScreen(self):

        screens.setCurrentIndex(screens.currentIndex()-1)



    def polLag(self,text):
        global LAG_POLL
        try:
            LAG_POLL = int(text)
        except:
            LAG_POLL = 0
    
    def tarLag(self,text):
        global LAG_TARGET
        
        try:
            LAG_TARGET = int(text)
        except:
            LAG_TARGET = 0


    def nextScreen(self):
        
        s7 = Screen7()
        screens.addWidget(s7)
        screens.setCurrentIndex(screens.currentIndex()+1)


## Model selection
class Screen7(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        print('In Screen 7')
        LagMsg = QLabel('<h1>Selection 5:Model Training</h1>', self)
        LagMsg.setGeometry(350,50,350,100)

        self.target = QLabel('<h2>Target Variable</h2>', self)
        target_choice = QComboBox(self)
        target_choice.addItem('PM 2.5')
        target_choice.addItem('PM 10')
        target_choice.setGeometry(140,240,200,50)
        self.target.setGeometry(150,200,300,50)
        target_choice.activated[str].connect(self.target_select)


        self.standard = QLabel('<h2>Standardization Method</h2>', self)
        standard_choice = QComboBox(self)
        standard_choice.addItem('No Standardization')
        standard_choice.addItem('Standard Scaling')
        standard_choice.addItem("Min Max Scaling")
        standard_choice.setGeometry(690,240,200,50)
        self.standard.setGeometry(675,200,300,50)
        standard_choice.activated[str].connect(self.standard_select)


        self.split = QLabel('<h2>Test-Train Split</h2>', self)
        split_choice = QComboBox(self)
        split_choice.addItem('20%')
        split_choice.addItem('25%')
        split_choice.addItem("33%")
        split_choice.setGeometry(140,330,200,50)
        self.split.setGeometry(140,300,400,50)
        split_choice.activated[str].connect(self.split_select)


        self.model = QLabel('<h2>ML Model</h2>', self)
        model_choice = QComboBox(self)
        model_choice.addItem('Linear Regression')
        model_choice.addItem('Ridge Regression')
        model_choice.addItem('Lasso Regression')
        model_choice.addItem('Elastic Net Regression')
        model_choice.addItem('SGD Regression')
        model_choice.addItem("Decision Tree")
        model_choice.addItem('Random Forest')
        model_choice.addItem("Ada Boost")
        model_choice.addItem('Bagging')
        model_choice.addItem('Gradient Boost')
        model_choice.addItem('XGBoost')
        model_choice.addItem('Extra Trees')
        model_choice.addItem('SVR')
        model_choice.addItem('HistGradientBoosting')
        model_choice.addItem('LGBMRegressor')
        model_choice.addItem('CatBoostRegressor')
        
        
        
        model_choice.setGeometry(690,330,200,50)
        self.model.setGeometry(720,300,400,50)
        model_choice.activated[str].connect(self.model_select)


        metricMsg = QLabel('<i>Metrics:</i>', self)
        metricMsg.setGeometry(120, 400, 200, 20)
        
        checkBox_metrics_a = QCheckBox(self)
        checkBox_metrics_a.setText('RMSE')
        checkBox_metrics_a.setGeometry(200, 400, 200, 20)
        checkBox_metrics_a.stateChanged.connect(self.metrics_a)
        checkBox_metrics_a.setChecked(True)

        checkBox_metrics_b = QCheckBox(self)
        checkBox_metrics_b.setText('R2 Score')
        checkBox_metrics_b.setGeometry(350, 400, 200, 20)
        checkBox_metrics_b.stateChanged.connect(self.metrics_b)
        checkBox_metrics_b.setChecked(True)

        checkBox_metrics_c = QCheckBox(self)
        checkBox_metrics_c.setText('MAE')
        checkBox_metrics_c.setGeometry(500, 400, 200, 20)
        checkBox_metrics_c.stateChanged.connect(self.metrics_c)
        checkBox_metrics_c.setChecked(True)

        checkBox_metrics_d = QCheckBox(self)
        checkBox_metrics_d.setText('MAPE')
        checkBox_metrics_d.setGeometry(650, 400, 200, 20)
        checkBox_metrics_d.stateChanged.connect(self.metrics_d)
        checkBox_metrics_d.setChecked(True)

        
        btn_ref_file = QPushButton('START PROCESS', self)
        btn_ref_file.resize(500, 80)
        btn_ref_file.move(300, 500)
        btn_ref_file.clicked.connect(self.nextScreen)
        #self.show()

        btn_back = QPushButton('Back', self)
        btn_back.resize(80, 50)
        btn_back.move(50, 20)
        btn_back.clicked.connect(self.backScreen)

    def backScreen(self):
        screens.setCurrentIndex(screens.currentIndex()-1)



    def nextScreen(self):
        s8 = Screen8()
        screens.addWidget(s8)
        screens.setCurrentIndex(screens.currentIndex()+1)

    def target_select(self,text):
        global TARGET
        TARGET = target_dict[text]

    def standard_select(self,text):
        global STANDARDIZATION
        STANDARDIZATION = standard_dict[text]

    def split_select(self,text):
        global SPLIT_PERC
        SPLIT_PERC = int(text.strip('%'))

    def model_select(self,text):
        global MODEL
        MODEL = model_dict[text]


    def metrics_a(self, checked):
        global metrics_dict
        if not checked:
            metrics_dict['RMSE']= 0
    
    def metrics_b(self, checked):
        global metrics_dict
        if not checked:
            metrics_dict['R2 Score']= 0
    
    def metrics_c(self, checked):
        global metrics_dict
        if not checked:
            metrics_dict['MAE']= 0
    
    def metrics_d(self, checked):
        global metrics_dict
        if not checked:
            metrics_dict['MAPE']= 0

## Displaying Output
class Screen8(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        print('In Screen 8')
        OutMsg = QLabel('<h1>Working on the data...</h1>', self)
        OutMsg.setGeometry(350,50,450,100)
        global result

        ## Until here we have called data_load 
        ## and missing_values

        ## Now we start from features

        try:
            features.final_features(df,features_dict,LAG_POLL,TARGET,LAG_TARGET)
            stats = model.get_data(SPLIT_PERC,STANDARDIZATION,MODEL)
            result = stats['result']
        except Exception as e:
            print(e)
            stats = {'ok':False, 'result':'Error!'}


        ## Features will give X,Y. We create train & test data from it
        #model.get_data(SPLIT_PERC,STANDARDIZATION,MODEL)

        ## Once we have model and X_test & Y_test, we can test it
        #stats = metrics.test(metrics_dict)
        
        
        ## Display the ouput
        resultsMsg = QLabel(stats['result'],self)
        resultsMsg.setGeometry(220,100,900,700)

        if stats['ok']==True:
            btn_ref_file = QPushButton('LOG RESULTS', self)
            btn_ref_file.resize(500, 40)
            btn_ref_file.move(300, 550)
            btn_ref_file.clicked.connect(self.log_results)

        btn1_ref_file = QPushButton('QUIT', self)
        btn1_ref_file.resize(500, 40)
        btn1_ref_file.move(300, 600)
        btn1_ref_file.clicked.connect(QtWidgets.qApp.quit)
        
    def log_results(self):
        field_names = ['STATION_ID','INTERVAL','MISSING TEMPERATURE FILLED USING',
               'MISSING PM FILLED USING','MISSING POLLUTANTS FILLED USING','MISSING MET PARAMS FILLED USING',
               'EXTRA FEATURES ADDED','LAG FOR POLLUTANTS','LAG FOR TARGET','TARGET','STANDARDIZATION','SPLIT_PERC','MODEL',
               'MSE','MAE','RMSE','MAPE','R2']

        li = []
        for key, val in features_dict.items():
                 if val == 1:
                     li.append(key)

        res = re.findall(r'[0-9]*[.,][0-9]*',result)
  
        # Dictionary
        dict_items={'STATION_ID':STATION_ID,'INTERVAL':INTERVAL,'MISSING TEMPERATURE FILLED USING': list(temp_na_dict.keys())[list(temp_na_dict.values()).index(TEMP_NA)],
               'MISSING PM FILLED USING': list(pm_na_dict.keys())[list(pm_na_dict.values()).index(PM_NA)],'MISSING POLLUTANTS FILLED USING':list(poll_na_dict.keys())[list(poll_na_dict.values()).index(POLL_NA)],
               'MISSING MET PARAMS FILLED USING': list(met_na_dict.keys())[list(met_na_dict.values()).index(MET_NA)],
               'EXTRA FEATURES ADDED':li,'LAG FOR POLLUTANTS':LAG_POLL,'LAG FOR TARGET':LAG_TARGET,'TARGET':list(target_dict.keys())[list(target_dict.values()).index(TARGET)],
               'STANDARDIZATION':list(standard_dict.keys())[list(standard_dict.values()).index(STANDARDIZATION)],'SPLIT_PERC':SPLIT_PERC,'MODEL':list(model_dict.keys())[list(model_dict.values()).index(MODEL)],
               'MSE':res[0],'MAE':res[1],'RMSE':res[2],'MAPE':res[3],'R2':res[4]}

        with open('results.csv', 'a') as f_object:
              
            # Pass the file object and a list 
            # of column names to DictWriter()
            # You will get a object of DictWriter
            dictwriter_object = DictWriter(f_object, fieldnames=field_names)
          
            #Pass the dictionary as an argument to the Writerow()
            dictwriter_object.writerow(dict_items)
          
            #Close the file object
            f_object.close()

            QtWidgets.qApp.quit()

    # def quit(self):

    #     self.close()

## Run function for running the app
## This initialized the 1st screen. 
## There onwards, every screen is initialized by a screen before it
def run():
    app = QApplication(sys.argv)

    global screens
    screens = QtWidgets.QStackedWidget()
    s1 = Screen1()
    screens.addWidget(s1)

    screens.setGeometry(50, 50, 1080, 800)

    screens.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    run()
