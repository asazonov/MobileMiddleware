HEARTBEAT_RATE = 3
HEARTBEAT_RATE_OUTDATED = 10
BROKER_COMMAND = ['nohup','python', "broker.py", "-p" + str(open_port), "-t" + str(open_port2)]