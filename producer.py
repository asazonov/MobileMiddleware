import argparse
import random
import requests
import json
import time
import datetime
import random
import string
import sys
import constants
import signal
from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import connectWS
from autobahn.wamp1.protocol import WampClientFactory, \
                                    WampClientProtocol


def generate_random_data(size=30, chars=string.ascii_letters + string.digits):
   """Generates a random string"""
   return ''.join(random.choice(chars) for _ in range(size))

registry_address = "" 
available_sensors = ""
lat = ""
lng = ""
producer_id = generate_random_data() # 30 characters, letters + digits
heartbeats_skipped = 0

def signal_handler(signal, frame):

   reactor.stop()
   sys.exit(0)

def advertise_availability():
   """Declare location and available sensors to registry"""
   payload = {'producer_id' : producer_id, 'sensors': available_sensors, 'lat' : lat, 'lng' : lng}
   global heartbeats_skipped
   try:
      req = requests.get(registry_address+"/register_producer", params=payload)
      response_json = req.text
      response = json.loads(response_json)
      time.sleep(1) # give time for broker to initialise
      heartbeats_skipped = 0
      # print "Heartbeat"
      return response["broker_address"]
   except:
      # print "Heartbeat skipped"
      heartbeats_skipped += 1
      if heartbeats_skipped > constants.MAX_HEARTBEATS_SKIPPED:
         print heartbeats_skipped + " heartbeats skipped. Exiting..."
         sys.exit()

class MyProducerFactory(WampClientFactory):
   """Factory class for the producer"""
   def clientConnectionLost(self, connector, reason):
      print "Broker dead. Re-initialising producer with registry"
      try:
         replace_broker()
      except:
         reactor.stop()
         exit(0)


class ProducerPubSubProtocol(WampClientProtocol):
   """Protocol class for the producer"""   
   def onSessionOpen(self):

      def onMyEvent1(topic, event):
         print "Received event", topic, event

      def heartbeat():
         advertise_availability()
         reactor.callLater(constants.HEARTBEAT_RATE, heartbeat)

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

      print "Connected!"
      self.counter = 0
      heartbeat()

      for sensor in sensors:
         self.subscribe(sensor, onMyEvent1)
         start_publishing_sensor(sensor, constants.PUBLISHING_INTERVAL, lat, lng)

def replace_broker():
   payload = {'producer_id' : producer_id}
   try:
      req = requests.get(registry_address+"/replace_broker", params=payload)
      response_json = req.text
      response = json.loads(response_json)
      time.sleep(1) # give time for the broker to initialise
      initialise_broker(response["broker_address"])
   except:
      print "Registry connectivity error - Unable to receive new broker"
      sys.exit()

def initialise_broker(socket_address):
   print "Connecting to", socket_address
   factory = MyProducerFactory(socket_address, debugWamp = False)
   factory.protocol = ProducerPubSubProtocol
   connectWS(factory)

if __name__ == '__main__':
   log.startLogging(sys.stdout)
   signal.signal(signal.SIGINT, signal_handler) 

   # Deal with command line arguments
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


   # Set up websocket connection with registry
   wsuri = advertise_availability()
   initialise_broker(wsuri) 

   reactor.run()