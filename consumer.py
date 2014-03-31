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

def request_broker_address(registry_address,request_parameters):
   payload = {'broker_param': request_parameters}
   req = requests.get(registry_address+"/request_broker", params=payload)
   response_json = req.text
   response = json.loads(response_json)
   return response["broker_address"]

def request_brokers(registry_address, request_parameters, max_brokers):
   payload = {'broker_param': request_parameters, 'max_brokers' : max_brokers}
   req = requests.get(registry_address + "/request_brokers", params=payload)
   response_json = req.text
   response = json.loads(response_json)
   # TODO: parse JSON response
      # if nothing valid, wait a while and then request again
      # else, for each broker in json
      #broker_list.append(broker)

   return response


if __name__ == '__main__':

   log.startLogging(sys.stdout)

   parser = argparse.ArgumentParser()
   parser.add_argument('-r', '--registry', type=str)
   parser.add_argument('-c', '--channels') #, nargs='+', type=str)
   parser.add_argument('-p', '--parameters', type=str)
   parser.add_argument('-b', '--maxbrokers', type=str)

   args = parser.parse_args()

   channels = args.channels.split(",")
   parameters = args.parameters
   registry_address = args.registry
   max_brokers = args.maxbrokers

   ## our WAMP/WebSocket client
   ##
 
   # ## TEST VERSION - makes 10 connections with one broker
   # wsuri = request_broker_address(registry_address, parameters)
   # print "Connecting to", wsuri
   # for i in range(0,10):
   #    factory = WampClientFactory(wsuri, debugWamp = False)
   #    factory.protocol = SensorDataConsumerClientProtocol
   #    connectWS(factory) 
   
   ## ACTUAL VERSION - loops through brokers in broker list, connecting to each
   broker_list = request_brokers(registry_address, parameters, max_brokers)
   
   if (broker_list):

      io_file = open("output/" + str(os.getpid()) + ".csv", 'w+')
      io_file.write("sensor,lat,lng,data,timestamp,time\n")
      for broker in broker_list:
         # print "## BROKER ADDRESS = " + broker['broker_address'] + " ##"
         wsuri = broker['broker_address']
         print "Connecting to", wsuri
         factory = WampClientFactory(wsuri, debugWamp = False)
         factory.protocol = SensorDataConsumerClientProtocol
         connectWS(factory)
      
      reactor.run()
