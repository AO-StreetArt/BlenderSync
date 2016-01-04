# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 23:26:37 2015

Blender Add-On to allow pulling and pushing information to a RethinkDB via
0MQ Queues as intermediaries

@author: alex
"""

bl_info = {
    "name": "Blender_Sync_Push", 
    "author": "Alex Barry",
    "version": (0, 0, 1),
    "blender": (2, 76, 2),
    "description": "Blender Sync Add-on to sync multiple instances of blender via RethinkDB and 0MQ",
    "category": "Object",
}

import bpy
import rethinkdb as r
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import zmq

#Utility Methods
def euclidean_distance_3d(x1, y1, z1, x2, y2, z2):
    return (((x2 - x1) ** 2) + ((y2 - y1) ** 2) + ((z2 - z1) ** 2)) ** 0.5
    
def euclidean_distance_4d(w1, x1, y1, z1, w2, x2, y2, z2):
    return (((w2 - w1) ** 2) + ((x2 - x1) ** 2) + ((y2 - y1) ** 2) + ((z2 - z1) ** 2)) ** 0.5

class LastMsgData():
    loc = [0.0, 0.0, 0.0]
    rote = [0.0, 0.0, 0.0]
    rotq = [0.0, 0.0, 0.0, 0.0]
    scale = [0.0, 0.0, 0.0]
    
class MsgData():
    msg_data_list = {}

class UpdateToDatabase(bpy.types.Operator):
    bl_idname = "object.update_to_db"
    bl_label = "Activate Live Object Updates to RethinkDB"
    bl_options = {'REGISTER'}
    sock = bpy.props.StringProperty(name="Outbound 0MQ Socket", default="tcp://localhost:5557")
    
    def execute(self, context):
        
        #Called by blender when the addon is run
        
        #Set up the Background Scheduler
        scheduler = BackgroundScheduler()
        interv = IntervalTrigger(seconds=3)
        scheduler.add_job(self.send_object_updates, interv)
        scheduler.start()

        #Let's blender know the operator is finished
        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
    def send_object_updates(self):
        #Connect to 0MQ
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.sock)

        for obj in bpy.data.objects:
            if obj.name in bpy.context.scene.msg_data.msg_data_list:
                last_msg = bpy.context.scene.msg_data.msg_data_list[obj.name]
            else:
                bpy.context.scene.msg_data.msg_data_list[obj.name] = LastMsgData()
                last_msg = bpy.context.scene.msg_data.msg_data_list[obj.name]
            last_loc = last_msg.loc
            last_rote = last_msg.rote
            last_rotq = last_msg.rotq
            last_scale = last_msg.scale
            
            loc_x = obj.location.x
            loc_y = obj.location.y
            loc_z = obj.location.z
            
            rote_x = obj.rotation_euler.x
            rote_y = obj.rotation_euler.y
            rote_z = obj.rotation_euler.z
            
            rotq_w = obj.rotation_quaternion.w
            rotq_x = obj.rotation_quaternion.x
            rotq_y = obj.rotation_quaternion.y
            rotq_z = obj.rotation_quaternion.z
            
            sc_x = obj.scale.x
            sc_y = obj.scale.y
            sc_z = obj.scale.z
            
            if euclidean_distance_3d(last_loc[0], last_loc[1], last_loc[2], loc_x, loc_y, loc_z) < 0.01 or\
                euclidean_distance_3d(last_rote[0], last_rote[1], last_rote[2], rote_x, rote_y, rote_z) < 0.01 or\
                    euclidean_distance_4d(last_rotq[0], last_rotq[1], last_rotq[2], last_rotq[3], rotq_w, rotq_x, rotq_y, rotq_z) < 0.01 or\
                        euclidean_distance_3d(last_scale[0], last_scale[1], last_scale[2], sc_x, sc_y, sc_z) < 0.01:
            
#            if last_loc[0] != loc_x or last_loc[1] != loc_y or last_loc[2] != loc_z or last_rote[0] != rote_x or\
#                last_rote[0] != rote_x or last_rote[1] != rote_y or last_rote[2] != rote_z or last_rotq[0] != rotq_w or\
#                    last_rotq[1] != rotq_x or last_rotq[2] != rotq_y or last_rotq[3] != rotq_z or last_scale[0] != sc_x or\
#                        last_scale[1] != sc_y or last_scale[2] != sc_z:
            
                #Wrap the values in a json message and send it to the Outbound Queue
                msg = '{"msg_type": "Update", "name": "%s","type": "%s","location": {"x": %s, "y": %s, "z": %s},"rotation_euler": {"x": %s, "y": %s, "z": %s}\
                    ,"rotation_quaternion": {"a": %s, "b": %s, "c": %s, "d": %s},"scale": {"x": %s, "y": %s, "z": %s}}'\
                        % (obj.name, obj.type, loc_x, loc_y, loc_z, rote_x, rote_y, rote_z, rotq_w, rotq_x, rotq_y, rotq_z, sc_x, sc_y, sc_z)
                        
                socket.send_string(msg)
                
                #  Wait for response from the server
                message = socket.recv()
                print("Received response: %s" % message)
                
                #Set the last message values
                bpy.context.scene.msg_data.msg_data_list[obj.name].loc[0] = loc_x 
                bpy.context.scene.msg_data.msg_data_list[obj.name].loc[1] = loc_y 
                bpy.context.scene.msg_data.msg_data_list[obj.name].loc[2] = loc_z 
                
                bpy.context.scene.msg_data.msg_data_list[obj.name].rote[0] = rote_x 
                bpy.context.scene.msg_data.msg_data_list[obj.name].rote[1] = rote_y 
                bpy.context.scene.msg_data.msg_data_list[obj.name].rote[2] = rote_z 
                
                bpy.context.scene.msg_data.msg_data_list[obj.name].rotq[0] = rotq_w 
                bpy.context.scene.msg_data.msg_data_list[obj.name].rotq[1] = rotq_x
                bpy.context.scene.msg_data.msg_data_list[obj.name].rotq[2] = rotq_y
                bpy.context.scene.msg_data.msg_data_list[obj.name].rotq[3] = rotq_z
                
                bpy.context.scene.msg_data.msg_data_list[obj.name].scale[0] = sc_x
                bpy.context.scene.msg_data.msg_data_list[obj.name].scale[1] = sc_y
                bpy.context.scene.msg_data.msg_data_list[obj.name].scale[2] = sc_z
        
def menu_func(self, context):
    self.layout.operator(UpdateToDatabase.bl_idname)        
        
def register():
    bpy.utils.register_class(UpdateToDatabase)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    bpy.types.Scene.msg_data = MsgData()
    
def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(UpdateToDatabase)
    del bpy.types.Scene.msg_data
    
if __name__ == "__main__":
    register()