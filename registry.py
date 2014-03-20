from flask import Flask, request
app = Flask(__name__)
import json
from geopy import geocoders, distance
from geopy.point import Point
from operator import itemgetter
import datetime
import time
from helper import pick_unused_port, spawn_daemon
import subprocess

producer_list = []

class Producer(object):
    """docstring for Sensor"""
    def __init__(self, sensors, location, lat, lng, access_time, broker_address):
        super(Producer, self).__init__()
        self.sensors = sensors
        self.location = location
        self.lat = lat
        self.lng = lng
        self.access_time = access_time
        self.broker_address = broker_address
        #self.http_port = http

    def __str__(self):
        return str([self.sensors, self.location, self.lat, self.lng, self.access_time, self.broker_address])


@app.route("/list_brokers", methods=['GET'])
def list_brokers():
    resp = ""
    resp += str(len(producer_list))
    for producer in producer_list:
        resp += "<p>" + str(producer) + "</p>"
    return resp

@app.route("/register_producer", methods=['GET'])
def register_producer():
    sensors = request.args.get('sensors', type=str).split(",")
    lat = request.args.get('lat', type=str)
    lng = request.args.get('lng', type=str)
    access_time = datetime.datetime.now()
    geocoder = geocoders.GoogleV3()

    # Unicode in Python 2 :-(
    location = unicode(geocoder.reverse(Point(lat, lng))[0]).encode('utf-8') 
    open_port = pick_unused_port()
    open_port2 = pick_unused_port()
    #spawn_demon("/usr/bin/say", "/Users/alehins/Documents/StAndrews/CT/MobileMiddleware/server.py -p " + str(open_port))
    #spawn_demon("say hi")
    cmd = ['/usr/bin/python', "/Users/alehins/Documents/StAndrews/CT/MobileMiddleware/server.py", "-p" + str(open_port), "-t" + str(open_port2)]
    # cmd = ['python', "D:\Andrew\Documents\GitHub\MobileMiddleware\server.py", "-p" + str(open_port), "-t" + str(open_port2)]
    subprocess.Popen(cmd)
    #spawn_daemon(cmd)
    access_time = datetime.datetime.now()
    broker_address = "ws://localhost:" + str(open_port)

    producer = Producer(sensors, location, lat, lng, access_time, broker_address)
    producer_list.append(producer)

    response = {"broker_address" : broker_address, "http_port" : open_port2}
    response_json = json.dumps(response)
    return response_json


@app.route("/request_broker", methods=['GET'])
def request_broker():
    broker_param = request.args.get('broker_param', type=str)
    print "broker_param", broker_param
    #request_parameters = request.args
    geocoder = geocoders.GoogleV3()
    place, (lat, lng) = geocoder.geocode(broker_param) 
    producer = get_best_producer(["camera", "microphone", "location"], lat, lng)

    response = {"broker_address" : producer.broker_address, "location" : producer.location, "lat" : producer.lat, "lng" : producer.lng}
    response_json = json.dumps(response)
    return response_json

def get_best_producer(sensors, lat, lng):
    # list of producers that have the requested sensors
    appropriate_producers = [] 
    for producer in producer_list:
        if set(sensors).issubset(set(producer.sensors)):
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
    #a = Producer(["camera", "microphone", "location"], "Moscow", 55.755826, 37.6173, datetime.datetime.now(), "ws://localhost:9000")
    #b = Producer(["camera", "microphone", "location"], "San Paolo", -23.5505199, -46.63330939999999, datetime.datetime.now(), "ws://localhost:9000")
    #producer_list.append(a)
    #producer_list.append(b)

    app.debug = True
    app.run(host='127.0.0.1')