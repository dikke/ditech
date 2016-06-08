"""
generate predictions file based on ditech list of timeslots.
From orders file, create training data file with features per district/day-of-year/Timeslot
y = demand or supply for the next timeslot
- need two models, one for demand, the other for supply 

X = ["district", "day_of_year", "demand_next", "supply_next", "t0", "demand", "supply", "rides_out", "rides_in", 
		"weather", "temperature", "pollution",
		"congestion1", "congestion2", "congestion3", "congestion4", "day_of_week"
		"t1", "t1_demand", "t1_supply", "t1_rides_in","t1_rides_out"]
		"t2", "t2_demand", "t2_supply", "t2_rides_in","t2_rides_out"]
"""
import pickle
import os

orders_dir = "/home/gordon/ditech/season_1/test_data/order_data/"
weather_dir = "/home/gordon/ditech/season_1/test_data/weather_data/"
traffic_dir = "/home/gordon/ditech/season_1/test_data/traffic_data/"
districts_file = "/home/gordon/ditech/season_1/test_data/cluster_map/cluster_map"
poi_file = "/home/gordon/ditech/season_1/test_data/poi_data/poi_data"
orders_out = "test_orders"
gap_dict_file = "test_gap_dict"
predict_dict_file = "test_predict_dict"

driver_dict = pickle.load(open("test_drivers", "r"))
dist_dict = pickle.load(open("test_districts", "r"))
weather_dict = pickle.load(open("test_weather", "r"))
traffic_dict = pickle.load(open("test_traffic", "r"))
poi_dict = pickle.load(open("test_pois", "r"))

def process_orders():
	gap_dict = {}
	demand = 0; supply = 0; into_dist = 0; out_of_dist = 0
	f = open(orders_out, "r")
	for line in f:
		fields = line.split(",")
		driver = fields[0]
		start_dist = fields[2]
		dest_dist = fields[3]
		day_of_year = fields[5]
		day_of_week = fields[6]
		timeslot = fields[7]
		date = fields[8]

		key = (start_dist, day_of_year, timeslot)
		if key in gap_dict:
			demand, supply, into_dist, out_of_dist, day_of_week, date = gap_dict[key]
		else:
			demand = 0; supply = 0; into_dist =0; out_of_dist = 0;

		demand += 1
		if not driver == "NULL": supply += 1

		if dest_dist == start_dist:
			into_dist += 1
		else:
			out_of_dist += 1

		gap_dict[key] = (demand, supply, into_dist, out_of_dist, day_of_week, date)
	
	return gap_dict


# process orders file - two passes:
# pass1: create dict with key: dist:day:ts, counts for demand, supply, rides_out, rides_in
if os.path.exists(gap_dict_file):
	gap_dict = pickle.load(open(gap_dict_file, "r"))
else:
	gap_dict = process_orders()
	pickle.dump(gap_dict, open(gap_dict_file, "w"))


# create training file
missing_label_cnt = 0	# count of missing labels from nest timeslot
record_count = 0
next_ts = 0;
train = {}
cnt = 0
for k in gap_dict:
	"""
	train_dict format = {'2016-01-23'} : {'Timeslot'} : {'District'}
														{'Demand'}
														{'Supply'}
	"""
	district = k[0]; day_of_year = k[1]; timeslot = k[2]
	demand, supply, into_dist, out_of_dist, day_of_week, date = gap_dict[k]
	
	if not date in train:
		train[date] = {}

	if not timeslot in train[date]:
		train[date][timeslot] = {}

	train[date][timeslot][district] = (demand, supply)

	record_count += 1

print "records processed: %d missing_label_cnt: %d" % (record_count, missing_label_cnt) 
pickle.dump(train, open(predict_dict_file, "w"))



