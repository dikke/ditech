#!/usr/bin/python
'''
performs feature scaling on input data X

def scale(X):
	x_scaled = []
	for row in X:
		x_min = float(min(row))
		x_max = float(max(row))
		scaled = [(x - x_min)/(x_max-x_min) for x in row]
		x_scaled.append(scaled)
	return x_scaled
'''
def scale(features_train, features_test):
	from sklearn import preprocessing
	scaler = preprocessing.StandardScaler().fit(features_train)
	features_train = scaler.transform(features_train)
	features_test = scaler.transform(features_test)
	return features_train, features_test