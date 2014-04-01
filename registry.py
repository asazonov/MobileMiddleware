from flask import Flask, request
app = Flask(__name__)
import json
from geopy import geocoders, distance as geopy_distance
from geopy.point import Point
from operator import itemgetter
import datetime
import time
from helper import pick_unused_port, spawn_daemon
import subprocess
import constants
import os
import pickle
import signal

producers = {}

class Producer(object):
    """docstring for Sensor"""
    def __init__(self, producer_id,  sensors, lat, lng, access_time, broker_address, broker_pid):
        super(Producer, self).__init__()
        self.sensors = sensors
        #self.location = location
        self.lat = lat
        self.lng = lng
        self.access_time = access_time
        self.broker_address = broker_address
        self.producer_id = producer_id
        self.broker_pid = broker_pid
        # print "###BROKER PID : " + str(broker_pid) + " ###"
        #self.http_port = http

    def __str__(self):
        return str([self.producer_id, self.sensors, self.lat, self.lng, self.access_time, self.broker_address, broker_pid])


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
        pickle.dump(producers, open( "producers.p", "wb" ))
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
        # cmd = ['python', "D:\Andrew\Documents\GitHub\MobileMiddleware\server.py", "-p" + str(open_port), "-t" + str(open_port2)]
        #subprocess.Popen(cmd)
        #spawn_daemon(cmd)
        #spawn_daemon(cmd)
        BROKER_COMMAND = ['nohup','python', "broker.py", "-p" + str(open_port), "-t" + str(open_port2), "-s", str(sensors)]
        broker = subprocess.Popen(BROKER_COMMAND, stdout=open('/dev/null', 'w'), stderr=open('logfile.log', 'a'), preexec_fn=os.setpgrp, close_fds = True)
        access_time = datetime.datetime.now()
        broker_address = "ws://localhost:" + str(open_port)

        producer = Producer(producer_id, sensors, lat, lng, access_time, broker_address, broker.pid)
        # producer = Producer(sensors, location, lat, lng, access_time, broker_address)
        producers[producer_id] = producer
        pickle.dump(producers, open( "producers.p", "wb" ))
        print "###BROKER PID [register producer]: " + str(producer.broker_pid) + " ###"


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
    sensors = request.args.get('sensors', type=str).split(",")

    if (location != None):
        geocoder = geocoders.GoogleV3()
        place, (lat, lng) = geocoder.geocode(location) 
    else:
        lat = request.args.get('lat', type=str)
        lng = request.args.get('lng', type=str)

    relevant_producers = get_relevant_producers(sensors, lat, lng, radius, max_brokers)

    response = []
    if (relevant_producers):
        for producer in relevant_producers:
            response.append({"broker_address" : producer.broker_address, "lat" : producer.lat, "lng" : producer.lng})

    response_json = json.dumps(response)
    return response_json

def get_relevant_producers(sensors, lat, lng, radius, max):
    relevant_producers = []
    current = 0
    centre = Point(lat, lng)

    now = datetime.datetime.now()

    for producer in producers.values():
        print "$$$ PRODUCER : " + producer.producer_id
        print " > BROKER : " + str(producer.broker_pid)
        print "======================"

    print ""
    print ""
    print ""

    for producer in producers.values():

        if ((now - producer.access_time).total_seconds() > constants.HEARTBEAT_RATE_OUTDATED):
            print "Removing producer " + producer.producer_id
            # print "###BROKER PID [get_relevant]: " + str(producer.broker_pid.pid) + " ###"
            # print "###BROKER PID [get_relevant]: " + str(int(producer.broker_pid)) + " ###"
            print "Removing broker " + str(producer.broker_pid)

            os.kill(producer.broker_pid, signal.SIGKILL) # kill broker associated with the producer
            producers.pop(producer.producer_id)
            pickle.dump(producers, open( "producers.p", "wb" ))
            continue

        if (current < max):
            prod_location = Point(producer.lat, producer.lng)
            distance = geopy_distance.distance(centre, prod_location).miles
            if set(sensors).issubset(set(producer.sensors)) and distance <= radius:
                relevant_producers.append(producer)
                current += 1
        else:
            break

    return relevant_producers

def remove_dead_producers():
    for producers in producers.values():
        if ((now - producer.access_time).total_seconds() > constants.HEARTBEAT_RATE_OUTDATED):
            os.kill(producer.broker_pid, signal.SIGKILL) # kill broker associated with the producer
            producers.pop(producer.producer_id)
            pickle.dump(producers, open( "producers.p", "wb" ))
            continue


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
        distance_miles = geopy_distance.distance(requested_point, producer_point).miles 
        appropriate_producers_distance.append(distance_miles)
    #index of the smallest item in the list (thus, the closest producer)
    min_distance_index = min(enumerate(appropriate_producers_distance), key=itemgetter(1))[0] 

    return appropriate_producers[min_distance_index]




if __name__ == "__main__":
    try:
        producers = pickle.load( open( "producers.p", "rb" ) )
        remove_dead_producers
    except:
        print "No pickle yet!"
    app.debug = True
    app.run(host='127.0.0.1')
    #lol