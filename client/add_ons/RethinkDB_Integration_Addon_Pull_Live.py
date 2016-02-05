# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 23:26:37 2015

Blender Add-On to allow pulling and pushing information to a RethinkDB via
0MQ Queues as intermediaries

@author: alex
"""

bl_info = {
    "name": "Blender_Sync_Pull", 
    "author": "Alex Barry",
    "version": (0, 0, 1),
    "blender": (2, 76, 2),
    "description": "Blender Sync Add-on to sync multiple instances of blender via RethinkDB and 0MQ",
    "category": "Object",
}

import bpy
import zmq
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

class UpdateFromDatabase(bpy.types.Operator):
    bl_idname = "object.update_from_db"
    bl_label = "Activate Object Updates from RethinkDB"
    bl_options = {'REGISTER'}
    socket = bpy.props.StringProperty(name="Inbound 0MQ Socket", default="tcp://localhost:5556")
    
    def execute(self, context):
        
        #Called by blender when the addon is run
        
        #Set up the Background Scheduler
        scheduler = BackgroundScheduler()
        interv = IntervalTrigger(seconds=3)
        scheduler.add_job(self.update_objects, interv)
        scheduler.start()
        
        #Let's blender know the operator is finished
        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
    def update_objects(self):
        #Connect to 0MQ
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.socket)
        #Pull all of the data down from the queue
        resp = ""
        while str(resp) != "b'Empty'":
            print("Sending request")
            socket.send(b"Get")
            
            #Get the reply
            resp = str(socket.recv())
            
            #Write the changes to the scene
            
            if resp != "b'Empty'":
            
                #Remove the first two and last digit from the message string
                #This is simply added because of all the passing through 0MQ instances
                fixed_resp = resp[2:]
                fixed_resp = fixed_resp[:-1]
                
                #Load the JSON Object
                json_response = json.loads(fixed_resp)
                
                #TODO: If json_response['old_value'] is null, call the appropriate
                #Operator from blender to add the object to the scene
                if json_response['old_val'] is None:
                    #Pull the new value attribute from the message
                    new_value = json_response['new_val']
                    new_name = new_value['name']
                    new_type = new_value['type']
                    new_subtype = new_value['subtype']
                    
                    if str(new_subtype) == "Cube":
                        #Call the cube operator
                        print('Creating new cube from DB')
                        bpy.ops.mesh.primitive_cube_add(radius=1, view_align=False, location=(0.0, 0.0, 0.0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                    
                    elif str(new_subtype) == "Plane":
                        #Call the plane operator
                        print('Creating new plane from DB')
                        bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, location=(0.0, 0.0, 0.0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
                    
                    elif str(new_subtype) == "Circle":
                        #Call the circle operator
                        print('Creating new circle from DB')
                        bpy.ops.mesh.primitive_circle_add(radius=1, view_align=False, location=(0.0, 0.0, 0.0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

                    elif str(new_subtype) == "UV Sphere":
                        #Call the uv sphere operator
                        print('Creating new UV Sphere from DB')
                        bpy.ops.mesh.primitive_uv_sphere_add(size=1, view_align=False, location=(0.0, 0.0, 0.0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

                    elif str(new_subtype) == "Icosphere":
                        #Call the icosphere operator
                        print('Creating new icosphere from DB')
                        bpy.ops.mesh.primitive_icosphere_add(size=1, view_align=False, location=(0.0, 0.0, 0.0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

                    elif str(new_subtype) == "Cylinder":
                        #Call the circle operator
                        print('Creating new cylinder from DB')
                        bpy.ops.mesh.primitive_cylinder_add(radius=1, depth2, view_align=False, location=(0.0, 0.0, 0.0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

                    elif str(new_subtype) == "Cone":
                        #Call the uv sphere operator
                        print('Creating new Cone from DB')
                        bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2, view_align=False, location=(0.0, 0.0, 0.0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

                    elif str(new_subtype) == "Custom":
                        #Call the add custom mesh flow
                        print('Creating new Cone from DB')
                    else:
                        #Unrecognized Mesh type
                        print('Unrecognized Mesh type')
                        
                    #Find the new object and assign the DB Name to it
                    obj_list = []
                    for obj in obj_list:
                        match = False
                        if obj.name == str(new_name):
                            match = True
                        if match == False:
                            obj_list.append(obj)
                            
                    if len(obj_list) == 0:
                        #No new objects found
                        print('Names all match')
                    if len(obj_list) > 1:
                        #More than one new object has been added, bad news bears
                        print('More than one new object has been added, bad news bears')
                        for obj in obj_list:
                            print(str(obj.name))
                    elif len(obj_list) == 1:
                        #Assign the DB Name to the object
                        print('DB Name assigned correctly')
                        obj_list[0].name = new_name
                        
                #If the old value is not null, then we have an update message to be applied
                else:
                    #Pull the new value attribute from the message
                    new_value = json_response['new_val']
                    
                    #Pull the new attributes from the json message
                    new_loc = new_value['location']
                    new_rot_euler = new_value['rotation_euler']
                    new_rot_quaternion = new_value['rotation_quaternion']
                    new_scale = new_value['scale']
                    new_name = new_value['name']
                    new_type = new_value['type']
                    
                    #Assign the new data
                    bpy.data.objects[new_name].location.x = new_loc['x']
                    bpy.data.objects[new_name].location.y = new_loc['y']
                    bpy.data.objects[new_name].location.z = new_loc['z']
                    
                    bpy.data.objects[new_name].rotation_euler.x = new_rot_euler['x']
                    bpy.data.objects[new_name].rotation_euler.y = new_rot_euler['y']
                    bpy.data.objects[new_name].rotation_euler.z = new_rot_euler['z']
                    
                    bpy.data.objects[new_name].rotation_quaternion.w = new_rot_quaternion['a']
                    bpy.data.objects[new_name].rotation_quaternion.x = new_rot_quaternion['b']
                    bpy.data.objects[new_name].rotation_quaternion.y = new_rot_quaternion['c']
                    bpy.data.objects[new_name].rotation_quaternion.z = new_rot_quaternion['d']
                    
                    bpy.data.objects[new_name].scale.x = new_scale['x']
                    bpy.data.objects[new_name].scale.y = new_scale['y']
                    bpy.data.objects[new_name].scale.z = new_scale['z']
        
def menu_func(self, context):
    self.layout.operator(UpdateFromDatabase.bl_idname)
        
def register():
    bpy.utils.register_class(UpdateFromDatabase)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    
def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(UpdateFromDatabase)
    
if __name__ == "__main__":
    register()