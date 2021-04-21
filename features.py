## Features is 3rd in heirarchy

## Missing_Values -> Features -> Model

from time import sleep
import pandas as pd
import numpy as np
import os
import missing_values # for getting the df
import data_load_proxy # for getting station and interval for file saving

# global X & Y for updating in function & sending it to model.py
X = []
Y = []

## global daily mean for calculating features
daily_means = []
df_2015 = []

## GUI calls this function and gives values of arguments
def get_data(STATION_ID, features_dict):
	
	global X,Y
	global daily_means
	global df_2015 
	
	df = missing_values.get_df()

	df['From Date'] = pd.to_datetime(df['From Date'])
	daily_means = df.groupby([pd.Grouper(key='From Date', freq='D')]).mean()

	## edit this later based on STATION_ID
	for file in os.listdir('data/'):
		if '2015' in file and str(STATION_ID) in file:
			file_2015 = file

	df_2015 = pd.read_csv('data/' + file_2015)
	df_2015 = df_2015[15:]
	df_2015.columns = list(df_2015.iloc[0])
	df_2015 = df_2015.reset_index(drop=True)
	df_2015 = df_2015[1:]
	df_2015 = df_2015[:366]
	df_2015['From Date'] = pd.to_datetime(df_2015['From Date'])

	df = add_features(df, features_dict)

	save_file(df,features_dict)

	#final_features(df,features_dict,LAG_POLL,TARGET,LAG_TARGET)

	
	stats = {'ok':True, 'process':'Alot!'}
	return df,stats


def add_features(df, features_dict):

	if features_dict['PM10_yest'] == 1:
		try:
			df = add_features_yesterday(df,10)
		except Exception as e:
			print('In error 1_10')
			print(e)

	if features_dict['PM10_week'] == 1:
		try:
			df = add_features_week(df,10)
		except Exception as e:
			print('In error 2_10')
			print(e)

	if features_dict['PM10_month'] == 1:
		try:
			df = add_features_month(df,10)
		except Exception as e:
			print('In error 3_10')
			print(e)

	if features_dict['PM2_yest'] == 1:
		try:
			df = add_features_yesterday(df,2)
		except Exception as e:
			print('In error 1_2')
			print(e)

	if features_dict['PM2_week'] == 1:
		try:
			df = add_features_week(df,2)
		except Exception as e:
			print('In error 2_2')
			print(e)

	if features_dict['PM2_month'] == 1:
		try:
			df = add_features_month(df,2)
		except Exception as e:
			print('In error 3_2')
			print(e)		

	if features_dict['PM10_last_yest'] == 1:
		try:
			df = add_features_last_yesterday(df,10)
		except Exception as e:
			print('In error 4_10')
			print(e)

	if features_dict['PM10_last_week'] == 1:
		try:
			df = add_features_last_week(df,10)
		except Exception as e:
			print('In error 5_10')
			print(e)

	if features_dict['PM10_last_month'] == 1:
		try:
			df = add_features_last_month(df,10)
		except Exception as e:
			print('In error 6_10')
			print(e)

	if features_dict['PM2_last_yest'] == 1:
		try:
			df = add_features_last_yesterday(df,2)
		except Exception as e:
			print('In error 4_2')
			print(e)

	if features_dict['PM2_last_week'] == 1:
		try:
			df = add_features_last_week(df,2)
		except Exception as e:
			print('In error 5_2')
			print(e)

	if features_dict['PM2_last_month'] == 1:
		try:
			df = add_features_last_month(df,2)
		except Exception as e:
			print('In error 6_2')
			print(e)

	if features_dict['seasons'] == 1:
		try:
			df = add_features_seasons(df)
		except Exception as e:
			print(e)

	if features_dict['weekends'] == 1:
		try:
			df = add_features_weekend(df)
		except Exception as e:
			print(e)

	if features_dict['all_pollutants'] == 0:
		try:
			df = add_features_pollutants(df)
		except Exception as e:
			print(e)

	if features_dict['all_met'] == 0:
		try:
			df = add_features_met(df)
		except Exception as e:
			print(e)

	return df



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
	            val = daily_means[(daily_means.index.month==mth) & (daily_means.index.day==dy) & (daily_means.index.year==yr)][pm_value].values[0]
	            pmlist_yest.append(val)
	            old_dy = dy

	        except:
	            val = np.nan
	            pmlist_yest.append(val)
	            old_dy = dy

    
	df[f'{pm_value} + Yesterday'] = pmlist_yest

	# print(len(pmlist_yest) == len(df))
	return df

## PM 10/2.5 Last week
def add_features_week(df,pm_value):

	if pm_value == 10:
		pm_value = 'PM10 (ug/m3)'
	
	else:
		pm_value = 'PM2.5 (ug/m3)'	

	pmlist_week = []
	old_dy = ''

	#df['From Date'] = pd.to_datetime(df['From Date'])

	for idx,row in df.iterrows():
	    
	    tm_stmp = row['From Date']
	    day_today = tm_stmp.day
	    
	    if day_today == old_dy:
	        pmlist_week.append(val)
	        
	    else:
	        pm_list = []

	        for i in range(1,8):
	            adj_tm_stmp = tm_stmp - pd.Timedelta(days=i)

	            mth = adj_tm_stmp.month
	            dy = adj_tm_stmp.day
	            yr = adj_tm_stmp.year


	            val = daily_means[(daily_means.index.month==mth) & (daily_means.index.day==dy) & (daily_means.index.year==yr)]['PM2.5 (ug/m3)'].values
	            # print(val)
	            if not len(val)==0 and not np.isnan(val[0]):
	                pm_list.append(val[0])
	                    #print(x)
	            else:
	                    #print(e)
	                pm_list.append(np.nan)


	        val = np.nanmean(pm_list)
	        pmlist_week.append(val)
	        old_dy = day_today


	df[f'{pm_value} + Week'] = pmlist_week

	# print(len(pmlist_week) == len(df))
	return df

## PM 10/2.5 Last month
def add_features_month(df,pm_value):

	if pm_value == 10:
		pm_value = 'PM10 (ug/m3)'
	
	else:
		pm_value = 'PM2.5 (ug/m3)'


	pmlist_month = []
	old_dy = ''

	#df['From Date'] = pd.to_datetime(df['From Date'])

	for idx,row in df.iterrows():
	    
	    tm_stmp = row['From Date']
	    day_today = tm_stmp.day
	    
	    if day_today == old_dy:
	        pmlist_month.append(val)
	        
	    else:
	        pm_list = []

	        for i in range(1,31):
	            adj_tm_stmp = tm_stmp - pd.Timedelta(days=i)

	            mth = adj_tm_stmp.month
	            dy = adj_tm_stmp.day
	            yr = adj_tm_stmp.year


	            val = daily_means[(daily_means.index.month==mth) & (daily_means.index.day==dy) & (daily_means.index.year==yr)]['PM2.5 (ug/m3)'].values
	            # print(val)
	            if not len(val)==0 and not np.isnan(val[0]):
	                pm_list.append(val[0])
	                    #print(x)
	            else:
	                    #print(e)
	                pm_list.append(np.nan)


	        val = np.nanmean(pm_list)
	        pmlist_month.append(val)
	        old_dy = day_today

	df[f'{pm_value} + Month'] = pmlist_month
	# print(len(pmlist_month) == len(df))
	return df

## PM 10/2.5 Last Year Yesterday
def add_features_last_yesterday(df,pm_value):

	if pm_value == 10:
		pm_value = 'PM10 (ug/m3)'
		pm_value_2015 = 'PM10'
	
	else:
		pm_value = 'PM2.5 (ug/m3)'
		pm_value_2015 = 'PM2.5'

	global df_2015


	pmlist_lytd = []
	old_dy = ''

	for i in df['From Date']:
	    yr = i.year - 1
	    mth = i.month
	    dy = i.day
	    
	    if dy == old_dy:
	        pmlist_lytd.append(val)
	        
	    else:

	        try:
	            if yr==2015:
	                val = df_2015[(df_2015['From Date'].dt.month == mth ) & (df_2015['From Date'].dt.day == dy)][pm_value_2015].values[0]
	                pmlist_lytd.append(val)

	                old_dy = dy

	            else:   
	                val = daily_means[(daily_means.index.month==mth) & (daily_means.index.day==dy) & (daily_means.index.year==yr)][pm_value].values[0]
	                pmlist_lytd.append()

	                old_dy = dy

	        except Exception as e:
	            val = None
	            pmlist_lytd.append(val)
	            old_dy = dy


	df[f'{pm_value} + Yesterday Last Year'] = pmlist_lytd
	# print(len(pmlist_lytd)==len(df))
	return df

## PM 10/2.5 Last Year Week
def add_features_last_week(df,pm_value):
	if pm_value == 10:
		pm_value = 'PM10 (ug/m3)'
		pm_value_2015 = 'PM10'
	
	else:
		pm_value = 'PM2.5 (ug/m3)'
		pm_value_2015 = 'PM2.5'

	old_dy = ''

	pmlist_lytw = []

	for i in df['From Date']:
	    yr = i.year - 1
	    mth = i.month
	    dy = i.day
	    
	    if dy == old_dy:
	        pmlist_lytw.append(val_pm)
	        continue
	    
	    if yr == 2015:
	        
	        #print(df_2015[(df_2015['From Date'].dt.month == mth ) & (df_2015['From Date'].dt.day == dy)])
	        try:
	            idx = df_2015[(df_2015['From Date'].dt.month == mth ) & (df_2015['From Date'].dt.day == dy)].index[0]
	            old_dy = dy
	        except:
	            pmlist_lytw.append(None)
	            
	            val_pm=None
	            
	            continue
	        
	        rolling_avg_pm = 0    
	        cnt_pm = 0
	        

	        for x in range(idx-3,idx+4):
	            try:

	                if df_2015.iloc[x][pm_value_2015]!='None':

	                    rolling_avg_pm += float(df_2015.iloc[x][pm_value_2015])
	                    cnt_pm += 1
	                    
	            except:
	                l = len(df_2015)
	                df.iloc[x-l]
	                if df.iloc[x-l][pm_value]!='None':

	                    rolling_avg_pm += float(df.iloc[x-l][pm_value])
	                    cnt_pm += 1
	                
	        try:
	            val_pm = rolling_avg_pm/cnt_pm
	            pmlist_lytw.append(val_pm)
	        except:
	            val_pm = None
	            pmlist_lytw.append(val_pm)
	        
	    else:
	        try:
	    
	            idx = df[(df['From Date'].dt.month == mth ) & (df['From Date'].dt.day == dy) & (df['From Date'].dt.year == yr)].index[0]
	            old_dy = dy

	        except:
	            pmlist_lytw.append(None)
	            val_pm=None
	            continue
	            
	        
	        rolling_avg_pm = 0    
	        cnt_pm = 0
	        


	        for x in range(idx-3,idx+4):

	            try:
	                if df.iloc[x][pm_value]!='None':

	                    rolling_avg_pm += float(df.iloc[x][pm_value])
	                    cnt_pm += 1


	            except:
	                continue
	            
	            
	        try:
	            val_pm = rolling_avg_pm/cnt_pm
	            pmlist_lytw.append(val_pm)
	        except:
	            val_pm = None
	            pmlist_lytw.append(val_pm)


	df[f'{pm_value} + Week Last Year'] = pmlist_lytw
	# print(len(pmlist_lytw)==len(df))

	return df

## PM 10/2.5 Last Year Month
def add_features_last_month(df,pm_value):
	if pm_value == 10:
		pm_value = 'PM10 (ug/m3)'
		pm_value_2015 = 'PM10'
	
	else:
		pm_value = 'PM2.5 (ug/m3)'
		pm_value_2015 = 'PM2.5'

	old_dy = ''

	pmlist_lytm = []

	for i in df['From Date']:
	    yr = i.year - 1
	    mth = i.month
	    dy = i.day
	    
	    if dy == old_dy:
	        pmlist_lytm.append(val_pm)
	        continue
	    
	    if yr == 2015:
	        
	        #print(df_2015[(df_2015['From Date'].dt.month == mth ) & (df_2015['From Date'].dt.day == dy)])
	        try:
	            idx = df_2015[(df_2015['From Date'].dt.month == mth ) & (df_2015['From Date'].dt.day == dy)].index[0]
	            old_dy = dy
	        except:
	            pmlist_lytm.append(None)
	            
	            val_pm=None
	            
	            continue
	        
	        rolling_avg_pm = 0    
	        cnt_pm = 0
	        

	        for x in range(idx-15,idx+16):
	            try:

	                if df_2015.iloc[x][pm_value_2015]!='None':

	                    rolling_avg_pm += float(df_2015.iloc[x][pm_value_2015])
	                    cnt_pm += 1

	                    
	            except:
	                l = len(df_2015)
	                df.iloc[x-l]
	                if df.iloc[x-l][pm_value]!='None':

	                    rolling_avg_pm += float(df.iloc[x-l][pm_value])
	                    cnt_pm += 1


	                
	        try:
	            val_pm = rolling_avg_pm/cnt_pm
	            pmlist_lytm.append(val_pm)
	        except:
	            val_pm = None
	            pmlist_lytm.append(val_pm)
	            
	            
	        
	    else:
	        try:
	    
	            idx = df[(df['From Date'].dt.month == mth ) & (df['From Date'].dt.day == dy) & (df['From Date'].dt.year == yr)].index[0]
	            old_dy = dy

	        except:
	            pmlist_lytm.append(None)
	            val_pm=None
	            continue
	            
	        
	        rolling_avg_pm = 0    
	        cnt_pm = 0
	        


	        for x in range(idx-15,idx+16):

	            try:
	                if df.iloc[x][pm_value]!='None':

	                    rolling_avg_pm += float(df.iloc[x][pm_value])
	                    cnt_pm += 1


	            except:
	                continue
	            
	            
	        try:
	            val_pm = rolling_avg_pm/cnt_pm
	            pmlist_lytm.append(val_pm)
	        except:
	            val_pm = None
	            pmlist_lytm.append(val_pm)


	df[f'{pm_value} + Month Last Year'] = pmlist_lytm

	# print(len(pmlist_lytm)==len(df))
	return df

def add_features_seasons(df):
	pass

	return df

def add_features_weekend(df):
	pass

	return df

def add_features_pollutants(df):
	POLLUTANT_PARAMS = ['NO (ug/m3)', 'NO2 (ug/m3)', 'NOx (ppb)', 'NH3 (ug/m3)', 'SO2 (ug/m3)','CO (mg/m3)', 'Ozone (ug/m3)', 'Benzene (ug/m3)', 'Toluene (ug/m3)','Eth-Benzene (ug/m3)', 'O Xylene (ug/m3)', 'CH4 (ug/m3)', 'NMHC (ug/m3)', 'SPM (ug/m3)']

	df_cols = df.columns

	pol_cols = list(df_cols.intersection(POLLUTANT_PARAMS))

	for col in pol_cols:
		del df[col]


	return df

def add_features_met(df):
	pass

	return df




## sending X and Y to model.py
def get_XY():
	return X,Y

## save file with all dets so that it can be re-fetched
def save_file(df,features_dict):
	station_id, interval = data_load_proxy.get_id_int()
	miss_list = missing_values.get_miss_list()
	feat_list = list(features_dict.values())
	file_name = f'station:{station_id}_int:{interval}_miss:{miss_list}_feat:{feat_list}_.csv'
	df.to_csv('data/saved/'+file_name,index = False)

def final_features(df,features_dict,LAG_POLL,TARGET,LAG_TARGET):
	if features_dict["all_pollutants"]==1:
		df = add_poll_lag(df, LAG_POLL)

	if TARGET == 0:
		TARGET = 'PM2.5 (ug/m3)'
	else:
		TARGET = 'PM10 (ug/m3)'

	
	if LAG_TARGET:
		df = add_target_lag(df,LAG_TARGET, TARGET)

	df = df.replace({'None':np.nan})
	df = df.dropna()

	global X,Y


	X = df.drop([TARGET,'From Date'],axis =1)
	print(f'X length = {len(X)}')
	if 'Date' in X.columns:
		X = X.drop(['Date'],axis =1)

	Y = df[TARGET]
	print(f'Y length = {len(Y)}')


def add_poll_lag(df, LAG_POLL):

	POLLUTANT_PARAMS = ['NO (ug/m3)', 'NO2 (ug/m3)', 'NOx (ppb)', 'NH3 (ug/m3)', 'SO2 (ug/m3)','CO (mg/m3)', 'Ozone (ug/m3)', 'Benzene (ug/m3)', 'Toluene (ug/m3)','Eth-Benzene (ug/m3)', 'O Xylene (ug/m3)', 'CH4 (ug/m3)', 'NMHC (ug/m3)', 'SPM (ug/m3)']

	df_cols = df.columns

	pol_cols = list(df_cols.intersection(POLLUTANT_PARAMS))
	for i in range(1,LAG_POLL+1):
		df[[pol_col+f' T-{i}' for pol_col in pol_cols]] = df[pol_cols].shift(i)

	for col in pol_cols:
		del df[col]

	return df

def add_target_lag(df,LAG_TARGET,TARGET):

	for i in range(1,LAG_TARGET+1):

		df[f'{TARGET} T-{i}'] = df[TARGET].shift(i)

	return df

def get_XY():
	return X,Y