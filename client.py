import sys

from twisted.python import log
from twisted.internet import reactor

from autobahn.twisted.websocket import connectWS

from autobahn.wamp1.protocol import WampClientFactory, \
                                    WampClientProtocol


class SensorDataConsumerClientProtocol(WampClientProtocol):
   """
   Protocol for the sensor data consumer client. Uses WAMP protocol.
   """

   def onSessionOpen(self):

      print "Connected to ", wsuri

      def onMyEvent1(topic, event):
         print "Received event", topic, event

      self.subscribe(channel, onMyEvent1)


if __name__ == '__main__':

   log.startLogging(sys.stdout)

   if len(sys.argv) > 1:
      wsuri = sys.argv[1]
      channel = sys.argv[2]
   else:
      wsuri = "ws://localhost:9000"
      channel = "http://example.com/myEvent1"

   print "Connecting to", wsuri

   ## our WAMP/WebSocket client
   ##
   factory = WampClientFactory(wsuri, debugWamp = False)
   factory.protocol = SensorDataConsumerClientProtocol
   connectWS(factory)
   
   reactor.run()
