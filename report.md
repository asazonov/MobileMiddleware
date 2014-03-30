Service-oriented middleware for mobile sensing
=================

# Goals

It was decided that a producer must send the data only to one source. Implementing data broadcasting through the producer would not be acceptable, since mobile devices are often limited in bandwidth. 

# Design

## Components
### Registry
### Broker
### Producer
### Consumer

# Implementation

## Key technologies

As described in the brief, the sensor data producer is deployed on a mobile device. This dictated a number of constraints that had to be considered while developing the system.

The technologies used to develop the producer had to be easy to deploy on a mobile device. In recent years, it has become increasingly popular to develop mobile web apps – applications that use device's browser as the execution environment. Such applications have an advantage of being easy to distribute and deploy on various platforms. HTML5 and Javascript, used to develop web apps, provide rich APIs for accessing sensor data – accelerometers, audio, video, etc. Thus, the project aimed to utilise technologies that are supported by browsers of modern mobile platforms. 

### WebSockets and WAMP
### REST

## Components
### Registry
### Broker
### Producer
### Consumer

# Testing
 
# Reproducing tests

# Future work

# Conclusion
