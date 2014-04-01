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
import constants
import os

producers = {}

class Producer(object):
    """docstring for Sensor"""
    def __init__(self, producer_id,  sensors, lat, lng, access_time, broker_address):
        super(Producer, self).__init__()
        self.sensors = sensors
        #self.location = location
        self.lat = lat
        self.lng = lng
        self.access_time = access_time
        self.broker_address = broker_address
        self.producer_id = producer_id
        #self.http_port = http

    def __str__(self):
        return str([self.producer_id, self.sensors, self.lat, self.lng, self.access_time, self.broker_address])


@app.route("/list_brokers", methods=['GET'])
def list_brokers():
    resp = ""
    resp += str(len(producers.values()))
    for producer in producers.values():
        resp += "<p>" + str(producer) + "</p>"
    return resp

@app.route("/register_producer", methods=['GET'])
def register_producer():

    producer_id = request.args.get('producer_id', type=str)

    if producer_id in producers:
        producers[producer_id].access_time = datetime.datetime.now()

    else:
        sensors = request.args.get('sensors', type=str).split(",")
        lat = request.args.get('lat', type=str)
        lng = request.args.get('lng', type=str)
        access_time = datetime.datetime.now()
        #geocoder = geocoders.GoogleV3()

        # Unicode in Python 2 :-(
        #location = unicode(geocoder.reverse(Point(lat, lng))[0]).encode('utf-8') 
        open_port = pick_unused_port()
        open_port2 = pick_unused_port()
        #spawn_demon("/usr/bin/say", "/Users/alehins/Documents/StAndrews/CT/MobileMiddleware/server.py -p " + str(open_port))
        #spawn_demon("say hi")
        cmd = ['nohup','python', "server.py", "-p" + str(open_port), "-t" + str(open_port2)]
        # cmd = ['python', "D:\Andrew\Documents\GitHub\MobileMiddleware\server.py", "-p" + str(open_port), "-t" + str(open_port2)]
        #subprocess.Popen(cmd)
        #spawn_daemon(cmd)
        #spawn_daemon(cmd)
        subprocess.Popen(cmd, stdout=open('/dev/null', 'w'), stderr=open('logfile.log', 'a'), preexec_fn=os.setpgrp, close_fds = True)
        access_time = datetime.datetime.now()
        broker_address = "ws://localhost:" + str(open_port)

        producer = Producer(producer_id, sensors, lat, lng, access_time, broker_address)
        # producer = Producer(sensors, location, lat, lng, access_time, broker_address)
        producers[producer_id] = producer

    response = {"broker_address" : producers[producer_id].broker_address} #, "http_port" : open_port2}
    response_json = json.dumps(response)
    return response_json


# @app.route("/request_broker", methods=['GET'])
# def request_broker():
#     location = request.args.get('location', type=str)
#     print "location", location
#     #request_parameters = request.args
#     geocoder = geocoders.GoogleV3()
#     place, (lat, lng) = geocoder.geocode(location) 
#     producer = get_best_producer(["camera", "microphone", "location"], lat, lng)
#     response = {"broker_address" : producer.broker_address, "lat" : producer.lat, "lng" : producer.lng}
#     response_json = json.dumps(response)
#     return response_json

@app.route("/request_brokers", methods=['GET'])
def request_brokers():
    location = request.args.get('location', type=str)
    max_brokers = request.args.get('max_brokers', type=int)
    radius = request.args.get('radius', type=int)

    geocoder = geocoders.GoogleV3()
    place, (lat, lng) = geocoder.geocode(location) 
    relevant_producers = get_relevant_producers(["location"], lat, lng, radius, max_brokers)

    response = []
    if (relevant_producers):
        for producer in relevant_producers:
            response.append({"broker_address" : producer.broker_address, "lat" : producer.lat, "lng" : producer.lng})

    response_json = json.dumps(response)
    print "I AM RETURNING: " + str(response_json)
    return response_json

def get_relevant_producers(sensors, lat, lng, radius, max):
    relevant_producers = []
    current = 0
    centre = Point(lat, lng)

    now = datetime.datetime.now()



    for producer in producers.values():

        if ((now - producer.access_time).total_seconds() > constants.HEARTBEAT_RATE_OUTDATED):
            print "Removing producer " + producer.producer_id
            producers.pop(producer.producer_id)
            continue

        if (current < max):
            prod_location = Point(producer.lat, producer.lng)
            distance = distance.distance(centre, prod_location).miles
            if set(sensors).issubset(set(producer.sensors)) and distance <= radius:
                relevant_producers.append(producer)
                current += 1
        else:
            break

    return relevant_producers

def get_best_producer(sensors, lat, lng):
    # list of producers that have the requested sensors
    appropriate_producers = []
    for producer in producers:
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
    #producers.append(a)
    #producers.append(b)

    app.debug = True
    app.run(host='127.0.0.1')