MobileMiddleware
================

Communication is done through HTTP and Websockets. 

* HTTP -- "requests" library and flask framework
* Websockets -- autobahn
* Geopy -- geocoding and distances

All should be available through pip.
(so to recap, install: requests, flask, autobahn, geopy)

20.03 – Alexey:
================


1) Added initial structure to the repository. Autobahn's tutorial code was used for the basic client and server (http://autobahn.ws/python/tutorials/pubsub/).

2) An alpha version of registry was implemented. The registry is a flask-based app (no need for fancy websocket stuff, as far as I can tell). Providers can register themselves. Clients can requests providers. Client-provider communication is done through servers (brokers?). Broker serves info from the provider to multiple clients through WAMP's (http://wamp.ws/) pubsub.

Stuff implemented:
* register_producer -- the producer provides a list of sensors it has (e.g. location, camera, noise) and its location (lat, lng). The lat, lng is matched to a "textual" location (using geocoding). A new server (broker?) is spawned. Server is running as a separate process, but they keep parent-child relationship with the registry (tried to fix this, but it is harder than it seems).
Sample request:

```
http://127.0.0.1:5000/register_producer?sensors=camera,microphone,location&lat=55.755826&lng=37.6173
```

Sample response:

```
{"broker_address": "ws://localhost:62893", "http_port": 62894} # ws -- websocket, ignore the http_port
```

* request_broker -- the client passes a list of sensors and a geographic location it is interested in (e.g. "Moscow, Russia") and receives an address of the broker that is connected to the appropriate provider. The registry prioritizes sensor availability over location. Only providers that have all of the requested sensors are considered. They are later ranked by distance to the requested point. At the moment, all brokers are stored in a global variable.

Sample request:

```
GET http://127.0.0.1:5000/request_broker?broker_param=Erevan
```

The request should be extended to take sensor list as a parameter.

Sample response: 

```
{"broker_address": "ws://localhost:61227", "lat": "51.755826", "lng": "37.6173", "location": "Kursk-Voronezh - Kshenskiy avtodoroga, Kursk Oblast, Russia"}
```

3) The client was extended. Using a GET request it asks the registry for the appropriate broker. The client connects to the broker and subscribes to some of the channels (channel per sensor. Theoretically, pubsub should work.

Run registry:

```
python registry.py
```

Run client:

```
python client.py -r http://127.0.0.1:5000 -p Warsaw -c location, sound # address of the registry, location of interest, sensors (channels) -- currently ignored  
```

There should be no need to run the server individually (the registry should handle this).

Haven't touched the provider code yet. The broker will probably require more work.

28.03 – Alexey:
================


A basic producer was implemented. 

```
python producer.py -r http://127.0.0.1:5000 -s camera,microphone,location --lat 51.755826", --lng 37.6173 
```

The producer advertises its availability to the registry. The registry spawns a broker and returns the broker's address to the producer. Producer connects to the broker and begins publishing. At the moment, it sends dummy messages every two seconds. 

The code was tested -- multiple clients can get the messages from the same subscriber through a single connection. Thus, broadcasting seems to work. 

29.03 – Alexey:
================

Dummy data generator for producer. Producer now publishes data to channels corresponding to sensors it has. 


TODO
================

* The producer only publishes to one channel, sending demo data. It should have some protocol for publishing relevant stuff to relevant channels. 
* request_broker in the registry in the Registry has a list of sensors hardwired -- needs a fix. Generally, need to make sure that nothing is hardwired.
* Start handling errors gracefully (e.g. no appropriate producer).
* Start implementing the tests.
* Report is important. Diagrams, justifications, etc. 


