## Model is 4th in heirarchy

## Features -> Model -> Metrics

from time import sleep
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import metrics
import features


# global model, X_test & Y_test for updating in function & sending it to metrics.py
X_test = []
Y_test = []
model = []

## GUI calls this function and gives values of arguments
def get_data(SPLIT_PERC,STANDARDIZATION,MODEL):
	print(SPLIT_PERC)

	X,Y = features.get_XY()

	global X_test,Y_test
	X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size = SPLIT_PERC/100,random_state=42)

	if STANDARDIZATION:

		X_train,X_test = standardize_X(X_train,X_test,STANDARDIZATION)

	
	print('starting model\n')
	stats = apply_model(MODEL,X_train,X_test,Y_train,Y_test)

	return stats

## Standardization
def standardize_X(X_train, X_test, STANDARDIZATION):
	if STANDARDIZATION==1:
		from sklearn.preprocessing import StandardScaler
		sc = StandardScaler()
		X_train = sc.fit_transform(X_train)
		X_test = sc.transform (X_test)
	
	else:
		from sklearn.preprocessing import MinMaxScaler
		mm = MinMaxScaler()
		X_train = mm.fit_transform(X_train)
		X_test = mm.transform (X_test)

	return X_train, X_test

def apply_model(MODEL, X_train,X_test,Y_train,Y_test):

	if MODEL ==0:
		from sklearn.linear_model import LinearRegression
		reg = LinearRegression()

	if MODEL ==1:
		from sklearn.linear_model import Ridge
		reg = Ridge()

	if MODEL ==2:
		from sklearn.linear_model import Lasso
		reg = Lasso()

	if MODEL ==3:
		from sklearn.linear_model import ElasticNet
		reg = ElasticNet()

	if MODEL ==4:
		from sklearn.linear_model import SGDRegressor
		reg = SGDRegressor()

	if MODEL ==5:
		from sklearn.tree import DecisionTreeRegressor
		reg = DecisionTreeRegressor()

	if MODEL ==6:
		from sklearn.ensemble import RandomForestRegressor
		reg = RandomForestRegressor()

	if MODEL ==7:
		from sklearn.ensemble import BaggingRegressor
		reg = BaggingRegressor()

	if MODEL ==8:
		from sklearn.ensemble import AdaBoostRegressor
		reg = AdaBoostRegressor()

	if MODEL ==9:
		from sklearn.ensemble import GradientBoostingRegressor
		reg = GradientBoostingRegressor()

	if MODEL ==10:
		from xgboost import XGBRegressor
		reg = XGBRegressor(objective='reg:squarederror')

	if MODEL ==11:
		from sklearn.ensemble import ExtraTreesRegressor
		reg = ExtraTreesRegressor()

	if MODEL ==12:
		from sklearn.svm import SVR
		reg = SVR()

	if MODEL ==13:
		from sklearn.experimental import enable_hist_gradient_boosting
		from sklearn.ensemble import HistGradientBoostingRegressor
		reg = HistGradientBoostingRegressor()

	if MODEL ==14:
		from lightgbm import LGBMRegressor
		reg = LGBMRegressor()

	if MODEL ==15:
		from catboost import CatBoostRegressor
		reg = CatBoostRegressor()

	print('starting fitting\n')
	trained = reg.fit(X_train,Y_train)

	Y_pred = trained.predict(X_test)

	stats = timeseries_evaluation_metrics_func(Y_test, Y_pred)

	return stats


def timeseries_evaluation_metrics_func(y_true, y_pred):

   def mean_absolute_percentage_error(y_true, y_pred):
     y_true, y_pred = np.array(y_true), np.array(y_pred)
     return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

   #print('Evaluation metric results:-')
   stats = {'ok':True, 'result':''}
   stats['result'] += f'MSE is : {metrics.mean_squared_error(y_true, y_pred)} <br>'
   stats['result'] += f'MAE is : {metrics.mean_absolute_error(y_true, y_pred)} <br>'
   stats['result'] += f'RMSE is : {np.sqrt(metrics.mean_squared_error(y_true, y_pred))} <br>'
   stats['result'] += f'MAPE is : {mean_absolute_percentage_error(y_true, y_pred)} <br>'
   stats['result'] += f'R2 is : {metrics.r2_score(y_true, y_pred)} <br>'

   return stats


## sending X_test and Y_test and model to metrics.py
def get_model():
	return X_test, Y_test, model