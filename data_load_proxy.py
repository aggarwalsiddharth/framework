## Data_Load is 1st in heirarchy

## GUI -> Data_Load -> Missing_Values

from time import sleep
import pandas as pd
import numpy as np
import os

# global df for updating in function & sending it to missing_values.py
df = []

# Station ID for sending it to Missing Values for 3 Nearest Stations
idx = 0

stats = {'process': '','ok': False}

# Station id and Interval to send it to Features for File saving
station_id = 0
interval = ''

## GUI calls this function and gives values of arguments
def start_load(STATION_ID,INTERVAL):
	global stats# Record the status as the process goes
	global df
	global idx
	global station_id
	global interval
	station_id = STATION_ID
	interval = INTERVAL

	idx = int(STATION_ID) ## For sending it to Missing Values.py

	## First read the file if it exists else say INVALID STATION
	if STATION_ID:
		df = read_file(str(STATION_ID))

		# If df is empty, return error
		if len(df)==0:
			stats['ok'] = False
			stats['process'] += 'Invalid Station' # Append to the process
			return stats

	# If STATION_ID is empty, return error
	else:
		stats['ok'] = False
		stats['process'] += 'Invalid Station'
		return stats


	# Once the file is in, we can begin to pre-process it
	if pre_process_file(STATION_ID):

		df = pd.read_csv('./data/'+f'{STATION_ID}_processed.csv', )
		df['From Date'] = pd.to_datetime(df['From Date'])

		stats['process'] += f' Pulling pre-processed dataset saved as "{STATION_ID}_processed.csv" <br>'
	
	else:
		df = pre_process(df)
		df.to_csv('./data/'+f'{STATION_ID}_processed.csv',index=False, na_rep=np.nan)

	df, upsampling = changeInterval(df, INTERVAL)

	if upsampling == True:
		## we return error saying "TIME UPSAMPLING NOT FEASIBLE. PLEASE CHOOSE ANOTHER TIME INTERVAL"
		stats['process'] += 'Upsampling not feasible. Please choose another time interval <br>'
		stats['ok']= False
		return stats


	## A dictionary for printing what all processes have been taken on the i/p
	## The stats['process'] be showed in GUI.
	stats['ok'] = True
	stats['process'] += 'Re-sampled the file according to the INTERVAL mentioned <br>' 

	## returning to GUI for printing stats & moving ahead if stats['ok']==True
	return stats


## read the file using the id from local computer 'data/' folder
## See documentation.ipynb for why & how
def read_file(idx):
	global stats
	file_name = ''
	for file in os.listdir('./data'):
	    if file.endswith('csv'):
	        if idx in (file.split('_')):
	            file_name = file

    # If station with this id found, return df
	if file_name:
		df = pd.read_csv('./data/' + file_name)
		stats['process'] += f'File uploaded: data/{file_name} <br>'
		return df

	# If station with this id not found, return False
	else:
		return False


## check if the pre-processed file is already saved & exists
def pre_process_file(STATION_ID):

	if f'{STATION_ID}_processed.csv' in os.listdir('./data'):
		return True
	else:
		return False

## Pre-process the df
def pre_process(df):
	global stats


	## Deleting empty columns
	empty_cols = [i for i in df.columns if df[i].count()==0]

	for i in empty_cols:
	    del df[i]
	stats['process'] += f'Deleted empty columns {empty_cols} <br>'

	## Delete Duplicates
	del df['S.No']
	df = df.drop_duplicates()
	stats['process'] += f'Deleted duplicate rows <br>'


	## Convert FROM DATE col to DATETIME format
	df['From Date'] = pd.to_datetime(df['From Date'])
	stats['process'] += f'Converted "From Date" column to Date-Time <br>'

	# Sort Values by From Date
	df = df.sort_values(by='From Date')
	stats['process'] += f'Sorted values by "DATE"<br>'
	
	## Re-index the df
	df.insert(0,'S.No',df.index)
	stats['process'] += f'Re-indexing the dataframe <br>'

	## Deleting Unnamed: 0 column (if it exists)
	if 'Unnamed: 0' in df.columns:
	    del df['Unnamed: 0']
	    stats['process'] += f'Deleted redundant column "Unnamed: 0 " <br>'

	stats['process'] += ' The dataset is now ready '

	return df

## Resample the df according to the INTERVAL
def changeInterval(df, INTERVAL):

	## Get to know the interval that is currently in the file
	if (df['From Date'][1] - df['From Date'][0]) > pd.to_timedelta(INTERVAL):
		# we return error saying "TIME UPSAMPLING NOT FEASIBLE. PLEASE CHOOSE ANOTHER TIME INTERVAL"
		return df,True

	## If we have to downsample, we do the following process:
	else:

		## We make the minutes to min AND hour(s) to H
		if INTERVAL.split(" ")[1]=='minutes':
			INTERVAL = INTERVAL.replace(INTERVAL.split(" ")[1],'min')
		else:
			INTERVAL = INTERVAL.replace(INTERVAL.split(" ")[1],'H')

		## Resample the data on FROM DATE by calculating mean()
		df = (df.resample(rule= INTERVAL ,on='From Date').mean())

		## Deleting the S.No because it is also averaged
		del df['S.No']

		## Inserting 'From Date' because right now it is a INDEX
		#df.insert(0,'From Date',df.index)

		## Reset Index so that 'From Date' is not an INDEX
		df.reset_index(inplace=True)

		## Return the df
		return df, False


## sending df to missing_values.py
def get_df():
	return idx, df

## 
def get_id_int():
	return station_id,interval

def check_file(STATION_ID,INTERVAL,TEMP_NA,PM_NA,POLL_NA,MET_NA,features_dict):
	miss_list = [TEMP_NA,PM_NA,POLL_NA,MET_NA]
	feat_list = list(features_dict.values())
	file_name = f'station:{STATION_ID}_int:{INTERVAL}_miss:{miss_list}_feat:{feat_list}_.csv'
	if file_name in os.listdir('./data/saved'):
		df = pd.read_csv('data/saved/'+file_name)
		print('File taken saved')
		return df, True
	else:
		return 0, False