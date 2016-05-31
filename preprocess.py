#!/usr/bin/python

import os
import pickle
import array
import datetime

def preprocess1():
	"""
	sequence through all orders data, convert order info to:
	driver_id - numeric value
	passenger_id - numeric value
	start_district - numeric value
	dest_district - numeric value
	Price - numeric value
	Day/Timezone - "DDDTTT" where DDD is days from beginning of year,
					 TTT is 1-144 representing the ten-min timeslot 

	create and store driver, passenger, district index files as dicts

	Preprocess:
- create driver, passenger, district dictionaries to map id's to numbers starting at 0
- read from order file and create gap file with gaps per district/date/timeslot
- date will be converted to day in year
- extra data to store:
	- day of week, demand, supply, gap, number of fares out of district, number of fares into district, 
		road_congestion for 4 most congested roads if available, weather, temperature, pollution

	"""

	orders_dir = "/home/gordon/ditech/season_1/training_data/order_data/"
	weather_dir = "/home/gordon/ditech/season_1/training_data/weather_data/"
	traffic_dir = "/home/gordon/ditech/season_1/training_data/traffic_data/"
	districts_file = "/home/gordon/ditech/season_1/training_data/cluster_map/cluster_map"
	poi_file = "/home/gordon/ditech/season_1/training_data/poi_data/poi_data"
	orders_out = "orders"


	if os.path.exists("drivers"):
		driver_dict = pickle.load(open("drivers", "r+"))
	else:
		driver_dict = {"NULL": "NULL"}

	if os.path.exists("passengers"):
		passenger_dict = pickle.load(open("passengers", "r+"))
	else:
		passenger_dict = {}

	#create districts file which maps distric string to shorter value using cluster map
	if os.path.exists("districts"):
		dist_dict = pickle.load(open("districts", "r+"))
	else:
		dist_dict = get_districts(districts_file)

	# process weather info
	if os.path.exists("weather"):
		weather_dict = pickle.load(open("weather", "r"))
	else:
		weather_dict = process_weather(weather_dir)

	# process traffic jam info
	if os.path.exists("traffic"):
		traffic_dict = pickle.load(open("traffic", "r"))
	else:
		traffic_dict = process_traffic(traffic_dir, dist_dict)

	#process poi info
	if os.path.exists("pois"):
		poi_dict = pickle.load(open("pois", "r"))
	else:
		poi_dict = get_poi(poi_file, dist_dict)

	# process orders file
	if not os.path.exists("orders"):
		process_orders(orders_dir, orders_out, driver_dict, passenger_dict, dist_dict)

	# write dict files
	pickle.dump(driver_dict, open( "drivers", "w" ))
	pickle.dump(passenger_dict, open( "passengers", "w" ))
	pickle.dump(dist_dict, open( "districts", "w" ))
	pickle.dump(poi_dict, open( "pois", "w" ))
	pickle.dump(weather_dict, open( "weather", "w" ))
	pickle.dump(traffic_dict, open( "traffic", "w" ))


def process_orders(orders_dir, orders_out, driver_dict, passenger_dict, dist_dict):
	driver_index = 0; passenger_index = 0; district_index = 0;
	orders_files = os.listdir(orders_dir)
	print " order files %s" % orders_files
	fout = open(orders_out, 'w')

	timeslots_cnt = array.array('i', [0]*145)
	timeslots_null_cnt = array.array('i', [0]*145)

	orders_tot = 0
	for ofile in orders_files:
		if ofile.startswith('order'):
			f = open(orders_dir + ofile, 'r')
			print "Processing file: %s" % ofile
			orders_cnt = 0
			for line in f:
				orders_cnt += 1
				fields = line.split()
				driver = fields[1]
				passenger = fields[2]
				start_district = fields[3]
				dest_district = fields[4]
				price = fields[5]
				date = fields[6]
				time = fields[7]
				# create dict keys
				# driver
				if not driver_dict.has_key(fields[1]):
					driver_out = str(driver_index)
					driver_dict[fields[1]] = driver_out
					driver_index += 1
				else:
					driver_out = driver_dict[fields[1]]
				#passenger
				if not passenger_dict.has_key(fields[2]):
					passenger_out = str(passenger_index)
					passenger_dict[fields[2]] = passenger_out
					passenger_index += 1
				else:
					passenger_out = passenger_dict[fields[2]]
				# start dist
				if not dist_dict.has_key(fields[3]):
					start_district_out = str(district_index)
					dist_dict[fields[3]] = start_district_out
					district_index += 1
				else:
					start_district_out = dist_dict[fields[3]]
				# dest dist
				if not dist_dict.has_key(fields[4]):
					dest_district_out = str(district_index)
					dist_dict[fields[4]] = dest_district_outl
					district_index += 1
				else:
					dest_district_out = dist_dict[fields[4]]
				# timeslot (0-143)
				timeslot_out = get_timeslot(fields[7])
				slot = int(timeslot_out)
				timeslots_cnt[slot] += 1
				# count NULL's by timeslot)
				if driver == "NULL":
					timeslots_null_cnt[slot] += 1
				# day in year
				day = str(day_in_year(date))
				# day of week
				dow = str(day_of_week(date))

				# write fields
				str_out = driver_out + "," + passenger_out + "," + \
					  start_district_out + "," + dest_district_out + "," + \
					  price + "," + day + "," + dow + "," + timeslot_out + ","
	 			fout.write(str_out)
	 			fout.write("\n")
	 		f.close()
	 		print "done, orders: %d" % orders_cnt
	 		orders_tot += orders_cnt

	print "done, orders: %d  drivers: %d  passengers: %d  districts: %d" % \
	 		(orders_tot, driver_index, passenger_index, district_index)
	for i in range(len(timeslots_cnt)):
	 	print i, timeslots_cnt[i], timeslots_null_cnt[i]
	#close files
	fout.close()


def process_traffic(d, dist_dict):
	print "processing traffic file"
	traffic_files = os.listdir(d)
	dic = {}
	for file in traffic_files:
		f = open(d + file, "r")
		line = f.readline()
		fields = line.split("\t")
		district = dist_dict[fields[0]]
		congestion1 = int(fields[1].split(":")[1])
		congestion2 = int(fields[2].split(":")[1])
		congestion3 = int(fields[3].split(":")[1])
		congestion4 = int(fields[4].split(":")[1])
		dt = fields[5].split("\r")[0].split(" ")
		day = day_in_year(dt[0])
		timeslot = get_timeslot(dt[1])
		key = district + ":" + str(day) + ":" + timeslot
		dic[key] = (congestion1, congestion2, congestion3, congestion4)
	return dic

def process_weather(wdir):
	"""
	{ key = day:timeslot data = (int weather, int(temperature), int(pollution}
	"""
	print "processing weather"
	dic = {}
	weather_files = os.listdir(wdir)
	for file in weather_files:
		f = open(wdir + file, "r")
		for line in f:
			fields = line.split("\t")
			date, time = fields[0].split(" ")
			day = day_in_year(date)
			dow = day_of_week(date)
			timeslot = get_timeslot(time)
			weather = int(fields[1])
			temp = round(float(fields[2]))
			pollution = fields[3].split("\n")
			pollution = round(float(pollution[0]))
			# create key (day:timeslot)
			key = str(day) + ":" + timeslot
			dic[key] = (weather, temp, pollution)
	return dic

def get_poi(file, dist_dict):
	# create poi dict consisting of number of destinations by 
	# classification per district key will be district:class
	f = open(file, "r")
	di = {}
	for line in f:
		fields = line.split("\t")
		dist = dist_dict[fields[0]]
		for i in range(len(fields)-1):
			if i != 0:
				poi, cnt = fields[i].split(":")
				key = dist + ":" + poi
				di[key] = int(cnt)
	return di

def get_districts(file):
	# create district dictionary based on provided file in cluster_map
	f_dist = open(file, "r")
	dist_dict = {}
	for line in f_dist():
		fields = line.split("\t")
		dist_dict[fields[0]] = fields[1][0]
	f_dist.close()
	return dist_dict

def get_timeslot(time):
	# convert time in one of 144 10-minute daily intervals
	# time is in format ('HH:MM:SS')
	t = time.split(":")
	minutes = int(t[0]) * 60 + int(t[1])
	return str(minutes / 10 + 1)

def day_in_year(date):
	#convert date into day in the year
	# ie 2016-01-03, return 3, third day in year
	x = date.split("-")
	yy = int(x[0])
	mm = int(x[1])
	dd = int(x[2]) 
	return datetime.datetime(yy,mm,dd).toordinal() - datetime.datetime(yy,01,01).toordinal()

def day_of_week(date):
	# return day of week (0=Monday to 6=Sunday)
	x = date.split("-")
	return datetime.datetime(int(x[0]), int(x[1]), int(x[2])).weekday()

if __name__ == '__main__':
	preprocess1()






