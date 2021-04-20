## Metrics is 5th & THE LAST in heirarchy

## Model -> Metrics -> GUI

from time import sleep
import pandas as pd
import numpy as np

import model

## This function is called by the GUI
def test(metrics_dict):
	

	X_test, Y_test, model = model.get_data()

	stats = {}

	## Saves the images of graphs online
	## Appends the data in a results.csv ( along with links of images )

	## The stats['result'] will be shown on GUI
	## Could be link of a graph & table of results
	return stats

