# Hourly Wunderground Forecast data

!pip install selenium
!apt-get update
!apt install chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('chromedriver',options=chrome_options)


import pandas as pd
import re
from datetime import datetime
from datetime import timedelta
import time


def get_wunderground_forecast(objFromDate, objEndDate):
  df = pd.DataFrame()
  while (objFromDate < objEndDate):
    df = pd.concat([df, fetchdata(objFromDate)], axis=0)
    #print(objFromDate.strftime('%Y-%m-%d'))
    objNextDate = objFromDate +timedelta(days=1)
    objFromDate = objNextDate
  
  df = preprocess_wunderground_forecast(df)
  return df


def fetchdata(objFromDate):
  driver.get('https://www.wunderground.com/hourly/in/new-delhi/VIDP/date/'+objFromDate.strftime('%Y-%m-%d'))

  driver.implicitly_wait(10)
  df=pd.read_html(driver.find_element_by_xpath('/html/body/app-root/app-hourly/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div/section/div[3]/div[1]/div/div[1]/div/lib-city-hourly-forecast/div/div[4]/div[1]/table').get_attribute('outerHTML'))[0]

  df['Date'] = objFromDate.strftime('%Y-%m-%d')
  df.dropna(inplace=True)

  return df


def preprocess_wunderground_forecast(df):

  # Rename Condition, 'Temperature
  df.columns = ['Time', 'Condition', 'Temperature', 'Feels Like', 'Precip', 'Rainfall', 'Cloud Cover', 'Dew Point', 'Humidity', 'Wind', 'Pressure', 'Date']
  #df_cols = ['From Date','Dew Point', 'Humidity', 'Wind', 'Wind Speed', 'Wind Gust', 'Pressure', 'Condition', 'Temperature in C']

  # Set DateTime
  df['From Date'] = df['Date'] + ' ' + df['Time']
  df['From Date'] = pd.to_datetime(df['From Date'])
  del df['Time'], df['Date']
  df = df.sort_values(by='From Date')

  #Remove duplicate dates and NA
  df = df.drop_duplicates(subset = ['From Date'],  keep = 'last').reset_index(drop = True)
  df = df.dropna()

  # Set Temp F to C
  df["Temperature"] = df["Temperature"].str.replace("\s+F", "")
  df["Temperature"] = df["Temperature"].astype('int64')
  df['Temperature in C'] = df['Temperature'].apply(lambda x: round((x-32) * 5/9 , 2))
  del df['Temperature']
  df['Temperature in C'].head()

  # Separate Wind Speed & Wind direction
  new = df["Wind"].str.split(" ", expand = True)
  # making separate first name column from new data frame
  df["Wind Speed"]= new[0]
  # making separate last name column from new data frame
  df["Wind Direction"] = new[1]
  # Dropping old Name columns
  df.drop(columns =["Wind"], inplace = True)
  #df.rename(columns={'Wind Direction': 'Wind'}, inplace=True)

  # Extract only integers
  df['Dew Point'] = df['Dew Point'].apply(lambda x: [int(s) for s in x.split() if s.isdigit()][0] )
  df['Humidity'] = df['Humidity'].apply(lambda x: [int(s) for s in x.split() if s.isdigit()][0] )
  df['Wind Speed'] = df['Wind Speed'].apply(lambda x: [int(s) for s in x.split() if s.isdigit()][0] )
  #df['Wind Gust'] = df['Wind Gust'].apply(lambda x: [int(s) for s in x.split() if s.isdigit()][0] )
  #df['Pressure'] = df['Pressure'].apply(lambda x: float(re.findall(r'[0-9]*[.,][0-9]*', x)[0]))
  #df['Pressure'] = df['Pressure'].apply(lambda x: round(x * 33.86389 , 2)) # 1 inhg to hpa = 33.86389 hpa
  #df['Rainfall'] = df['Rainfall'].apply(lambda x: [int(s) for s in x.split() if s.isdigit()][0] )
  #df['Rainfall'] = df['Rainfall'].apply(lambda x: float(re.findall(r'[0-9]*[.,][0-9]*', x)[0]))
  df['Pressure'] = df['Pressure'].apply(lambda x: [float(s) for s in x.split() if s.replace('.', '', 1).isdigit()][0] )
  df['Rainfall'] = df['Rainfall'].apply(lambda x: [float(s) for s in x.split() if s.replace('.', '', 1).isdigit()][0] )

  df.loc[df["Wind Speed"]==0, 'Wind Direction'] = 'CALM'
  df["Wind Direction"] = df["Wind Direction"].astype('category')
  df["Condition"] = df["Condition"].astype('category')

  # Keep specific columns
  sel_cols = ['From Date', 'Temperature in C', 'Humidity', 'Wind Direction', 'Wind Speed', 'Pressure', 'Dew Point', 'Rainfall', 'Condition']
  df = df[sel_cols]

  return df




fromDate = datetime.today().strftime('%Y-%m-%d')
how_many_days = 10



objFromDate = datetime.strptime(fromDate, "%Y-%m-%d" )
objEndDate = objFromDate + timedelta(days=how_many_days)
df_forecast = pd.DataFrame()
df_forecast = get_wunderground_forecast(objFromDate, objEndDate)
df_forecast.head()
