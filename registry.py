from flask import Flask, request
app = Flask(__name__)
import json
from geopy import geocoders, distance
from geopy.point import Point
from operator import itemgetter

producer_list = []

class Producer(object):
	"""docstring for Sensor"""
	def __init__(self, sensors, lat, lng):
		super(Sensor, self).__init__()
		self.sensors = sensors
		self.lat = lat
		self.lng = lng
		

@app.route("/request_broker", methods=['GET'])
def request_broker():
    broker_param = request.args.get('broker_param', 0, type=str)
    print "broker_param", broker_param
    #request_parameters = request.args
    g = geocoders.GoogleV3()
    place, (lat, lng) = g.geocode(broker_param)  
    response = {"broker_address" : "ws://localhost:9000", "address" : place, "lat" : lat, "lng" : lng}
    response_json = json.dumps(response)
    return response_json

def get_best_producer(sensors, lat, lng):
	# list of producers that have the requested sensors
	appropriate_producers = [] 
	for producer in producer_list:
		if sensors.issubset(producer.sensors):
			appropriate_producers.append(producer)

	# now find the closest producer to the defined location
	appropriate_producers_distance = []
	requested_point = Point(lat,lng)
	for producer in appropriate_producers:
		producer_point = Point(producer.lat,producer.lng)
		distance_miles = distance.distance(requested_point, producer_point).miles 
		appropriate_producers_distance.append(distance_miles)
	#index of the smallest item in the list (thus, the closest producer)
	min_distance_index = min(enumerate(appropriate_producers_distance), key=itemgetter(1))[0] 

	return appropriate_producers[min_distance_index]




if __name__ == "__main__":
    a = Sensor(1.33232, 2323.12332, ["camera", "microphone", "location"])
    app.debug = True
    app.run(host='0.0.0.0')