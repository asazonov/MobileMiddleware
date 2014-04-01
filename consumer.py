import sys

from twisted.python import log
from twisted.internet import reactor

from autobahn.twisted.websocket import connectWS

from autobahn.wamp1.protocol import WampClientFactory, \
                                    WampClientProtocol
import argparse
import requests
import json
import os
import datetime

brokers_list = []

class SensorDataConsumerClientProtocol(WampClientProtocol):
   """
   Protocol for the sensor data consumer client. Uses WAMP protocol.
   """

   def onSessionOpen(self):

      print "Connected to ", wsuri

      def default_response(topic, event):
         print "Received event", topic, event

      # io_file = open("output/" + str(os.getpid()) + ".csv", 'w+')
      # io_file.write("sensor,lat,lng,data,timestamp,time\n")
      
      def save_to_file(topic, event):
         io_file.write(str(str(event['sensor']) + "," + event['lat']) + "," + str(event['lng']) + "," + str(event['data']) + "," + str(event['timestamp']) + "," + str((datetime.datetime.now() - datetime.datetime.strptime(event['timestamp'], "%Y-%m-%d %H:%M:%S.%f")).total_seconds()) + "\n")

      for channel in channels:
         print channel
         self.subscribe(channel, save_to_file)
         # self.subscribe(channel, default_response)

      #self.subscribe("location", default_response)
      #self.subscribe("http://example.com/myEvent1", default_response) # hardwired for testing

def request_broker_address(registry_address,location):
   payload = {'location': location}
   req = requests.get(registry_address+"/request_broker", params=payload)
   response_json = req.text
   response = json.loads(response_json)
   return response["broker_address"]

def request_brokers_l(registry_address, location, radius, max_brokers):
   payload = {'location': location, 'max_brokers' : max_brokers, 'radius' : radius}
   req = requests.get(registry_address + "/request_brokers", params=payload)
   response_json = req.text
   response = json.loads(response_json)
   return response

def request_brokers_xy(registry_address, lat, lng, radius, max_brokers):
   payload = {'lat': lat, 'lng' : lng, 'max_brokers' : max_brokers, 'radius' : radius}
   req = requests.get(registry_address + "/request_brokers", params=payload)
   response_json = req.text
   response = json.loads(response_json)
   return response

if __name__ == '__main__':

   log.startLogging(sys.stdout)

   parser = argparse.ArgumentParser()
   parser.add_argument('-r', '--registry', type=str)
   parser.add_argument('-c', '--channels') #, nargs='+', type=str)
   parser.add_argument('-l', '--location', type=str)
   parser.add_argument('-b', '--maxbrokers', type=int)
   parser.add_argument('-d', '--radius', type=int)
   parser.add_argument('-x', '--lat', type=str)
   parser.add_argument('-y', '--lng', type=str)

   args = parser.parse_args()

   channels = args.channels.split(",")
   location = args.location
   lat = args.lat
   lng = args.lng
   registry_address = args.registry
   max_brokers = args.maxbrokers
   radius = args.radius

   #######################################
   ##    SHOULD PUT SOMETHING HERE TO   ##
   ##    CHECK COMMAND ARGS AND QUIT    ##
   ##       IF THEY AREN'T CORRECT      ##
   #######################################

   ## loops through brokers in broker list, connecting to each
   if (location != None):
      broker_list = request_brokers_l(registry_address, location, radius, max_brokers)
   else:
      if (lat == None or lng == None):
         print "ERROR - must have either location (-l) or latitude (-x) and longitude (-y)"
         exit()
      broker_list = request_brokers_xy(registry_address, lat, lng, radius, max_brokers)

   if (broker_list):
      print "### BROKERS : " + str(len(broker_list))
      io_file = open("output/" + str(os.getpid()) + ".csv", 'w+')
      io_file.write("sensor,lat,lng,data,timestamp,time\n")
      for broker in broker_list:
         wsuri = broker['broker_address']
         print "Connecting to", wsuri
         factory = WampClientFactory(wsuri, debugWamp = False)
         factory.protocol = SensorDataConsumerClientProtocol
         connectWS(factory)
      
      reactor.run()
