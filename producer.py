###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import sys

from twisted.python import log
from twisted.internet import reactor

from autobahn.twisted.websocket import connectWS

from autobahn.wamp1.protocol import WampClientFactory, \
                                    WampClientProtocol
import argparse
import random
import requests
import json
import time
import datetime
import random
import string

def generate_random_data(size=30, chars=string.ascii_letters + string.digits):
   return ''.join(random.choice(chars) for _ in range(size))

def advertise_availability(registry_address, available_sensors, lat, lng):
   payload = {'sensors': available_sensors, 'lat' : lat, 'lng' : lng}
   req = requests.get(registry_address+"/register_producer", params=payload)
   response_json = req.text
   response = json.loads(response_json)
   time.sleep(2) # a dirty hack. We need to give time for the broker to initialise
   return response["broker_address"]


class MyPubSubClientProtocol(WampClientProtocol):
   """
   Protocol class for our simple demo WAMP client.
   """

   def onSessionOpen(self):

      print "Connected!"

      def onMyEvent1(topic, event):
         print "Received event", topic, event

      #self.subscribe("http://example.com/myEvent1", onMyEvent1)

      self.counter = 0

      def start_publishing_sensor(sensor_name, every_n_seconds, lat, lng):
         self.publish(sensor_name,
            {
               "sensor" : sensor_name,
               "data" : generate_random_data(),
               "timestamp" : str(datetime.datetime.now()),
               "lat" : str(lat),
               "lng" : str(lng)

            }
         )
         reactor.callLater(every_n_seconds, start_publishing_sensor, sensor_name=sensor_name, every_n_seconds=every_n_seconds, lat=lat, lng=lng)

      for sensor in sensors:
         self.subscribe(sensor, onMyEvent1)
         start_publishing_sensor(sensor, 0.1, lat, lng)
      
      #start_publishing_sensor("http://example.com/myEvent1", 0.1, lat, lng)


   def onClose(self, wasClean, code, reason):
      print "Connection closed", reason
      reactor.stop()


if __name__ == '__main__':

   log.startLogging(sys.stdout)

   parser = argparse.ArgumentParser()
   #parser.add_argument('-t', '--tcp', type=int)
   parser.add_argument('-r', '--registry', type=str)
   parser.add_argument('-s', '--sensors')
   parser.add_argument('-x', '--lat')
   parser.add_argument('-y', '--lng')



   args = parser.parse_args()

   sensors = args.sensors.split(",")
   lat = args.lat
   lng = args.lng


   wsuri = advertise_availability(args.registry, args.sensors, 55.755826 + random.random() * 3, 37.6173 + random.random() * 3)
   print "Connecting to", wsuri

   ## our WAMP/WebSocket client
   ##
   factory = WampClientFactory(wsuri, debugWamp = False)
   factory.protocol = MyPubSubClientProtocol
   connectWS(factory)

   ## run the Twisted network reactor
   ##
   reactor.run()
