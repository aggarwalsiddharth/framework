## Missing Values is 2nd in heirarchy

## Data_load -> Missing_Values -> Features

from time import sleep
import pandas as pd
import numpy as np
import os
import re # Importing regex for file splitting

import data_load_proxy # for getting the df

# global df for updating in function & sending it to features.py
df = []

# Nearest Station Dictionary used for filling Values
# Format = {station:list of 3 nearest stations ids as strings}
near_st_dict = {33: ['17','36','38'], 21:['17','36','38']}

stats = {'process': '','ok': False}

# Fill list to send to features for file saving
fill_list = []

## GUI calls this function and gives values of arguments
def fill_values(TEMP_NA,PM_NA,POLL_NA,MET_NA):
	global stats# Record the status as the process goes
	global fill_list

	fill_list = [TEMP_NA,PM_NA,POLL_NA,MET_NA]

	# Get df from data_load
	global df
	STATION_ID, df = data_load_proxy.get_df()
	df = df.replace(to_replace=float('-inf'), value=np.nan)

## FIRST FILLING TEMPERATURE
	if TEMP_NA == 0:
		try:
			# wunderground function
			df = Temp_0(df)
			stats['process'] += 'Temperature filled using Wunderground Data <br>'
		except Exception as e:
			print(e)
			stats['ok'] = False
			stats['process'] += 'Some error occured in filling Temperature using Wunderground data <br>'
			return stats

	elif TEMP_NA == 1:
		try:
			# 3 nearest station function
			df = Temp_1(df, STATION_ID)
			stats['process'] += 'Temperature filled using 3 Nearest Station Data <br>'

		except Exception as e:
			print(e)
			stats['ok'] = False
			stats['process'] += 'Some error occured in filling Temperature using 3 Nearest Station data <br>'
			return stats


	else:
		# Swap AT for Temp
		df = Temp_2(df)
		stats['process'] += 'Temperature missing values not filled <br>'

## SECOND FILLING PM
	if PM_NA == 0:
		
		try:
			# Previous Avg Values
			df = PM_0(df)
			stats['process'] += 'PM vals filled using Previous Avg Values Data <br>'
		except Exception as e:
			print('Exception is')
			print(e)
			stats['ok'] = False
			stats['process'] += 'Some error occured in filling PM using Previous Avg Values <br>'
			return stats

		

	elif PM_NA == 1:
		try:
			# 3 nearest station function
			df = PM_1(df, STATION_ID)
			stats['process'] += 'PM vals filled using 3 Nearest Stations Data <br>'
		except:
			stats['ok'] = False
			stats['process'] += 'Some error occured in filling PM using 3 Nearest Stations Data <br>'
			return stats

	else:
		# Drop NA
		df = PM_2(df)
		stats['process'] += 'PM missing values not filled <br>'

## THIRD FILLING POLLUTANTS
	if POLL_NA == 0:
		
		try:
			# Previous Avg Values
			df = Poll_0(df)
			stats['process'] += 'Pollutants filled using Previous Avg Values Data <br>'
		except Exception as e:
			print(e)
			stats['ok'] = False
			stats['process'] += 'Some error occured in filling Pollutants using Previous Avg Values <br>'
			return stats


	elif POLL_NA == 1:
		try:
			# 3 nearest station function
			df = Poll_1(df, STATION_ID)
			stats['process'] += 'Pollutants filled using 3 nearest station Data <br>'
		except:
			stats['ok'] = False
			stats['process'] += 'Some error occured in filling Pollutants using 3 nearest station <br>'
			return stats


	else:
		# Drop NA
		df = Poll_2(df)
		stats['process'] += 'Pollutants missing values not filled <br>'


## FOURTH FILLING MET PARAMS
	if MET_NA == 0:
		try:
			# Use Wunderground Values
			df = Met_0(df)
			stats['process'] += 'Met Params replaced by Wunderground Values <br>'
		except Exception as e:
			print(e)
			stats['ok'] = False
			stats['process'] += 'Some error occured in replacing Met Params by Wunderground Values <br>'
			return stats

	elif MET_NA == 1:
		try:
			# Previous Avg Values
			df = Met_1(df)
			stats['process'] += 'Met Params filled using Previous Avg Values <br>'
		except Exception as e:
			print(e)
			stats['ok'] = False
			stats['process'] += 'Some error occured in filling Met Params by Previous Avg Values <br>'
			return stats

	elif MET_NA==2:
		try:
			# 3 nearest station function
			df = Met_2(df, STATION_ID)
			stats['process'] += 'Met Params filled using 3 nearest station <br>'
		except Exception as e:
			print(e)
			stats['ok'] = False
			stats['process'] += 'Some error occured in filling Met Params by 3 nearest station <br>'
			return stats

	else:
		# Drop NA
		df = Met_3(df)
		stats['process'] += 'Met Parameters missing values not filled <br>'


## Returing to GUI
	stats['ok'] = True
	stats['process'] += 'Missing Values filled as required <br>' 


	return stats


# TEMPERATURE FILLING FUNCTIONS
# TEMP 0: Wunderground
def Temp_0(df):
	## Wunderground data load (It is same for all the stations):
	## It has no empty values and or Duplicates etc
	
	wdf = pd.read_csv('data/wunderground_temp_final.csv')
	wdf['From Date'] = pd.to_datetime(wdf['From Date'])

	## These both are important for the JOIN:
	wdf.index = wdf['From Date']
	#df.index = df['From Date']
	print('1')
	## Right now we are just filling Temperature
	wdf_temp = wdf['Temperature in C'] 

	df = (df.join(wdf['Temperature in C'], on =df['From Date'], how='left')).reset_index(drop=True)
	print('2')
	## Now we can delete the original Temp (degree C) column & AT (degree C) col:
	del df['Temp (degree C)'], df['AT (degree C)']


	return df


# TEMP 1: 3 Nearest Stations
def Temp_1(df, STATION_ID):

	'''
	Here there would be these few steps:
	1. First we have a near_st_dict which is the Nearest Station Dictionary where for each station, three 
	stations are stored
	2. For these three stations, make sure a file is present in the data folder
	3. Once the files are loaded, they are cleaned and gotten ready for a JOIN
	4. In the df, we join the Temp columns of all the 3 files
	5. We make a new column of the mean of all the 3 column 
	6. We fill null values in Temp (degree C) with this mean column
	'''

	# Nearest station dict:
	split_pattern = r"[_.]" # Using regex to get the files that have the number in them

	# 1ST OPEN THE 3 FILES in df1, df2, df3
	file_name = []

	for i,idx in enumerate(near_st_dict[STATION_ID]):
	    
	    for file in os.listdir('./data'):
	        
	        if file.endswith('csv'):
	            
	            if idx in re.split(split_pattern,file):
	                
	                file_name.append(file)
	                print(file)
			
	## Read the file, make its From Date column to datetime, drop duplicates and make From Date its index

	df1 = pd.read_csv(f'data/{file_name[0]}')
	df1['From Date'] = pd.to_datetime(df1['From Date'])
	del df1['Unnamed: 0']
	del df1['S.No']
	df1 = df1.drop_duplicates(subset='From Date')
	df1.index = df1['From Date']

	df2 = pd.read_csv(f'data/{file_name[1]}')
	del df2['Unnamed: 0']
	del df2['S.No']
	df2 = df2.drop_duplicates(subset='From Date')
	df2['From Date'] = pd.to_datetime(df2['From Date'])
	df2.index = df2['From Date']

	df3 = pd.read_csv(f'data/{file_name[2]}')
	del df3['Unnamed: 0']
	del df3['S.No']
	df3['From Date'] = pd.to_datetime(df3['From Date'])
	df3 = df3.drop_duplicates(subset='From Date')
	df3.index = df3['From Date']

	## Change the name of the columns of the files so that they dont clash once they are merged
	df1 = df1.rename(columns={'Temp (degree C)': 'Temp_file_1'})
	df2 = df2.rename(columns={'Temp (degree C)': 'Temp_file_2'})
	df3 = df3.rename(columns={'Temp (degree C)': 'Temp_file_3'})

	## Get df ready for JOIN, make its index FROM DATE
	df.index = df['From Date']

	df = (df.join(df1['Temp_file_1'], on=df['From Date'], how='left')).reset_index(drop=True)
	df = (df.join(df2['Temp_file_2'], on=df['From Date'], how='left')).reset_index(drop=True)
	df = (df.join(df3['Temp_file_3'], on=df['From Date'], how='left')).reset_index(drop=True)

	df['Temp_mean'] = df[['Temp_file_1','Temp_file_2','Temp_file_3']].mean(skipna=True, axis = 1)

	df['Temp (degree C)'] = df['Temp (degree C)'].fillna(df['Temp_mean'])

	## Now we can delete the 4 temp columns:
	del df['Temp_file_1'], df['Temp_file_2'], df['Temp_file_3'], df['Temp_mean']
	
	df.rename(columns={'Temp (degree C)': 'Temperature in C'},inplace=True)

	## Also deleting AT (degree C)

	del df['AT (degree C)']

	return df


# TEMP 2: Swap AT for Temp
def Temp_2(df):

	del df['Temp (degree C)']
	df.rename(columns={'AT (degree C)': 'Temperature in C'},inplace=True)

	return df



# PM FILLING FUNCTIONS
# PM 0: Avg Previous Values
def PM_0(df):
	
	#df.to_csv('check_this.csv')
	#df.astype({'PM2.5 (ug/m3)': 'float', 'PM10 (ug/m3)': 'float' }).dtypes
	
	df['PM2.5 (ug/m3)'].fillna(value = np.nan, inplace=True)
	#df['PM2.5 (ug/m3)'] = pd.to_numeric(df['PM2.5 (ug/m3)'])
	df['PM10 (ug/m3)'].fillna(value = np.nan, inplace=True)
	df['From Date'] = pd.to_datetime(df['From Date'])


## FIRST PM 2.5 using last day/ 2 days back/ 3 days back/ week average

	for idx in range(len(df)):
    

	    if np.isnan(df['PM2.5 (ug/m3)'][idx]):
	        
	        tm_stmp = df['From Date'][idx]
	        adj_tm_stmp = tm_stmp - pd.Timedelta(days=1)
	## CASE 1:
	# The last day's value at this time is present:
	        x = df[df['From Date'] == adj_tm_stmp]['PM2.5 (ug/m3)'].values
	        #print(x[0])
	        if not len(x)==0 and not np.isnan(x[0]):
	            df['PM2.5 (ug/m3)'][idx] = x[0]
	            #print(x[0])

	            
	## CASE 2:
	# The last day's value is not present:
	        else:
	            # Then take 2 day's back value at same time

	            adj_tm_stmp = tm_stmp - pd.Timedelta(days=2)

	            x = df[df['From Date'] == adj_tm_stmp]['PM2.5 (ug/m3)'].values
	            if not len(x)==0 and not np.isnan(x[0]):
	                df['PM2.5 (ug/m3)'][idx] = x[0]
	            
	            else:
	                ## 3 day's back value at same time
	                adj_tm_stmp = tm_stmp - pd.Timedelta(days=3)
	                x = df[df['From Date'] == adj_tm_stmp]['PM2.5 (ug/m3)'].values
	                if not len(x)==0 and not np.isnan(x[0]):
	                    df['PM2.5 (ug/m3)'][idx] = x[0] 

	                else:
	                    pm_list = []

	                    for i in range(1,4):
	                        adj_tm_stmp = tm_stmp - pd.Timedelta(days=i)
	                        #print(adj_tm_stmp)
	                        x = df[df['From Date'] == adj_tm_stmp]['PM2.5 (ug/m3)'].values
	                        if not len(x)==0 and not np.isnan(x[0]):
	                            pm_list.append(x)
	                        #print(x)
	                        else:
	                        #print(e)
	                            pm_list.append(np.nan)


	                    for i in range(0,4):
	                        adj_tm_stmp = tm_stmp - pd.Timedelta(days=i)
	                        #print(adj_tm_stmp)
	                        x = df[df['From Date'] == adj_tm_stmp]['PM2.5 (ug/m3)'].values
	                        if not len(x)==0 and not np.isnan(x[0]):
	                            pm_list.append(x)
	                        #print(x)
	                        else:
	                        #print(e)
	                            pm_list.append(np.nan)
	                    
	                    df['PM2.5 (ug/m3)'][idx] = np.nanmean(pm_list)
	    else:
	        continue
                    

	print('here2')


## NEXT PM 10 using last day/ 2days back/ 3 days back / week average
	for idx in range(len(df)):
	    
	    if np.isnan(df['PM2.5 (ug/m3)'][idx]):
	        
	        tm_stmp = df['From Date'][idx]
	        adj_tm_stmp = tm_stmp - pd.Timedelta(days=1)
	## CASE 1:
	# The last day's value at this time is present:
	        x = df[df['From Date'] == adj_tm_stmp]['PM10 (ug/m3)'].values
	        if not len(x)==0 and not np.isnan(x[0]):
	            df['PM10 (ug/m3)'][idx] = x[0]
	            #print(idx)

	            
	## CASE 2:
	# The last day's value is not present:
	        else:
	            # Then take 2 day's back value at same time

	            adj_tm_stmp = tm_stmp - pd.Timedelta(days=2)

	            x = df[df['From Date'] == adj_tm_stmp]['PM10 (ug/m3)'].values
	            if not len(x)==0 and not np.isnan(x[0]):
	                df['PM10 (ug/m3)'][idx] = x[0]
	            
	            else:
	                ## 3 day's back value at same time
	                adj_tm_stmp = tm_stmp - pd.Timedelta(days=3)
	                x = df[df['From Date'] == adj_tm_stmp]['PM10 (ug/m3)'].values
	                if not len(x)==0 and not np.isnan(x[0]):
	                    df['PM10 (ug/m3)'][idx] = x[0] 

	                else:
	                    pm_list = []

	                    for i in range(1,4):
	                        adj_tm_stmp = tm_stmp - pd.Timedelta(days=i)
	                        #print(adj_tm_stmp)
	                        x = df[df['From Date'] == adj_tm_stmp]['PM10 (ug/m3)'].values
	                        if not len(x)==0 and not np.isnan(x[0]):
	                            pm_list.append(x)
	                        #print(x)
	                        else:
	                        #print(e)
	                            pm_list.append(np.nan)


	                    for i in range(0,4):
	                        adj_tm_stmp = tm_stmp - pd.Timedelta(days=i)
	                        #print(adj_tm_stmp)
	                        x = df[df['From Date'] == adj_tm_stmp]['PM10 (ug/m3)'].values
	                        if not len(x)==0 and not np.isnan(x[0]):
	                            pm_list.append(x)
	                        #print(x)
	                        else:
	                        #print(e)
	                            pm_list.append(np.nan)
	                    
	                    df['PM10 (ug/m3)'][idx] = np.nanmean(pm_list)
	    else:
	        continue

	return df

# PM 1: 3 Nearest Stations
def PM_1(df, STATION_ID):

	'''
	Here there would be these few steps:
	1. First we have a near_st_dict which is the Nearest Station Dictionary where for each station, three 
	stations are stored
	2. For these three stations, make sure a file is present in the data folder
	3. Once the files are loaded, they are cleaned and gotten ready for a JOIN
	4. In the df, we join the Temp columns of all the 3 files
	5. We make a new column of the mean of all the 3 column 
	6. We fill null values in Temp (degree C) with this mean column
	'''

	# Nearest station dict:
	split_pattern = r"[_.]" # Using regex to get the files that have the number in them

	# 1ST OPEN THE 3 FILES in df1, df2, df3
	file_name = []

	for i,idx in enumerate(near_st_dict[STATION_ID]):
	    
	    for file in os.listdir('./data'):
	        
	        if file.endswith('csv'):
	            
	            if idx in re.split(split_pattern,file):
	                
	                file_name.append(file)
	                print(file)
			
	## Read the file, make its From Date column to datetime, drop duplicates and make From Date its index

	df1 = pd.read_csv(f'data/{file_name[0]}')
	df1['From Date'] = pd.to_datetime(df1['From Date'])
	del df1['Unnamed: 0']
	del df1['S.No']
	df1 = df1.drop_duplicates(subset='From Date')
	df1.index = df1['From Date']

	df2 = pd.read_csv(f'data/{file_name[1]}')
	del df2['Unnamed: 0']
	del df2['S.No']
	df2 = df2.drop_duplicates(subset='From Date')
	df2['From Date'] = pd.to_datetime(df2['From Date'])
	df2.index = df2['From Date']

	df3 = pd.read_csv(f'data/{file_name[2]}')
	del df3['Unnamed: 0']
	del df3['S.No']
	df3['From Date'] = pd.to_datetime(df3['From Date'])
	df3 = df3.drop_duplicates(subset='From Date')
	df3.index = df3['From Date']

	## Change the name of the columns of the files so that they dont clash once they are merged
	df1 = df1.rename(columns={'PM2.5 (ug/m3)': 'PM2.5_file_1'})
	df2 = df2.rename(columns={'PM2.5 (ug/m3)': 'PM2.5_file_2'})
	df3 = df3.rename(columns={'PM2.5 (ug/m3)': 'PM2.5_file_3'})

	df1 = df1.rename(columns={'PM10 (ug/m3)': 'PM10_file_1'})
	df2 = df2.rename(columns={'PM10 (ug/m3)': 'PM10_file_2'})
	df3 = df3.rename(columns={'PM10 (ug/m3)': 'PM10_file_3'})

	## Get df ready for JOIN, make its index FROM DATE
	df.index = df['From Date']

	df = (df.join(df1['PM2.5_file_1'], on=df['From Date'], how='left')).reset_index(drop=True)
	df = (df.join(df2['PM2.5_file_2'], on=df['From Date'], how='left')).reset_index(drop=True)
	df = (df.join(df3['PM2.5_file_3'], on=df['From Date'], how='left')).reset_index(drop=True)
	
	df = (df.join(df1['PM10_file_1'], on=df['From Date'], how='left')).reset_index(drop=True)
	df = (df.join(df2['PM10_file_2'], on=df['From Date'], how='left')).reset_index(drop=True)
	df = (df.join(df3['PM10_file_3'], on=df['From Date'], how='left')).reset_index(drop=True)


	df['PM2.5_mean'] = df[['PM2.5_file_1','PM2.5_file_2','PM2.5_file_3']].mean(skipna=True, axis = 1)
	df['PM10_mean'] = df[['PM10_file_1','PM10_file_2','PM10_file_3']].mean(skipna=True, axis = 1)

	
	df['PM2.5 (ug/m3)'] = df['PM2.5 (ug/m3)'].fillna(df['PM2.5_mean'])
	df['PM10 (ug/m3)'] = df['PM10 (ug/m3)'].fillna(df['PM10_mean'])

	## Now we can delete the other columns:
	del df['PM2.5_file_1'], df['PM2.5_file_2'], df['PM2.5_file_3'], df['PM2.5_mean']

	del df['PM10_file_1'], df['PM10_file_2'], df['PM10_file_3'], df['PM10_mean']


	return df


# PM 2: Drop NA
def PM_2(df):

	# drop cols that are empty
	# i am passing it right now

	pass

	return df




# POLLUTANTS FILLING FUNCTIONS
# POLL 0: Avg Previous Values
def Poll_0(df):

	df_cols = df.columns
	POLLUTANT_PARAMS = ['NO (ug/m3)', 'NO2 (ug/m3)', 'NOx (ppb)', 'NH3 (ug/m3)', 'SO2 (ug/m3)','CO (mg/m3)', 'Ozone (ug/m3)', 'Benzene (ug/m3)', 'Toluene (ug/m3)','Eth-Benzene (ug/m3)', 'O Xylene (ug/m3)', 'CH4 (ug/m3)', 'NMHC (ug/m3)', 'SPM (ug/m3)']

	poll_exist = list(df_cols.intersection(POLLUTANT_PARAMS))

	for poll in poll_exist:
		df[poll].fillna(value = np.nan, inplace=True)

	for poll in poll_exist:
	    for idx in range(len(df)):

	        if np.isnan(df[poll][idx]):

	            tm_stmp = df['From Date'][idx]
	            adj_tm_stmp = tm_stmp - pd.Timedelta(days=1)
	    ## CASE 1:
	    # The last day's value at this time is present:
	            x = df[df['From Date'] == adj_tm_stmp][poll].values
	            if not len(x)==0 and not np.isnan(x[0]):
	                df[poll][idx] = x[0]
	                #print(idx)


	    ## CASE 2:
	    # The last day's value is not present:
	            else:
	                # Then take 2 day's back value at same time

	                adj_tm_stmp = tm_stmp - pd.Timedelta(days=2)

	                x = df[df['From Date'] == adj_tm_stmp][poll].values
	                if not len(x)==0 and not np.isnan(x[0]):
	                    df[poll][idx] = x[0]

	                else:
	                    ## 3 day's back value at same time
	                    adj_tm_stmp = tm_stmp - pd.Timedelta(days=3)
	                    x = df[df['From Date'] == adj_tm_stmp][poll].values
	                    if not len(x)==0 and not np.isnan(x[0]):
	                        df[poll][idx] = x[0] 

	                    else:
	                        pm_list = []

	                        for i in range(1,4):
	                            adj_tm_stmp = tm_stmp - pd.Timedelta(days=i)
	                            #print(adj_tm_stmp)
	                            x = df[df['From Date'] == adj_tm_stmp][poll].values
	                            if not len(x)==0 and not np.isnan(x[0]):
	                                pm_list.append(x)
	                            #print(x)
	                            else:
	                            #print(e)
	                                pm_list.append(np.nan)


	                        for i in range(0,4):
	                            adj_tm_stmp = tm_stmp - pd.Timedelta(days=i)
	                            #print(adj_tm_stmp)
	                            x = df[df['From Date'] == adj_tm_stmp][poll].values
	                            if not len(x)==0 and not np.isnan(x[0]):
	                                pm_list.append(x)
	                            #print(x)
	                            else:
	                            #print(e)
	                                pm_list.append(np.nan)

	                        df[poll][idx] = np.nanmean(pm_list)
	        else:
	            continue
                    

	return df


# POLL 1: 3 Nearest Stations
def Poll_1(df, STATION_ID):

	'''
	Here there would be these few steps:
	1. First we have a near_st_dict which is the Nearest Station Dictionary where for each station, three 
	stations are stored
	2. For these three stations, make sure a file is present in the data folder
	3. Once the files are loaded, they are cleaned and gotten ready for a JOIN
	4. In the df, we join the Temp columns of all the 3 files
	5. We make a new column of the mean of all the 3 column 
	6. We fill null values in Temp (degree C) with this mean column
	'''

	# Nearest station dict:
	split_pattern = r"[_.]" # Using regex to get the files that have the number in them

	# 1ST OPEN THE 3 FILES in df1, df2, df3
	file_name = []

	for i,idx in enumerate(near_st_dict[STATION_ID]):
	    
	    for file in os.listdir('./data'):
	        
	        if file.endswith('csv'):
	            
	            if idx in re.split(split_pattern,file):
	                
	                file_name.append(file)
	                print(file)
			
	## Read the file, make its From Date column to datetime, drop duplicates and make From Date its index

	df1 = pd.read_csv(f'data/{file_name[0]}')
	df1['From Date'] = pd.to_datetime(df1['From Date'])
	del df1['Unnamed: 0']
	del df1['S.No']
	df1 = df1.drop_duplicates(subset='From Date')
	df1.index = df1['From Date']

	df2 = pd.read_csv(f'data/{file_name[1]}')
	del df2['Unnamed: 0']
	del df2['S.No']
	df2 = df2.drop_duplicates(subset='From Date')
	df2['From Date'] = pd.to_datetime(df2['From Date'])
	df2.index = df2['From Date']

	df3 = pd.read_csv(f'data/{file_name[2]}')
	del df3['Unnamed: 0']
	del df3['S.No']
	df3['From Date'] = pd.to_datetime(df3['From Date'])
	df3 = df3.drop_duplicates(subset='From Date')
	df3.index = df3['From Date']

	df_cols = df.columns
	POLLUTANT_PARAMS = ['NO (ug/m3)', 'NO2 (ug/m3)', 'NOx (ppb)', 'NH3 (ug/m3)', 'SO2 (ug/m3)','CO (mg/m3)', 'Ozone (ug/m3)', 'Benzene (ug/m3)', 'Toluene (ug/m3)','Eth-Benzene (ug/m3)', 'O Xylene (ug/m3)', 'CH4 (ug/m3)', 'NMHC (ug/m3)', 'SPM (ug/m3)']
	poll_exist = list(df_cols.intersection(POLLUTANT_PARAMS))



	## Change the name of the columns of the files so that they dont clash once they are merged
	for poll in poll_exist:
	    
	    if poll in df1.columns:
	        df1 = df1.rename(columns={poll: f'{poll}_file_1'})
	        
	    else:
	        print(f'1 - {poll}')
	        df1[poll] = np.nan
	        df1 = df1.rename(columns={poll: f'{poll}_file_1'})
	        
	    if poll in df2.columns:
	        df2 = df2.rename(columns={poll: f'{poll}_file_2'})
	        
	    else:
	        print(f'2 - {poll}')
	        df2[poll] = np.nan
	        df2 = df2.rename(columns={poll: f'{poll}_file_2'})
	        
	    if poll in df3.columns:
	        df3 = df3.rename(columns={poll: f'{poll}_file_3'})
	        
	    else:
	        print(f'3 - {poll}')
	        df3[poll] = np.nan
	        df3 = df3.rename(columns={poll: f'{poll}_file_3'})
	      


	## Get df ready for JOIN, make its index FROM DATE
	df.index = df['From Date']

	for poll in poll_exist:
	    df = (df.join(df1[f'{poll}_file_1'], on=df['From Date'], how='left')).reset_index(drop=True)
	    df = (df.join(df2[f'{poll}_file_2'], on=df['From Date'], how='left')).reset_index(drop=True)
	    df = (df.join(df3[f'{poll}_file_3'], on=df['From Date'], how='left')).reset_index(drop=True)
	

	for poll in poll_exist:
		df[f'{poll}_mean'] = df[[f'{poll}_file_1',f'{poll}_file_2',f'{poll}_file_3']].mean(skipna=True, axis = 1)
	

	for poll in poll_exist:
		df[poll] = df[poll].fillna(df[f'{poll}_mean'])


	## Now we can delete the 4 temp columns:
	for poll in poll_exist:
	    del df[f'{poll}_file_1'], df[f'{poll}_file_2'], df[f'{poll}_file_3'], df[f'{poll}_mean']	
	

	return df


# POLL 2: Drop NA
def Poll_2(df):

	## Passing this for now

	pass

	return df



# MET PARAMS FILLING FUNCTIONS
# MET 0: USING WUNDERGROUND VALUES OF MET PARAMS
def Met_0(df):
	## Wunderground data load (It is same for all the stations):
	## It has no empty values and or Duplicates etc
	wdf = pd.read_csv('data/wunderground_temp_final.csv')


	wdf['From Date'] = pd.to_datetime(wdf['From Date'])

	## These both are important for the JOIN:
	wdf.rename(columns={'From Date':'Date'},inplace=True)
	wdf.index = wdf['Date']
	df.index = df['From Date']

	# We dont need temperature here as it is already in the dataset:
	del wdf['Temperature in C']

	df = (df.join(wdf, on =df['From Date'], how='left')).reset_index(drop=True)

	## Deleting the original met columns from the df, so that only Wunderground cols remain
	MET_PARAMS = ['Temp (degree C)','RH (%)','WS (m/s)','WD (deg)','SR (W/mt2)','BP (mmHg)','VWS (degree)','AT (degree C)','WS (m/s)']
	df_cols = df.columns
	df_met = list(df_cols.intersection(MET_PARAMS))
	
	for col in df_met:
		del df[col]

	return df


# MET 1: Previous average values for filling MET PARAMS
def Met_1(df):
	df_cols = df.columns
	MET_PARAMS = ['RH (%)','WS (m/s)','WD (deg)','SR (W/mt2)','BP (mmHg)','VWS (degree)','AT (degree C)','WS (m/s)']
	met_exist = list(df_cols.intersection(MET_PARAMS))
	
	for met in met_exist:
	    df[met].fillna(value = np.nan, inplace=True)

	for met in met_exist:
	    for idx in range(len(df)):

	        if np.isnan(df[met][idx]):

	            tm_stmp = df['From Date'][idx]
	            adj_tm_stmp = tm_stmp - pd.Timedelta(days=1)
	    ## CASE 1:
	    # The last day's value at this time is present:
	            x = df[df['From Date'] == adj_tm_stmp][met].values
	            if not len(x)==0 and not np.isnan(x[0]):
	                df[met][idx] = x[0]
	                #print(idx)


	    ## CASE 2:
	    # The last day's value is not present:
	            else:
	                # Then take 2 day's back value at same time

	                adj_tm_stmp = tm_stmp - pd.Timedelta(days=2)

	                x = df[df['From Date'] == adj_tm_stmp][met].values
	                if not len(x)==0 and not np.isnan(x[0]):
	                    df[met][idx] = x[0]

	                else:
	                    ## 3 day's back value at same time
	                    adj_tm_stmp = tm_stmp - pd.Timedelta(days=3)
	                    x = df[df['From Date'] == adj_tm_stmp][met].values
	                    if not len(x)==0 and not np.isnan(x[0]):
	                        df[met][idx] = x[0] 

	                    else:
	                        pm_list = []

	                        for i in range(1,4):
	                            adj_tm_stmp = tm_stmp - pd.Timedelta(days=i)
	                            #print(adj_tm_stmp)
	                            x = df[df['From Date'] == adj_tm_stmp][met].values
	                            if not len(x)==0 and not np.isnan(x[0]):
	                                pm_list.append(x)
	                            #print(x)
	                            else:
	                            #print(e)
	                                pm_list.append(np.nan)


	                        for i in range(0,4):
	                            adj_tm_stmp = tm_stmp - pd.Timedelta(days=i)
	                            #print(adj_tm_stmp)
	                            x = df[df['From Date'] == adj_tm_stmp][met].values
	                            if not len(x)==0 and not np.isnan(x[0]):
	                                pm_list.append(x)
	                            #print(x)
	                            else:
	                            #print(e)
	                                pm_list.append(np.nan)

	                        df[met][idx] = np.nanmean(pm_list)
	        else:
	            continue

	return df


# MET 2: USING 3 Nearest Neighbouring Stations
def Met_2(df, STATION_ID):

	split_pattern = r"[_.]" # Using regex to get the files that have the number in them

	# 1ST OPEN THE 3 FILES in df1, df2, df3
	file_name = []

	for i,idx in enumerate(near_st_dict[STATION_ID]):
	    
	    for file in os.listdir('./data'):
	        
	        if file.endswith('csv'):
	            
	            if idx in re.split(split_pattern,file):
	                
	                file_name.append(file)
	                print(file)

	## Read the file, make its From Date column to datetime, drop duplicates and make From Date its index

	df1 = pd.read_csv(f'data/{file_name[0]}')
	df1['From Date'] = pd.to_datetime(df1['From Date'])
	del df1['Unnamed: 0']
	del df1['S.No']
	df1 = df1.drop_duplicates(subset='From Date')
	df1.index = df1['From Date']

	df2 = pd.read_csv(f'data/{file_name[1]}')
	del df2['Unnamed: 0']
	del df2['S.No']
	df2 = df2.drop_duplicates(subset='From Date')
	df2['From Date'] = pd.to_datetime(df2['From Date'])
	df2.index = df2['From Date']

	df3 = pd.read_csv(f'data/{file_name[2]}')
	del df3['Unnamed: 0']
	del df3['S.No']
	df3['From Date'] = pd.to_datetime(df3['From Date'])
	df3 = df3.drop_duplicates(subset='From Date')
	df3.index = df3['From Date']

	df_cols = df.columns
	MET_PARAMS = ['RH (%)','WS (m/s)','WD (deg)','SR (W/mt2)','BP (mmHg)','VWS (degree)','AT (degree C)','WS (m/s)']
	met_exist = list(df_cols.intersection(MET_PARAMS))
	#print(met_exist)

	for met in met_exist:
    
	    if met in df1.columns:
	        df1 = df1.rename(columns={met: f'{met}_file_1'})
	        
	    else:
	        print(f'1 - {met}')
	        df1[met] = np.nan
	        df1 = df1.rename(columns={met: f'{met}_file_1'})
	        
	    if met in df2.columns:
	        df2 = df2.rename(columns={met: f'{met}_file_2'})
	        
	    else:
	        print(f'2 - {met}')
	        df2[met] = np.nan
	        df2 = df2.rename(columns={met: f'{met}_file_2'})
	        
	    if met in df3.columns:
	        df3 = df3.rename(columns={met: f'{met}_file_3'})
	        
	    else:
	        print(f'3 - {met}')
	        df3[met] = np.nan
	        df3 = df3.rename(columns={met: f'{met}_file_3'})

	## Get df ready for JOIN, make its index FROM DATE
	df.index = df['From Date']

	for met in met_exist:
	    df = (df.join(df1[f'{met}_file_1'], on=df['From Date'], how='left')).reset_index(drop=True)
	    df = (df.join(df2[f'{met}_file_2'], on=df['From Date'], how='left')).reset_index(drop=True)
	    df = (df.join(df3[f'{met}_file_3'], on=df['From Date'], how='left')).reset_index(drop=True)
	    #print(f'Done for met - {met}')

	for met in met_exist:
	    df[f'{met}_mean'] = df[[f'{met}_file_1',f'{met}_file_2',f'{met}_file_3']].mean(skipna=True, axis = 1)
	      
	for met in met_exist:
	    df[met] = df[met].fillna(df[f'{met}_mean'])

	## Now we can delete the 4 temp columns:
	for met in met_exist:
	    del df[f'{met}_file_1'], df[f'{met}_file_2'], df[f'{met}_file_3'], df[f'{met}_mean']

	return df

# MET 3: Dropping NA
def Met_3(df):
	# passing this for now

	pass

	return df



## sending df to features.py
def get_df():
	return df

def get_miss_list():
	return fill_list