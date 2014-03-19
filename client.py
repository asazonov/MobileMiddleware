import sys

from twisted.python import log
from twisted.internet import reactor

from autobahn.twisted.websocket import connectWS

from autobahn.wamp1.protocol import WampClientFactory, \
                                    WampClientProtocol
import argparse


class SensorDataConsumerClientProtocol(WampClientProtocol):
   """
   Protocol for the sensor data consumer client. Uses WAMP protocol.
   """

   def onSessionOpen(self):

      print "Connected to ", wsuri

      def default_response(topic, event):
         print "Received event", topic, event

      for channel in channels:
         self.subscribe(channel, default_response)


if __name__ == '__main__':

   log.startLogging(sys.stdout)

   parser = argparse.ArgumentParser()
   parser.add_argument('-s', '--server', type=str)
   parser.add_argument('-c', '--channels', nargs='+', type=str)
   args = parser.parse_args()

   wsuri = args.server
   channels = args.channels

   print "Connecting to", wsuri

   ## our WAMP/WebSocket client
   ##
   factory = WampClientFactory(wsuri, debugWamp = False)
   factory.protocol = SensorDataConsumerClientProtocol
   connectWS(factory)
   
   reactor.run()
