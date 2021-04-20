import pandas as pd
import numpy as np

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
		df.insert(0,'From Date',df.index)

		## Reset Index so that 'From Date' is not an INDEX
		df.reset_index(drop=True, inplace=True)

		## Return the df
		return df, False


def PM_0(df):
	
	#df.to_csv('check_this.csv')
	#df.astype({'PM2.5 (ug/m3)': 'float', 'PM10 (ug/m3)': 'float' }).dtypes
	
	df['PM2.5 (ug/m3)'].fillna(value = np.nan, inplace=True)
	#df['PM2.5 (ug/m3)'] = pd.to_numeric(df['PM2.5 (ug/m3)'])
	df['PM10 (ug/m3)'].fillna(value = np.nan, inplace=True)
	df['From Date'] = pd.to_datetime(df['From Date'])


## FIRST PM 2.5 using last day/ 2 days back/ 3 days back/ week average

	for idx,row in df.iterrows():
    
	    # if(type(row['PM2.5 (ug/m3)'])) == type(pd.NaT):

	    if type(row['PM2.5 (ug/m3)']) == type(pd.NaT):
	    	print('hi')
	    	#row['PM2.5 (ug/m3)'] = pd.to_numeric(row['PM2.5 (ug/m3)'])
	    	print(type(row['PM2.5 (ug/m3)']))

	    if np.isnan(row['PM2.5 (ug/m3)']):
	        
	        tm_stmp = row['From Date']
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
	for idx,row in df.iterrows():
	    
	    if np.isnan(row['PM10 (ug/m3)']):
	        
	        tm_stmp = row['From Date']
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

if __name__ == '__main__':
	df = pd.read_csv('data/33_processed.csv')
	df['From Date'] = pd.to_datetime(df['From Date'])
	#df, upsampling = changeInterval(df, '30 minutes')

	df = PM_0(df)

	df.to_csv('check_csv_now.csv')
