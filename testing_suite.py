import subprocess
import time 
import os
import signal
import argparse

def test_broker_scalability(upper_bound):
    consumer_list = []
    p1 = subprocess.Popen(['python', 'registry.py'])
    time.sleep(5) # Give time for the registry to start
    p2 = subprocess.Popen(['python', 'producer.py', '-r', 'http://127.0.0.1:5000', '-s', 'camera,microphone,location', '--lat', '55.75', '--lng', '37.61']) 
    time.sleep(5) # Give time for the producer to register

    for x in range(upper_bound):
        consumer_list.append(subprocess.Popen(['python', 'consumer.py', '-r', 'http://127.0.0.1:5000', '-x' '55.75', '-y', '37.61', '-d', '500', '--maxbrokers', '1', '-s', 'camera,microphone,location', '-o', str(upper_bound) + '-' + str(x) ]))
        time.sleep(0)


    #exit_codes = [p.wait() for p in p1, p2]

    time.sleep(100) # / (upper_bound / 10))
    for consumer in consumer_list:
    	print "============ kill" 
        os.kill(consumer.pid, signal.SIGKILL)

    os.kill(p2.pid, signal.SIGKILL)    
    p3 = subprocess.Popen(['python', 'consumer.py', '-r', 'http://127.0.0.1:5000', '-x' '55.75', '-y', '37.61', '-d', '500', '--maxbrokers', '1', '-s', 'camera,microphone,location', '-o', str("1") + '-' + str(x) ])

    os.kill(p1.pid, signal.SIGKILL)
    os.kill(p3.pid, signal.SIGKILL)




def main():


    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--scalability', action='store_true')
    parser.add_argument('-t', '--tempinterrupt', action='store_true')
    parser.add_argument('-d', '--removeproducers', action='store_true')
    parser.add_argument('-b', '--replacebrokers', action='store_true')
    parser.add_argument('-r', '--rebuildregistry', action='store_true')

    args = parser.parse_args()

    if (args.scalability):
        consumer_bounds = [  80, 160, 320] # 10, 20, 40 ] # 
        for consumer_bound in consumer_bounds:
            test_broker_scalability(consumer_bound)

    #if (args.tempinterrupt):



    #if (args.removeproducers):
   


    #if (args.replacebrokers):
    


    #if (args.rebuildregistry):








if  __name__ =='__main__':main()
