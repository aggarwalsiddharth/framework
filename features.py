## Features is 3rd in heirarchy

## Missing_Values -> Features -> Model

from time import sleep
import pandas as pd
import numpy as np

import missing_values # for getting the df

# global X & Y for updating in function & sending it to model.py
X = []
Y = []

## global daily mean for calculating features
daily_means = []

## GUI calls this function and gives values of arguments
def get_data(features_dict,LAG_POLL,TARGET,LAG_TARGET):
	
	global X,Y
	
	df = missing_values.get_df()

	df['From Date'] = pd.to_datetime(df['From Date'])
	daily_means = df.groupby([pd.Grouper(key='From Date', freq='D')]).mean()

	df = add_features(df, features_dict)

	if features_dict["all_pollutants"]==1:
		df = add_lag(df, LAG_POLL)

	X,Y = create_XY(df, TARGET,LAG_TARGET)

	return

features_dict = {'PM10_yest':0,'PM10_week':0,'PM10_month':0,'PM2_yest':0,'PM2_week':0,'PM2_month':0, 'PM10_last_yest':0,'PM10_last_week':0,'PM10_last_month':0,'PM2_last_yest':0,'PM2_last_week':0,'PM2_last_month':0,'seasons':0,'weekends':0,'all_pollutants':0,'all_met':0}

def add_features(df, features_dict):

	if features_dict['PM10_yest'] == 1:
		df = add_features_yesterday(df,10)

	if features_dict['PM10_week'] == 1:
		df = add_features_week(df,10)

	if features_dict['PM10_month'] == 1:
		df = add_features_month(df,10)

	if features_dict['PM2_yest'] == 1:
		df = add_features_yesterday(df,2)

	if features_dict['PM2_week'] == 1:
		df = add_features_week(df,2)

	if features_dict['PM2_month'] == 1:
		df = add_features_month(df,2)

	if features_dict['PM10_last_yest'] == 1:
		df = add_features_last_yesterday(df,10)

	if features_dict['PM10_last_week'] == 1:
		df = add_features_last_week(df,10)

	if features_dict['PM10_last_month'] == 1:
		df = add_features_last_month(df,10)

	if features_dict['PM2_last_yest'] == 1:
		df = add_features_last_yesterday(df,2)

	if features_dict['PM2_last_week'] == 1:
		df = add_features_last_week(df,2)

	if features_dict['PM2_last_month'] == 1:
		df = add_features_last_month(df,2)

	if features_dict['seasons'] == 1:
		df = add_features_seasons(df)

	if features_dict['weekends'] == 1:
		df = add_features_weekend(df)

	if features_dict['all_pollutants'] == 1:
		df = add_features_pollutants(df)

	if features_dict['all_met'] == 1:
		df = add_features_met(df)


## PM 10/2.5 Yesterday
def add_features_yesterday(df,pm_value):
	
	if pm_value == 10:
		pm_value = 'PM10 (ug/m3)'
	
	else:
		pm_value = 'PM2.5 (ug/m3)'

	pmlist_yest = []
	old_dy = ''

	#df['From Date'] = pd.to_datetime(df['From Date'])

	for idx,row in df.iterrows():
	    
	    tm_stmp = row['From Date']
	    adj_tm_stmp = tm_stmp - pd.Timedelta(days=1)
	    
	    mth = adj_tm_stmp.month
	    dy = adj_tm_stmp.day
	    yr = adj_tm_stmp.year
	    
	    if dy == old_dy:
	        pmlist_yest.append(val)
	        
	    else:

	        try:
	            val = daily_means[(daily_means.index.month==mth) & (daily_means.index.day==dy) & (daily_means.index.year==yr)][pm_value]
	            pmlist_yest.append(val)
	            old_dy = dy

	        except:
	            val = np.nan
	            pmlist_yest.append(val)
	            old_dy = dy

    
    df[f'{pm_value} + Yesterday'] = pmlist_yest

	return df

## PM 10/2.5 Last week
def add_features_week(df,pm_value):

	return df

## PM 10/2.5 Last month
def add_features_month(df,pm_value):

	return df

## PM 10/2.5 Last Year Yesterday
def add_features_last_yesterday(df,pm_value):

	return df

## PM 10/2.5 Last Year Week
def add_features_last_week(df,pm_value):

	return df

## PM 10/2.5 Last Year Month
def add_features_last_month(df,pm_value):

	return df

def add_features_seasons(df):

	return df

def add_features_weekend(df):

	return df

def add_features_pollutants(df):

	return df

def add_features_met(df):

	return df




## sending X and Y to model.py
def get_XY():
	return X,Y


