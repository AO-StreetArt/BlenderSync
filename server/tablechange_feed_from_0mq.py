# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 16:41:43 2015

0MQ Client to write objects from a 0MQ Queue to a RethinkDB Object Document
We read a single inbound queue and
We accept input parameters for the outbound RethinkDB name and port, the log file
and level, and the configuration xml file

@author: alex
"""

import sys
import json
import zmq
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import rethinkdb as r
try:
    from Queue import Queue
except:
    from queue import Queue
    
def update_db():
    logging.debug('Update Database Called')
    #Pull all of the values off the queue and update the DB with them
    if len(sys.argv) > 2:
        #Connect to the RethinkDB
        r.connect(sys.argv[1], int(float(sys.argv[2]))).repl()
        while int_queue.empty() == False:
                
            #Retrieve the top value from the queue
            data = int_queue.get()
            resp = str(data)
            
            logging.debug('Message pulled off queue')
            logging.debug('%s' % (data))
            
            #Remove the first two and last digit from the message string
            #This is simply added because of all the passing through 0MQ instances
            fixed_resp = resp[2:]
            fixed_resp = fixed_resp[:-1]
            
            #Load the JSON Message
            json_response = json.loads(fixed_resp)
            
            if json_response['msg_type'] == "Update":
            
                #Pull the data from the json message
                loc = json_response['location']
                loc_x = loc['x']
                loc_y = loc['y']
                loc_z = loc['z']
                
                rote = json_response['rotation_euler']
                rote_x = rote['x']
                rote_y = rote['y']
                rote_z = rote['z']
                
                rotq = json_response['rotation_quaternion']
                rotq_w = rotq['a']
                rotq_x = rotq['b']
                rotq_y = rotq['c']
                rotq_z = rotq['d']
                
                sc = json_response['scale']
                sc_x = sc['x']
                sc_y = sc['y']
                sc_z = sc['z']
                
                #Update the DB with the values from the message
                r.table("objects").filter(r.row['name'] == json_response['name']).update({"location": {"x": loc_x, "y": loc_y, "z": loc_z}}).run()
                r.table("objects").filter(r.row['name'] == json_response['name']).update({"rotation_euler": {"x": rote_x, "y": rote_y, "z": rote_z}}).run()
                r.table("objects").filter(r.row['name'] == json_response['name']).update({"rotation_quaternion": {"a": rotq_w, "b": rotq_x, "c": rotq_y, "d": rotq_z}}).run()
                r.table("objects").filter(r.row['name'] == json_response['name']).update({"scale": {"x": sc_x, "y": sc_y, "z": sc_z}}).run()
                logging.debug('Message successfully written to DB')
            
            elif json_response['msg_type'] == "Create":
                #Find the names already in the db
                cur = r.table('objects').pluck('name').run()
                
                new_name = json_response['name']
                match = True
                
                #Compare the name in the operator property to the names from the db
                while match == True:
                    match = False
                    for name in cur:
                        if json_response['name'] == str(name):
                            new_name ="name%s" % ("_c")
                            match = True
                        
                #Insert a record into the DB
                r.table("objects").insert({"name": new_name,"type": json_response['type'],"subtype": json_response['subtype'],"location": {"x": 0.0, "y": 0.0, "z": 0.0},"rotation_euler": {"x": 0.0, "y": 0.0, "z": 0.0},"rotation_quaternion": {"a": 0.0, "b": 0.0, "c": 0.0, "d": 0.0},"scale": {"x": 0.0, "y": 0.0, "z": 0.0}}).run()
              
                logging.debug('Message successfully written to DB')

#Handle the input parameters
if len(sys.argv) == 1:
    print("Input Parameters:")
    print("DB Path: Path to the database information folder")
    print("Port #: the Port number for the database")
    print("0MQ Inbound Queue: 0MQ Socket to read data from")
    print("Log File: The file name to write the logs out to")
    print("Log Level: Debug, Info, Warning, Error")
    print("Example: python3 tablechange_feed_from_0mq.py localhost 28015 tcp://*:5557 tablechange_feed.log Debug")
elif len(sys.argv) != 6:
    
    print("Wrong number of Input Parameters")
    
else:

    print("Input Parameters:")
    print("DB Path: %s" % (sys.argv[1]))
    print("Port #: %s" % (sys.argv[2]))
    print("0MQ Socket: %s" % (sys.argv[3]))
    print("Log File: %s" % (sys.argv[4]))
    print("Log Level: %s" % (sys.argv[5]))
    
    #Set up the file logging config
    if sys.argv[5] == 'Debug':
        logging.basicConfig(filename=sys.argv[4], level=logging.DEBUG)
    elif sys.argv[5] == 'Info':
        logging.basicConfig(filename=sys.argv[4], level=logging.INFO)
    elif sys.argv[5] == 'Warning':
        logging.basicConfig(filename=sys.argv[4], level=logging.WARNING)
    elif sys.argv[5] == 'Error':
        logging.basicConfig(filename=sys.argv[4], level=logging.ERROR)
    else:
        print("Log level not set to one of the given options, defaulting to debug level")
        logging.basicConfig(filename=sys.argv[4], level=logging.DEBUG)
        
    #Expose the 0MQ Socket
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(sys.argv[3])
    
    #Create the internal queue
    int_queue = Queue(maxsize=0)
    
    #Set up the Background Scheduler
    scheduler = BackgroundScheduler()
    interv = IntervalTrigger(seconds=2)
    scheduler.add_job(update_db, interv)
    scheduler.start()
    
    while True:
        #  Wait for next request from client
        message = socket.recv()
        logging.debug("Received request: %s" % message)
        
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