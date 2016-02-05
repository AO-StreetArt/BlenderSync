# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 23:26:37 2015

Blender Add-On to allow adding cubes to a rethinkdb, so that they can be added to 
all connected instances of blender simultaneously

@author: alex
"""

bl_info = {
    "name": "Blender_Sync_Add_Cube", 
    "author": "Alex Barry",
    "version": (0, 0, 1),
    "blender": (2, 76, 2),
    "description": "Blender Sync Add-on to sync multiple instances of blender via RethinkDB and 0MQ",
    "category": "Object",
}

import bpy
import zmq

class AddCubeToRethinkDB(bpy.types.Operator):
    bl_idname = "object.create_rethink_cube"
    bl_label = "Rethink Cube"
    bl_options = {'REGISTER', 'UNDO'}
    soc = bpy.props.StringProperty(name="Outbound 0MQ Socket", default="tcp://localhost:5557")
    name = bpy.props.StringProperty(name="Name", default="Cube")
    
    def execute(self, context):
        
        #Called by blender when the addon is run
        
        #Connect to 0MQ
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.soc)

        loc_x = 0.0
        loc_y = 0.0
        loc_z = 0.0
        
        rote_x = 0.0
        rote_y = 0.0
        rote_z = 0.0
        
        rotq_w = 0.0
        rotq_x = 0.0
        rotq_y = 0.0
        rotq_z = 0.0
        
        sc_x = 1.0
        sc_y = 1.0
        sc_z = 1.0
        
        #Wrap the values in a json message and send it to the Outbound Queue
        msg = '{"msg_type": "Create", "name": "%s","type": "Mesh", "subtype": "Cube","location": {"x": %s, "y": %s, "z": %s},"rotation_euler": {"x": %s, "y": %s, "z": %s},"rotation_quaternion": {"a": %s, "b": %s, "c": %s, "d": %s},"scale": {"x": %s, "y": %s, "z": %s}}' % (self.name, loc_x, loc_y, loc_z, rote_x, rote_y, rote_z, rotq_w, rotq_x, rotq_y, rotq_z, sc_x, sc_y, sc_z)
                
        socket.send_string(msg)
        
        #Let's blender know the operator is finished
        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
class AddPlaneToRethinkDB(bpy.types.Operator):
    bl_idname = "object.create_rethink_plane"
    bl_label = "Rethink Plane"
    bl_options = {'REGISTER', 'UNDO'}
    soc = bpy.props.StringProperty(name="Outbound 0MQ Socket", default="tcp://localhost:5557")
    name = bpy.props.StringProperty(name="Name", default="Plane")
    
    def execute(self, context):
        
        #Called by blender when the addon is run
        
        #Connect to 0MQ
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.soc)

        loc_x = 0.0
        loc_y = 0.0
        loc_z = 0.0
        
        rote_x = 0.0
        rote_y = 0.0
        rote_z = 0.0
        
        rotq_w = 0.0
        rotq_x = 0.0
        rotq_y = 0.0
        rotq_z = 0.0
        
        sc_x = 1.0
        sc_y = 1.0
        sc_z = 1.0
        
        #Wrap the values in a json message and send it to the Outbound Queue
        msg = '{"msg_type": "Create", "name": "%s","type": "Mesh", "subtype": "Plane","location": {"x": %s, "y": %s, "z": %s},"rotation_euler": {"x": %s, "y": %s, "z": %s},"rotation_quaternion": {"a": %s, "b": %s, "c": %s, "d": %s},"scale": {"x": %s, "y": %s, "z": %s}}' % (self.name, loc_x, loc_y, loc_z, rote_x, rote_y, rote_z, rotq_w, rotq_x, rotq_y, rotq_z, sc_x, sc_y, sc_z)
                
        socket.send_string(msg)
        
        #Let's blender know the operator is finished
        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
class AddCircleToRethinkDB(bpy.types.Operator):
    bl_idname = "object.create_rethink_circle"
    bl_label = "Rethink Circle"
    bl_options = {'REGISTER', 'UNDO'}
    soc = bpy.props.StringProperty(name="Outbound 0MQ Socket", default="tcp://localhost:5557")
    name = bpy.props.StringProperty(name="Name", default="Circle")
    
    def execute(self, context):
        
        #Called by blender when the addon is run
        
        #Connect to 0MQ
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.soc)

        loc_x = 0.0
        loc_y = 0.0
        loc_z = 0.0
        
        rote_x = 0.0
        rote_y = 0.0
        rote_z = 0.0
        
        rotq_w = 0.0
        rotq_x = 0.0
        rotq_y = 0.0
        rotq_z = 0.0
        
        sc_x = 1.0
        sc_y = 1.0
        sc_z = 1.0
        
        #Wrap the values in a json message and send it to the Outbound Queue
        msg = '{"msg_type": "Create", "name": "%s","type": "Mesh", "subtype": "Circle","location": {"x": %s, "y": %s, "z": %s},"rotation_euler": {"x": %s, "y": %s, "z": %s},"rotation_quaternion": {"a": %s, "b": %s, "c": %s, "d": %s},"scale": {"x": %s, "y": %s, "z": %s}}' % (self.name, loc_x, loc_y, loc_z, rote_x, rote_y, rote_z, rotq_w, rotq_x, rotq_y, rotq_z, sc_x, sc_y, sc_z)
                
        socket.send_string(msg)
        
        #Let's blender know the operator is finished
        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
class AddIcosphereToRethinkDB(bpy.types.Operator):
    bl_idname = "object.create_rethink_icosphere"
    bl_label = "Rethink Icosphere"
    bl_options = {'REGISTER', 'UNDO'}
    soc = bpy.props.StringProperty(name="Outbound 0MQ Socket", default="tcp://localhost:5557")
    name = bpy.props.StringProperty(name="Name", default="Icosphere")
    
    def execute(self, context):
        
        #Called by blender when the addon is run
        
        #Connect to 0MQ
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.soc)

        loc_x = 0.0
        loc_y = 0.0
        loc_z = 0.0
        
        rote_x = 0.0
        rote_y = 0.0
        rote_z = 0.0
        
        rotq_w = 0.0
        rotq_x = 0.0
        rotq_y = 0.0
        rotq_z = 0.0
        
        sc_x = 1.0
        sc_y = 1.0
        sc_z = 1.0
        
        #Wrap the values in a json message and send it to the Outbound Queue
        msg = '{"msg_type": "Create", "name": "%s","type": "Mesh", "subtype": "Icosphere","location": {"x": %s, "y": %s, "z": %s},"rotation_euler": {"x": %s, "y": %s, "z": %s},"rotation_quaternion": {"a": %s, "b": %s, "c": %s, "d": %s},"scale": {"x": %s, "y": %s, "z": %s}}' % (self.name, loc_x, loc_y, loc_z, rote_x, rote_y, rote_z, rotq_w, rotq_x, rotq_y, rotq_z, sc_x, sc_y, sc_z)
                
        socket.send_string(msg)
        
        #Let's blender know the operator is finished
        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
class AddUVSphereToRethinkDB(bpy.types.Operator):
    bl_idname = "object.create_rethink_uvsphere"
    bl_label = "Rethink UV Sphere"
    bl_options = {'REGISTER', 'UNDO'}
    soc = bpy.props.StringProperty(name="Outbound 0MQ Socket", default="tcp://localhost:5557")
    name = bpy.props.StringProperty(name="Name", default="UV Sphere")
    
    def execute(self, context):
        
        #Called by blender when the addon is run
        
        #Connect to 0MQ
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.soc)

        loc_x = 0.0
        loc_y = 0.0
        loc_z = 0.0
        
        rote_x = 0.0
        rote_y = 0.0
        rote_z = 0.0
        
        rotq_w = 0.0
        rotq_x = 0.0
        rotq_y = 0.0
        rotq_z = 0.0
        
        sc_x = 1.0
        sc_y = 1.0
        sc_z = 1.0
        
        #Wrap the values in a json message and send it to the Outbound Queue
        msg = '{"msg_type": "Create", "name": "%s","type": "Mesh", "subtype": "UVSphere","location": {"x": %s, "y": %s, "z": %s},"rotation_euler": {"x": %s, "y": %s, "z": %s},"rotation_quaternion": {"a": %s, "b": %s, "c": %s, "d": %s},"scale": {"x": %s, "y": %s, "z": %s}}' % (self.name, loc_x, loc_y, loc_z, rote_x, rote_y, rote_z, rotq_w, rotq_x, rotq_y, rotq_z, sc_x, sc_y, sc_z)
                
        socket.send_string(msg)
        
        #Let's blender know the operator is finished
        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
class AddCylinderToRethinkDB(bpy.types.Operator):
    bl_idname = "object.create_rethink_cylinder"
    bl_label = "Rethink Cylinder"
    bl_options = {'REGISTER', 'UNDO'}
    soc = bpy.props.StringProperty(name="Outbound 0MQ Socket", default="tcp://localhost:5557")
    name = bpy.props.StringProperty(name="Name", default="Cylinder")
    
    def execute(self, context):
        
        #Called by blender when the addon is run
        
        #Connect to 0MQ
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.soc)

        loc_x = 0.0
        loc_y = 0.0
        loc_z = 0.0
        
        rote_x = 0.0
        rote_y = 0.0
        rote_z = 0.0
        
        rotq_w = 0.0
        rotq_x = 0.0
        rotq_y = 0.0
        rotq_z = 0.0
        
        sc_x = 1.0
        sc_y = 1.0
        sc_z = 1.0
        
        #Wrap the values in a json message and send it to the Outbound Queue
        msg = '{"msg_type": "Create", "name": "%s","type": "Mesh", "subtype": "Cylinder","location": {"x": %s, "y": %s, "z": %s},"rotation_euler": {"x": %s, "y": %s, "z": %s},"rotation_quaternion": {"a": %s, "b": %s, "c": %s, "d": %s},"scale": {"x": %s, "y": %s, "z": %s}}' % (self.name, loc_x, loc_y, loc_z, rote_x, rote_y, rote_z, rotq_w, rotq_x, rotq_y, rotq_z, sc_x, sc_y, sc_z)
                
        socket.send_string(msg)
        
        #Let's blender know the operator is finished
        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
class AddConeToRethinkDB(bpy.types.Operator):
    bl_idname = "object.create_rethink_cube"
    bl_label = "Rethink Cone"
    bl_options = {'REGISTER', 'UNDO'}
    soc = bpy.props.StringProperty(name="Outbound 0MQ Socket", default="tcp://localhost:5557")
    name = bpy.props.StringProperty(name="Name", default="Cone")
    
    def execute(self, context):
        
        #Called by blender when the addon is run
        
        #Connect to 0MQ
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(self.soc)

        loc_x = 0.0
        loc_y = 0.0
        loc_z = 0.0
        
        rote_x = 0.0
        rote_y = 0.0
        rote_z = 0.0
        
        rotq_w = 0.0
        rotq_x = 0.0
        rotq_y = 0.0
        rotq_z = 0.0
        
        sc_x = 1.0
        sc_y = 1.0
        sc_z = 1.0
        
        #Wrap the values in a json message and send it to the Outbound Queue
        msg = '{"msg_type": "Create", "name": "%s","type": "Mesh", "subtype": "Cone","location": {"x": %s, "y": %s, "z": %s},"rotation_euler": {"x": %s, "y": %s, "z": %s},"rotation_quaternion": {"a": %s, "b": %s, "c": %s, "d": %s},"scale": {"x": %s, "y": %s, "z": %s}}' % (self.name, loc_x, loc_y, loc_z, rote_x, rote_y, rote_z, rotq_w, rotq_x, rotq_y, rotq_z, sc_x, sc_y, sc_z)
                
        socket.send_string(msg)
        
        #Let's blender know the operator is finished
        return {'FINISHED'}
        
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
        
def register():
    bpy.utils.register_class(AddCubeToRethinkDB)
    
def unregister():
    bpy.utils.unregister_class(AddCubeToRethinkDB)
    
if __name__ == "__main__":
    register()