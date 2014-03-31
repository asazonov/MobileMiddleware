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

class SensorDataConsumerClientProtocol(WampClientProtocol):
   """
   Protocol for the sensor data consumer client. Uses WAMP protocol.
   """

   def onSessionOpen(self):

      print "Connected to ", wsuri

      def default_response(topic, event):
         print "Received event", topic, event

      io_file = open("output/" + str(os.getpid()) + ".csv", 'w+')
      io_file.write("sensor,lat,lng,data,timestamp,time\n")
      
      def save_to_file(topic, event):
         io_file.write(str(str(event['sensor']) + "," + event['lat']) + "," + str(event['lng']) + "," + str(event['data']) + "," + str(event['timestamp']) + "," + str((datetime.datetime.now() - datetime.datetime.strptime(event['timestamp'], "%Y-%m-%d %H:%M:%S.%f")).total_seconds()) + "\n")

      for channel in channels:
         print channel
         self.subscribe(channel, save_to_file)

      #self.subscribe("location", default_response)
      #self.subscribe("http://example.com/myEvent1", default_response) # hardwired for testing

def request_broker_address(registry_address,request_parameters):
   payload = {'broker_param': request_parameters}
   req = requests.get(registry_address+"/request_broker", params=payload)
   response_json = req.text
   response = json.loads(response_json)
   return response["broker_address"]


if __name__ == '__main__':

   log.startLogging(sys.stdout)

   parser = argparse.ArgumentParser()
   parser.add_argument('-r', '--registry', type=str)
   parser.add_argument('-c', '--channels') #, nargs='+', type=str)
   parser.add_argument('-p', '--parameters', type=str)

   args = parser.parse_args()

   channels = args.channels.split(",")
   parameters = args.parameters
   registry_address = args.registry

   wsuri = request_broker_address(registry_address, parameters)

   print "Connecting to", wsuri

   ## our WAMP/WebSocket client
   ##
   factory = WampClientFactory(wsuri, debugWamp = False)
   factory.protocol = SensorDataConsumerClientProtocol
   connectWS(factory)
   
   reactor.run()
