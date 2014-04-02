There are three runnables:
* registry.py
* producer.py
* consumer.py

==============
BEFORE RUNNING
==============
The following Python libraries are required:
* requests - simplifies HTTP requests, used in Flask
* flask - offers straightforward web routing, useful for REST
* twisted - server framework
* autobahn - based on twisted, offers basic PubSub and RPC functionality
* geopy - used for geographical distance calculations

All should be available via pip:
pip install requests
pip install flask
pip install twisted
pip install autobahn
pip install geopy


==============
TO RUN/ARGUMENTS
==============
registry.py
=----------=
-r   			: flag which, if present, indicates registry should save producer list
-p <port-no>    : port number to listen on
-a <address>	: address to run registry on (e.g. 127.0.0.1)

python registry.py -r -p 5000 -a 127.0.0.1

=====
producer.py
=----------=
-r <address>	: address of registry to advertise to
-s <sen1,sen2..>: comma-separated list of sensors available
-x <co-ords>	: latitude of location
-y <co-ords>	: longitude of location

python producer.py -r http://127.0.0.1:5000 -s camera,microphone,location -x 55.76 -y 37.62

=====
consumer.py
=----------=
-r <address>	: address of registry to request brokers from
-s <sen1,sen2..>: comma-separated list of sensors required
-x <co-ords>	: latitude of location wanted
-y <co-ords>	: longitude of location wanted
-d <radius>		: maximum acceptable distance from location
-o <filename>	: file to output data to

python consumer.py -r http://127.0.0.1:5000 -s camera,microphone,location -x 55.76 -y 37.62 -d 10 -b 5 -o example_file