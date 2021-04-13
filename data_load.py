import os
import pandas as pd
import numpy as np
import sklearn
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler


STATION_ID = os.environ.get('STATION_ID')

PARAMS = os.environ.get('PARAMS')
MET_PARAMS = ['Temp (degree C)','RH (%)','WS (m/s)','WD (deg)','SR (W/mt2)','BP (mmHg)','VWS (degree)','AT (degree C)','WS (m/s)']
POLLUTANT_PARAMS = ['NO (ug/m3)', 'NO2 (ug/m3)', 'NOx (ppb)', 'NH3 (ug/m3)', 'SO2 (ug/m3)','CO (mg/m3)', 'Ozone (ug/m3)', 'Benzene (ug/m3)', 'Toluene (ug/m3)','Eth-Benzene (ug/m3)', 'O Xylene (ug/m3)', 'CH4 (ug/m3)', 'NMHC (ug/m3)', 'SPM (ug/m3)']

POLLUTANT_PARAMS_LAG = int(os.environ.get('POLLUTANT_PARAMS_LAG'))


TARGET = os.environ.get('TARGET')

LAG = int(os.environ.get('LAG'))

SCALING = os.environ.get('SCALING')


if __name__ == '__main__':

## Load file for the Station using STATION_ID
	df = []
	for f in os.listdir('data/'):
		if str(STATION_ID) in f.split('_'):
			df = pd.read_csv(f'data/{f}')

## Dataset is Loaded

## If no such STATION_ID:
	if len(df)==0:
		print('ERROR: No file with this station id foud')
		exit() ## EXIT

## TARGET
	if TARGET == 'PM2.5':
		TARGET = 'PM2.5 (ug/m3)'
		y = df['PM2.5 (ug/m3)']
	else:
		TARGET = 'PM10 (ug/m3)'
		y = df['PM10 (ug/m3)']


## Returns a Dataframe df_final which has all
## the parameters that are required 

## PARAMS: MET ONLY
	if PARAMS == 'MET':
		## Find intersection between the df's cols & MET_PARAMS
		df_cols = set(df.columns)
		met_cols = list(df_cols.intersection(MET_PARAMS))

		## Make a X so that it has only those PARAMS
		df_met = df[met_cols]
		df_final = df_met

## PARAMS: POLLUTANTS ONLY
	elif PARAMS == 'MET+POL':
		## Find intersection between the df's cols & POLLUTANT_PARAMS
		df_cols = set(df.columns)
		met_cols = list(df_cols.intersection(MET_PARAMS))

		df_met = df[met_cols]
		df_final = df_met

		pol_cols = list(df_cols.intersection(POLLUTANT_PARAMS))

		if POLLUTANT_PARAMS_LAG:
			for i in range(1,POLLUTANT_PARAMS_LAG+1):
				df_final[[pol_col+f' T-{i}' for pol_col in pol_cols]] = df[pol_cols].shift(i)
		
		print(df_final.shape)
		print(df_final.columns)

	


## MISSING VALUES before SCALING
## SCALING ( MIN-MAX, STANDARD, NONE)

	if SCALING:
		if SCALING == 'min-max':
			df_final_scaled = MinMaxScaler().fit_transform(df_final)
		else:
			df_final_scaled = StandardScaler().fit_transform(df_final)

## TIME LAG (t-1) etc..

	if LAG:
		for i in range(1,LAG+1):
			df_final[f'TARGET T-{i}'] = df[TARGET].shift(i)


## ONCE X and Y are ready, do model and metrics



