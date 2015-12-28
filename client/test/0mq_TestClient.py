# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 16:03:16 2015

A test client to connect to a 0mq socket and pull data

@author: alex
"""

import zmq
import sys
import json

if len(sys.argv) == 1:
    
    print("Input Parameters:")
    print("0MQ Socket: The 0mq socket to connect to")
    print("Example: python3 0mq_TestClient.py tcp://localhost:5555")
    
elif len(sys.argv) != 2:
    
    print("Wrong number of Input Parameters")
    
else:

    print("Input Parameters:")
    print("0MQ Socket: %s" % (sys.argv[1]))

    context = zmq.Context()
    
    #  Socket to talk to server
    print("Connecting to Queue")
    socket = context.socket(zmq.REQ)
    socket.connect(sys.argv[1])
    
    #Pull all of the data down from the queue
    resp = ""
    while str(resp) != "b'Empty'":
        print("Sending request")
        socket.send(b"Get")
        
        #Get the reply
        resp = str(socket.recv())
        
        #Print the reply
        print('%s' % (resp))
        
        if resp != "b'Empty'":
            
            #Remove the first two and last digit from the message string
            #This is simply added because of all the passing through 0MQ instances
            fixed_resp = resp[2:]
            fixed_resp = fixed_resp[:-1]
            
            #Load the JSON Object
            json_response = json.loads(fixed_resp)
            
            #Print the high level json objects
            for obj in json_response:
                print(str(obj))
                
            print(json_response['old_val'])
            
            new_val = json_response['new_val']
            new_val_rot_euler = new_val['rotation_euler']
            print(new_val_rot_euler)
            new_name = new_val['name']
            print(new_name)