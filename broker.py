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
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import listenWS

from autobahn.wamp1.protocol import WampServerFactory, \
                                    WampServerProtocol

import argparse
import ast

sensors = ""


class MyPubSubServerProtocol(WampServerProtocol):
   """
   Protocol class for our simple demo WAMP server.
   """

   def onSessionOpen(self):
      ## When the WAMP session to a client has been established,
      ## register a single fixed URI as PubSub topic that our
      ## message broker will handle
      ##
      for sensor in sensors:
         self.registerForPubSub(sensor)
      #self.registerForPubSub("http://example.com/myEvent1")
      #self.registerForPubSub("camera")
      #self.registerForPubSub("location")
      #self.registerForPubSub("speed")

if __name__ == '__main__':
   log.startLogging(sys.stdout)

   parser = argparse.ArgumentParser()
   parser.add_argument('-p', '--port', type=str)
   parser.add_argument('-t', '--tcp', type=int)
   parser.add_argument('-s', '--sensors', type=str)

   args = parser.parse_args()
   print "sensorssensorssensors"  + sensors
   port = args.port
   tcp = args.tcp
   sensors = ast.literal_eval(args.sensors)

   wampFactory = WampServerFactory("ws://localhost:" + str(port), debugWamp = False)
   wampFactory.protocol = MyPubSubServerProtocol
   listenWS(wampFactory)

   ## our Web server (for static Web content)
   ##
   webFactory = Site(File("."))
   reactor.listenTCP(int(tcp), webFactory)

   ## run the Twisted network reactor
   ##
   reactor.run()
