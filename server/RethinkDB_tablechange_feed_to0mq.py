# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 14:00:05 2015

Realtime Feed from RethinkDB

@author: alex barry
"""

import rethinkdb as r
import sys
import zmq
import logging
import json

#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#

#Accept input parameters for DB Name, Port #, table name, 0mq socket, log file, and log level
if len(sys.argv) == 1:
    print("Input Parameters:")
    print("DB Path: Path to the database information folder")
    print("Port #: the Port number for the database")
    print("Table Name: The table name to watch")
    print("0MQ Socket: The 0mq socket to connect to")
    print("Log File: The file name to write the logs out to")
    print("Log Level: Debug, Info, Warning, Error")
    print("Example: python3 tablechange_feed_to0mq.py localhost 28015 objects tcp://localhost:5555 tablechange_feed.log Debug")
elif len(sys.argv) != 7:
    
    print("Wrong number of Input Parameters")
    
else:

    print("Input Parameters:")
    print("DB Path: %s" % (sys.argv[1]))
    print("Port #: %s" % (sys.argv[2]))
    print("Table Name: %s" % (sys.argv[3]))
    print("0MQ Socket: %s" % (sys.argv[4]))
    print("Log File: %s" % (sys.argv[5]))
    print("Log Level: %s" % (sys.argv[6]))
    
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
    
    #Set up the file logging config
    if sys.argv[6] == 'Debug':
        logging.basicConfig(filename=sys.argv[5], level=logging.DEBUG)
    elif sys.argv[6] == 'Info':
        logging.basicConfig(filename=sys.argv[5], level=logging.INFO)
    elif sys.argv[6] == 'Warning':
        logging.basicConfig(filename=sys.argv[5], level=logging.WARNING)
    elif sys.argv[6] == 'Error':
        logging.basicConfig(filename=sys.argv[5], level=logging.ERROR)
    else:
        print("Log level not set to one of the given options, defaulting to debug level")
        logging.basicConfig(filename=sys.argv[5], level=logging.DEBUG)
        
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
    
    #Establish the 0mq context
    context = zmq.Context()
    
    #Connect to the 0mq Queue
    socket = context.socket(zmq.REQ)
    socket.connect(sys.argv[4])

    #Connect to the RethinkDB
    r.connect(sys.argv[1], int(float(sys.argv[2]))).repl()
    
    #Connect to a realtime feed on table changes for the DB
    cursor = r.table(sys.argv[3]).changes().run()
    
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
    
    #The cursor is infinite so the process will sit and wait on changes,
    for document in cursor:
        
        try:
            #When a change occurs, send the change out to the 0mq queue
            message = json.dumps(document)
            socket.send_string(message)
            
            #Recieve the response 
            resp = socket.recv()
            
            #Log the response message to the log file
            if str(resp) == "b'Success'":
                logging.warning('Message sent successfully')
                logging.debug('%s' % (document))
            else:
                logging.warning('Message sent to destination with failure response')
                logging.error('%s' % (document))
                
        #If an exception is thrown while sending the message,
        #write that out to the log file
        except Exception as e:
            logging.error('Exception while sending document')
            logging.error('%s' % (document))
            logging.error(e)