import subprocess
import time 


def test_broker_scalability(upper_bound):
    p1 = subprocess.Popen(['python', 'registry.py'])
    time.sleep(5) # Give time for the registry to start
    p2 = subprocess.Popen(['python', 'producer.py', '-r', 'http://127.0.0.1:5000', '-s', 'camera,microphone,location', '--lat', '51.755826', '--lng', '37.6173']) 
    time.sleep(5) # Give time for the producer to register

    for x in range(0, upper_bound):
    	subprocess.Popen(['python', 'client.py', '-r', 'http://127.0.0.1:5000', '-p' 'Warsaw', '-c' 'camera,microphone,location'])
    	time.sleep(2)
    exit_codes = [p.wait() for p in p1, p2]


def main():
	test_broker_scalability(100)


if  __name__ =='__main__':main()
