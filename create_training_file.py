"""
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

orders_dir = "/home/gordon/ditech/season_1/training_data/order_data/"
weather_dir = "/home/gordon/ditech/season_1/training_data/weather_data/"
traffic_dir = "/home/gordon/ditech/season_1/training_data/traffic_data/"
districts_file = "/home/gordon/ditech/season_1/training_data/cluster_map/cluster_map"
poi_file = "/home/gordon/ditech/season_1/training_data/poi_data/poi_data"
orders_out = "orders"

driver_dict = pickle.load(open("drivers", "r"))
dist_dict = pickle.load(open("districts", "r"))
weather_dict = pickle.load(open("weather", "r"))
traffic_dict = pickle.load(open("traffic", "r"))
poi_dict = pickle.load(open("pois", "r"))

def process_orders():
	gap_dict = {}
	demand = 0; supply = 0; into_dist = 0; out_of_dist = 0
	f = open("orders", "r")
	for line in f:
		fields = line.split(",")
		driver = fields[0]
		start_dist = fields[2]
		dest_dist = fields[3]
		day_of_year = fields[5]
		day_of_week = fields[6]
		timeslot = fields[7]

		key = (start_dist, day_of_year, timeslot)
		if key in gap_dict:
			demand, supply, into_dist, out_of_dist, day_of_week = gap_dict[key]
		else:
			demand = 0; supply = 0; into_dist =0; out_of_dist = 0;

		demand += 1
		if not driver == "NULL": supply += 1

		if dest_dist == start_dist:
			into_dist += 1
		else:
			out_of_dist += 1

		gap_dict[key] = (demand, supply, into_dist, out_of_dist, day_of_week)
	
	return gap_dict


# process orders file - two passes:
# pass1: create dict with key: dist:day:ts, counts for demand, supply, rides_out, rides_in
if os.path.exists("gap_dict"):
	gap_dict = pickle.load(open("gap_dict", "r"))
else:
	gap_dict = process_orders()
	pickle.dump(gap_dict, open("gap_dict", "w"))


# create training file
next_ts = 0;
train = {}
cnt = 0
for k in gap_dict:
	if cnt > 100:
		break
	district = k[0]; day_of_year = k[1]; timeslot = k[2]
	demand, supply, into_dist, out_of_dist, day_of_week = gap_dict[k]
	train[k] = {"district": k[0], 'day_of_year': k[1], "timeslot": k[2],
				"demand": demand, "supply": supply, "into_district": into_dist,
				"out_of_district": out_of_district, "day_of_week": day_of_week }

	next_ts = (timeslot + 1) % 145
	prior_ts = (timeslot - 1) % 145
	penult_ts  = (timeslot - 2) % 145


	# get targets (next_demand, next_supply)
	key = (district, day_of_year, next_ts)
	if key in gap_dict:
		demand_next, supply_next = gap_dict[key]
		train[k]["demand_predict"] = demand_next
		train[k]["supply_predict"] = supply_next

#	get data from prior timeslot
	key = (district, day_of_year, prior_ts)
	if key in gap_dict:
		demand, supply, into_dist, out_of_dist, day_of_week = gap_dict[key]
		train[k]["demand_t1"] = demand
		train[k]["supply_t1"] = supply
		train[k]["into_district_t1"] = into_dist
		train[k]["out_of_district_t1"] = out_of_district

#	get data from penultimate timeslot
	key = (district, day_of_year, penult_ts)
	if key in gap_dict:
		demand, supply, into_dist, out_of_dist, day_of_week = gap_dict[key]
		train[k]["demand_t2"] = demand
		train[k]["supply_t2"] = supply
		train[k]["into_district_t2"] = into_dist
		train[k]["out_of_district_t2"] = out_of_district

#	get traffic if it exists for this timeslot
	key = str(district) + ":" + str(day_of_year) + ":" + str(timeslot)
	if key in traffic_dict:
		congestion1, congestion2, congestion3, congestion4 = traffic_dict[key]
		train[k]["congestion1"] = congestion1
		train[k]["congestion2"] = congestion2
		train[k]["congestion3"] = congestion3
		train[k]["congestion4"] = congestion4

#	get weather if it exists for this timeslot
	key = str(day_of_year) + ":" + str(timeslot)
	if key in weather_dict:
		weather, temperature, pollution = weather_dict[key]
		train[k]["weather"] = weather
		train[k]["temperature"] = temperature
		train[k]["pollution"] = pollution

	count += 1

pickle.dump(train, open("train_dict", "w"))



