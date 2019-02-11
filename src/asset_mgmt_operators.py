'''
Copyright (C) 2018 Alex Barry
aostreetart9@gmail.com

Created by Alex Barry

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
from bpy.props import (
            BoolProperty,
            CollectionProperty,
            EnumProperty,
            FloatProperty,
            FloatVectorProperty,
            IntProperty,
            PointerProperty,
            StringProperty
            )
import threading

from ..animation_client.asset_mgmt import save_selected_as_obj_asset, save_scene_as_blend_asset


# Create an Asset by exporting to obj
# This should be called from the 3d view in Object mode
class OBJECT_OT_CreateObjAsset(bpy.types.Operator):
    bl_idname = "object.create_obj_asset"
    bl_label = "Save as obj"
    bl_description = "Export selected objects to an .obj file and save this to Aesel"
    bl_options = {"REGISTER"}
    asset_name: bpy.props.StringProperty(name="Asset Name", default="")
    asset_public: bpy.props.BoolProperty(name="Is Asset Public?", default=True)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        # Post the file to Aesel on a background thread
        save_thread = threading.Thread(target=save_selected_as_obj_asset,
                                       args=(bpy.context.scene.general_api_wrapper,
                                             bpy.context.scene.portation_api_wrapper,
                                             bpy.types.Scene.transaction_client,
                                             self.asset_name,
                                             self.asset_public))
        save_thread.daemon = True
        save_thread.start()
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


# Create an Asset by exporting to blend
# This should be called from the 3d view in Object mode
class OBJECT_OT_CreateBlendAsset(bpy.types.Operator):
    bl_idname = "object.create_blend_asset"
    bl_label = "Save as blend"
    bl_description = "Export all objects to a .blend file and save this to Aesel"
    bl_options = {"REGISTER"}
    asset_name: bpy.props.StringProperty(name="Asset Name", default="")
    asset_public: bpy.props.BoolProperty(name="Is Asset Public?", default=True)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        # Post the file to Aesel on a background thread
        save_thread = threading.Thread(target=save_scene_as_blend_asset,
                                       args=(bpy.context.scene.general_api_wrapper,
                                             bpy.context.scene.portation_api_wrapper,
                                             bpy.types.Scene.transaction_client,
                                             self.asset_name,
                                             self.asset_public))
        save_thread.daemon = True
        save_thread.start()
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
