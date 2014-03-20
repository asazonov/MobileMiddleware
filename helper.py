from __future__ import print_function
import os
import sys
import socket
import subprocess

def pick_unused_port():
    # adapted from http://code.activestate.com/recipes/531822-pick-unused-port/history/1/
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    addr, port = s.getsockname()
    s.close()
    return port

def spawn_daemon(cmd):
	# adapted from http://stackoverflow.com/questions/6011235/run-a-program-from-python-and-have-it-continue-to-run-after-the-script-is-kille
    try: 
        pid = os.fork() 
        if pid > 0:
            # parent process, return and keep running
            return
    except OSError, e:
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1)

    os.setsid()

    # do second fork
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit from second parent
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1)

    # do stuff
    subprocess.Popen(cmd)

    # all done
    os._exit(os.EX_OK)
