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
import constants
import sys

def generate_random_data(size=30, chars=string.ascii_letters + string.digits):
   return ''.join(random.choice(chars) for _ in range(size))

registry_address = "" 
available_sensors = ""
lat = ""
lng = ""
producer_id = generate_random_data() # 30 characters, letters + digists. Probably enough for a random ID
heartbeats_skipped = 0

def advertise_availability():
   payload = {'producer_id' : producer_id, 'sensors': available_sensors, 'lat' : lat, 'lng' : lng}
   global heartbeats_skipped  
   try:
      req = requests.get(registry_address+"/register_producer", params=payload)
      response_json = req.text
      response = json.loads(response_json)
      time.sleep(2) # a dirty hack. We need to give time for the broker to initialise
      heartbeats_skipped = 0
      print "Heartbeat"
      return response["broker_address"]
   except:
      print "Heartbeat skipped"
      heartbeats_skipped += 1
      if heartbeats_skipped > constants.MAX_HEARTBEATS_SKIPPED:
         print heartbeats_skipped + " heartbeats skipped. Exiting..."
         sys.exit()


class ProducerPubSubProtocol(WampClientProtocol):
   """
   Protocol class for the producer
   """   
   def onSessionOpen(self):

      print "Connected!"

      def onMyEvent1(topic, event):
         print "Received event", topic, event

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
         start_publishing_sensor(sensor, 1, lat, lng)
      
      def heartbeat():
         advertise_availability()
         reactor.callLater(constants.HEARTBEAT_RATE, heartbeat)

      heartbeat()


   def onClose(self, wasClean, code, reason):
      print "Connection closed", reason
      if reason == constants.UNCLEAN_BROKER_DISCONNECT:
         print "Broker dead. Re-initialising producer with registry"
         initialise_broker()
      else:
         reactor.stop()

def initialise_broker():
   wsuri = advertise_availability()
   print "Connecting to", wsuri

   factory = WampClientFactory(wsuri, debugWamp = False)
   factory.protocol = ProducerPubSubProtocol
   connectWS(factory)

if __name__ == '__main__':

   log.startLogging(sys.stdout)

   parser = argparse.ArgumentParser()
   parser.add_argument('-t', '--tcp', type=int)
   parser.add_argument('-r', '--registry', type=str)
   parser.add_argument('-s', '--sensors', type=str)
   parser.add_argument('-x', '--lat', type=str)
   parser.add_argument('-y', '--lng', type=str)



   args = parser.parse_args()

   sensors = args.sensors.split(",")
   lat = args.lat
   lng = args.lng

   registry_address = args.registry
   available_sensors = args.sensors
   lat = args.lat
   lng = args.lng

   initialise_broker()  
   reactor.run()
   
