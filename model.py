## Model is 4th in heirarchy

## Features -> Model -> Metrics

from time import sleep
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import features


# global model, X_test & Y_test for updating in function & sending it to metrics.py
X_test = []
Y_test = []
model = []

## GUI calls this function and gives values of arguments
def get_data(SPLIT_PERC,STANDARDIZATION,MODEL):

	X,Y = features.get_XY()

	global X_test,Y_test
	X_train, X_test, Y_train, Y_test = train_test_split(X,Y,test_size = (STANDARDIZATION//100))

	if STANDARDIZATION:

		X_train,X_test = standardize_X(X_train,X_test,STANDARDIZATION)

	global model
	model = apply_model(MODEL,X_train,X_test,Y_train,Y_test)

	return 

## sending X_test and Y_test and model to metrics.py
def get_model():
	return X_test, Y_test, model