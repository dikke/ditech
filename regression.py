#!/usr/bin/python

"""
    Taken from finance_regression.py in udacity ml course
    Takes a dictionary of features per district/day_of_year/timeslot
    1- creates a numpy array using chosen features to run regression
    2- Labels are demand and supply, gap = demand - supply

    Data preprocessing:
    - use feature scaling for congestion, pollution,
         maybe for weather, temperature
    - dummy variables for district, day_of_week (categories)
    
    Try two separate models for supply and demand
    Look into combining into two labels, since supply/demand are correlated
"""    


def mean_squared_error(reg, features, labels):
    # calculate least squares error
    import numpy as np
    predict = reg.predict(features)
    label = np.array(labels)
    return np.sum( (label-predict)**2) / len(label)


import sys
import pickle

from feature_format import featureFormat, targetFeatureSplit
dictionary = pickle.load( open("train_dict", "r") )

### list the features you want to look at--first item in the 
### list will be the "target" feature
features_list = ["gap_predict", "demand", "supply"]
#features_list = ["demand_predict", "demand", "supply", "demand_t1", "supply_t1", "demand_t2", "supply_t2"]
data = featureFormat( dictionary, features_list, remove_all_zeroes=False)
target, features = targetFeatureSplit( data )

### training-testing split needed in regression, just like classification
from sklearn.cross_validation import train_test_split
feature_train, feature_test, target_train, target_test = train_test_split(features, target, test_size=0.2)
train_color = "b"
test_color = "r"


from feature_scaling import scale
feature_train, feature_test = scale(feature_train, feature_test)
### Your regression goes here!
### Please name it reg, so that the plotting code below picks it up and 
### plots it correctly. Don't forget to change the test_color above from "b" to
### "r" to differentiate training points from test points.

from sklearn import linear_model
reg = linear_model.LinearRegression()
reg.fit(feature_train, target_train)

# calculate least squares error
print "least squares error %f" % mean_squared_error(reg, feature_test, target_test)

print reg.coef_, reg.intercept_
print "training score", reg.score(feature_train, target_train)
print "test score", reg.score(feature_test, target_test)


"""
### draw the scatterplot, with color-coded training and testing points
import matplotlib.pyplot as plt
for feature, target in zip(feature_test, target_test):
    plt.scatter( feature, target, color=test_color ) 
for feature, target in zip(feature_train, target_train):
    plt.scatter( feature, target, color=train_color ) 

### labels for the legend
plt.scatter(feature_test[0], target_test[0], color=test_color, label="test")
plt.scatter(feature_test[0], target_test[0], color=train_color, label="train")




### draw the regression line, once it's coded
try:
    plt.plot( feature_test, reg.predict(feature_test) )
except NameError:
    pass
reg.fit(feature_test, target_test)
plt.plot(feature_train, reg.predict(feature_train), color="b")
print reg.coef_ 
plt.xlabel(features_list[1])
plt.ylabel(features_list[0])
plt.legend()
plt.show()
"""