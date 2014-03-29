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

      self.subscribe("http://example.com/myEvent1", onMyEvent1)

      self.counter = 0

      def sendMyEvent1():
         self.counter += 1
         self.publish("http://example.com/myEvent1",
            {
               "msg": "Hello from Python!",
               "counter": self.counter
            }
         )
         reactor.callLater(2, sendMyEvent1)

      sendMyEvent1()


   def onClose(self, wasClean, code, reason):
      print "Connection closed", reason
      reactor.stop()


if __name__ == '__main__':

   log.startLogging(sys.stdout)

   parser = argparse.ArgumentParser()
   #parser.add_argument('-t', '--tcp', type=int)
   parser.add_argument('-r', '--registry', type=str)
   parser.add_argument('-s', '--sensors')

   args = parser.parse_args()

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
