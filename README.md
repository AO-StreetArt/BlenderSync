#Welcome to BlenderSync

BlenderSync is a set of tools allowing for real-time integration of multiple [Blender](http://www.blender.org) instances across a network.

It is built on RethinkDB, a NoSQL Database Server, with 0MQ for inter-process communication.

The main idea is to stand up message queue's which Blender can query, which are always up-to-date with changelogs coming out of the database.  Each instance of blender gets a changestream (a RethinkDB concept) and a message queue to read from.  Each blender instances also gets an outbound queue to write changes to.  Instead of operations directly making updates to the blender instances, they simply wrap the desired changes into a JSON message and pass this to the outbound message queue.  This queue pulls the messages off independently and writes to the DB based on these JSON documents.  The database generates JSON messages out to any queue's subscribed to a changestream, which are then picked up by all connected blender instances and updated simultaneously.

##Current Features

Please note that BlenderSync is still highly experimental and, as such, the feature set is currently quite limited.  However, a solid framework has been built to quickly add many new operations to the feature set.

* Synchronize Location, Rotation, and Scale across all active in the scene which are entered into the DB manually
* Add a mesh cube to the DB from a Blender Instance

#Install
BlenderSync is not a single application, rather it is a pre-built (but not configured) Database Server with a set of python scripts to be executed independently, as well as a collection of [Blender](http://www.blender.org) Add-Ons.  The downside to this is that install is somewhat difficult. 

##RethinkDB
Follow the instructions [here](http://www.rethinkdb.com/docs/install/).  Note that the RethinkDB instance will be running locally in test cases, but in the 'ideal' production scenario, the rethinkdb would have it's own dedicated server.

You can execute the included seed script to configure the DB (once RethinkDB is installed and an instance is running.  Note that this assumes it's connecting through localhost, so if you want to run the seed script remotely it might take some tweaking)

```
$python3 Blender_BaseScene.py
```

##Python Dependencies
```
(sudo) pip install zmq
(sudo) pip install apscheduler
(sudo) pip install rethinkdb
```

Use Sudo at your own discretion.

##Blender
###Set up Blender's Python Instance
Using BlenderSync requires installing 0MQ into Blender's Python.  This can be done in a number of ways:

* Follow the instructions [here](http://www.blender.org/api/blender_python_api_2_63_release/info_tips_and_tricks.html) to push blender to fallback to the system python.  This is the recommended solution

* Alternatively, you can manually move 0MQ & APScheduler and their dependecies to your system python.  Follow the instructions in the Python Dependencies section, and then manually copy all of the output files into the blender python/lib directory.

Note: The following files had to be copied directly into blender python/lib from system python libraries for APScheduler to function correctly.

  * six.py
  * pkg_resources.py

###Install the Addons
* Start up an instance of blender and install the addons in the addons folder into blender

Note: This requires that 0MQ is installed into the blender python

* Enable both addons.  This enables two commands which can be accessed via spacebar searching for 'rethink' to automatically push and pull updates from the db.  Please remember that your queues should be on and connected prior to running these commands to turn the updates on.

#Usage
##Local
* Start RethinkDB Server

```
$rethinkdb
```

* If necessary, create the base objects in the table using the Blender_BaseScene.py file

```
$python3 Blender_BaseScene.py
```

* Start the 0MQ Queue

```
$python3 0mq_Q.py tcp://*:5555 0mq_Q.log Debug
```

* Start the Outbound DB Feed

```
$python3 tablechange_feed_to0mq.py localhost 28015 objects tcp://localhost:5555 tablechange_feed.log Debug
```

* Start the Inbound DB Feed

```
$python3 tablechange_feed_from_0mq.py localhost 28015 tcp://*:5557 tablechange_feed_in.log Debug
```

* Another instance of the 0MQ Queue and the Outbound DB Feed can be started on port 5556.  

* Start two independent instances of blender.  Use the spacebar search to find 'rethink', and you will find both commands to start automated updates from a particular set of 0MQ Queues.  Each instance of blender should connect to it's own 0MQ Queue ('Enable Updates from RethinkDB'), but all instances of blender can connect to the same Inbound DB Feed ('Enable Automatic Updates to RethinkDB') or different ones, it's up to you.

* Update one blender instance, and the update will be shown (potentially after a slight delay) on both screens

##Remote
BlenderSync has yet to be tested across a network, but all of the communications protocols utilized allow for network communication
