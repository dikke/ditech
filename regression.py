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

    Regression Models:
        - Linear Regression
        - Lasso Regression
        - Decision Tree Regression
        - SV Regression
"""    
import sys
import pickle
import numpy as np
import datetime

def mean_squared_error(reg, features, labels):
    # calculate least squares error
    import numpy as np
    predict = reg.predict(features)
    label = np.array(labels)
    return np.sum( (label-predict)**2) / len(label)

def get_model(features_list, dictionary):
    """
    performs model training and model fitting, 
    return the model without testing
    """

    from feature_format import featureFormat, targetFeatureSplit

    ### list the features you want to look at--first item in the 
    ### list will be the "target" feature
    ### features_list = ["gap_predict", "demand", "supply"]
    #features_list = ["demand_predict", "demand", "supply", "demand_t1", "supply_t1", "demand_t2", "supply_t2"]
    data = featureFormat( dictionary, features_list, remove_all_zeroes=False)
    target, features = targetFeatureSplit( data )

    ### training-testing split needed in regression, just like classification
    from sklearn.cross_validation import train_test_split
    feature_train, feature_test, target_train, target_test = train_test_split(features, target, test_size=0.2)
    train_color = "b"
    test_color = "r"


 #   from feature_scaling import scale
 #   feature_train, feature_test = scale(feature_train, feature_test)
    ### Your regression goes here!
    ### Please name it reg, so that the plotting code below picks it up and 
    ### plots it correctly. Don't forget to change the test_color above from "b" to
    ### "r" to differentiate training points from test points.
    """
    from sklearn import linear_model

    model = linear_model.LinearRegression()
    model.fit(feature_train, target_train)

    model = linear_model.Lasso()
    model.fit(feature_train, target_train)
    """

    from sklearn.tree import DecisionTreeRegressor
    model = DecisionTreeRegressor()
    model.fit(feature_train, target_train)


    print "least squares error %f" % mean_squared_error(model, feature_test, target_test)
 #   print model.coef_, model.intercept_
    print "training score", model.score(feature_train, target_train)
    print "test score", model.score(feature_test, target_test)
    print model.predict(33)
    return model


def regression(dictionary):

#    dictionary = pickle.load( open(dic, "r") )
    features_list_demand = ["demand_predict", "demand"]
    features_list_supply = ["supply_predict", "supply"]
    # train supply and demand models
    demand_model = get_model(features_list_demand, dictionary)
    supply_model = get_model(features_list_supply, dictionary)
    # test models
    # create test data
    from feature_format import featureFormat, targetFeatureSplit
    features_list = ["gap_predict", "demand", "supply"]
    # create numpy array of features
    data = featureFormat( dictionary, features_list, remove_all_zeroes=False)
    #target, features = targetFeatureSplit( data )

    #randomly select 20% of data for testing
    np.random.shuffle(data)
    n = len(data) / 5
    test_data = data[:n+1]

    demand_predictions = np.array(demand_model.predict(test_data[:,1].reshape(-1,1)))
    supply_predictions = np.array(supply_model.predict(test_data[:,2].reshape(-1,1)))
    gap_predictions = demand_predictions - supply_predictions
    for i in range(50):
        print gap_predictions[i], test_data[:,0][i]
    # get mean-squared-error
    MSE = np.sum( (test_data[:,0] - gap_predictions)**2 )/ len(test_data)
    print "mean-squared-error: %f" % MSE
    return demand_model, supply_model

def day_of_year(date):
    yy = int(x[0])
    mm = int(x[1])
    dd = int(x[2]) 
    return datetime.datetime(yy,mm,dd).toordinal() - datetime.datetime(yy,01,01).toordinal()

def get_prior_date(date):
    x = date.split("-")
    yy = int(x[0])
    mm = int(x[1])
    dd = int(x[2])
    prior_day_ordinal = datetime.datetime(yy,mm,dd).toordinal() - 1
    prior_date = datetime.datetime.fromordinal(prior_day_ordinal)
    return prior_date.strftime("%Y-%m-%d")

def create_predictions_file(to_predict_list, predict_dict, demand_model, supply_model):
    print "creating predictions file"
    fout = open("ditech_predictions.csv", "w")

    for line in to_predict_list:
        fields = line.split("-")
        date = line[:10]
        timeslot_to_predict = fields[3].split("\n")[0]
        #find prior timeslot and get demand, supply
        timeslot_prior = int(timeslot_to_predict) - 1
        # if prediction is for fist timeslot, then get last timeslot of prior day
        if timeslot_prior == 0:
            timeslot_prior = 144
            date = get_prior_day(date)

        #get demand and supply from prior timeslot for all districts
        if not date in predict_dict:
            print "cannot find date: %s" % date 
            continue

        ts = str(timeslot_prior)
        if not ts in predict_dict[date]:
            print "cannot find timeslot %s for date %d" % (ts, date)

        for district in predict_dict[date][ts]:
            demand, supply = predict_dict[date][ts][district]
            demand_predict = demand_model.predict(demand)
            supply_predict = supply_model.predict(supply)
            gap_predict = demand_predict - supply_predict
            if gap_predict < 0:
                gap_predict = 0
            #format prediction string
            sep = "-"
            field2 = sep.join([date, timeslot_to_predict])
            sep = ","
            str_gap = '%.1f' % gap_predict
            str_out = sep.join([district, field2, str_gap])
            fout.writelines(str_out)
            fout.write("\n")
    fout.close()


if __name__ == "__main__":
    train_dict = pickle.load(open("train_dict", "r"))
    # perform training, derive demand and supply models
    demand_model, supply_model = regression(train_dict)
    # verify if predictions file should be created
    if len(sys.argv) > 1:
        sys.exit()
    #get timeslots that need to have predictions
    predict_dict_file = "test_predict_dict"
    predict_dict = pickle.load(open(predict_dict_file, 'r'))
    f = open("read_me_1.txt", "r")
    f.readline()    #first line is header
    to_predict_list = [line for line in f.readlines()]
    f.close
    create_predictions_file(to_predict_list, predict_dict, demand_model, supply_model)






"""
# calculate least squares error
print "least squares error %f" % mean_squared_error(reg, feature_test, target_test)

print reg.coef_, reg.intercept_
print "training score", reg.score(feature_train, target_train)
print "test score", reg.score(feature_test, target_test)



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