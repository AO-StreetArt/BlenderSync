# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 14:35:08 2015

An in-memory 0mq Queue to hold messages

@author: alex
"""

import zmq
import sys
import logging

try:
    from Queue import Queue
except:
    from queue import Queue
    
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
    
if len(sys.argv) == 1:
    
    print("Input Parameters:")
    print("0MQ Socket: The 0mq socket to expose")
    print("Log File: The file name to write the logs out to")
    print("Log Level: Debug, Info, Warning, Error")
    print("Example: python3 0mq_Q.py tcp://*:5555 0mq_Q.log Debug")
    
elif len(sys.argv) != 4:
    
    print("Wrong number of Input Parameters")
    
else:

    print("Input Parameters:")
    print("0MQ Socket: %s" % (sys.argv[1]))
    print("Log File: %s" % (sys.argv[2]))
    print("Log Level: %s" % (sys.argv[3]))
    
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
        
    #Set up the file logging config
    if sys.argv[3] == 'Debug':
        logging.basicConfig(filename=sys.argv[2], level=logging.DEBUG)
    elif sys.argv[3] == 'Info':
        logging.basicConfig(filename=sys.argv[2], level=logging.INFO)
    elif sys.argv[3] == 'Warning':
        logging.basicConfig(filename=sys.argv[2], level=logging.WARNING)
    elif sys.argv[3] == 'Error':
        logging.basicConfig(filename=sys.argv[2], level=logging.ERROR)
    else:
        print("Log level not set to one of the given options, defaulting to debug level")
        logging.basicConfig(filename=sys.argv[2], level=logging.DEBUG)
        
    #-----------------------------------------------------------------------------#
    #-----------------------------------------------------------------------------#
    
    #Expose the 0MQ Socket
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(sys.argv[1])
    
    #Create the internal queue
    int_queue = Queue(maxsize=0)
    
    #-----------------------------------------------------------------------------#
    #-----------------------------------------------------------------------------#
    
    while True:
        #  Wait for next request from client
        message = socket.recv()
        logging.debug("Received request: %s" % message)
        
        #If the message recieved is a get message, pop the top value off the queue
        #and send it back as the response
        if str(message) == "b'Get'":
            #Get the next value from the queue
            if int_queue.empty() == False:
                resp = int_queue.get()
                logging.debug('Message Taken from queue successfully:')
                logging.debug(resp)
                socket.send(resp)
                int_queue.task_done()
            else:
                logging.debug('Get called against empty queue')
                socket.send(b"Empty")
        else:
            try:
                #  Put the message to the Queue
                int_queue.put(message)
                
                #Write the message to the log
                logging.debug('Message written to internal queue successfully:')
                logging.debug(message)
            
                #  Send reply back to client
                socket.send(b"Success")
            except Exception as e:
                socket.send(b"Failure")
                logging.error(e)