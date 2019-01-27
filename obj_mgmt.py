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
import copy

from .asset_mgmt import save_selected_as_obj_asset
from .scene_mgmt import get_selected_scene

from aesel.AeselTransactionClient import AeselTransactionClient
from aesel.model.AeselAssetRelationship import AeselAssetRelationship
from aesel.model.AeselObject import AeselObject

# Save the active object to Aesel
class OBJECT_OT_CreateAeselObject(bpy.types.Operator):
    bl_idname = "object.create_aesel_object"
    bl_label = "Save Object"
    bl_options = {'REGISTER'}

    def execute(self, context):
        selected_key = get_selected_scene(context)
        obj = bpy.context.active_object
        # First, we need to save the current rotation, and move the object
        # to (0,0,0) so that it exports correctly
        current_location = [copy.deepcopy(obj.location.x),
                            copy.deepcopy(obj.location.y),
                            copy.deepcopy(obj.location.z)]
        current_rotation = [copy.deepcopy(obj.rotation_euler.x),
                            copy.deepcopy(obj.rotation_euler.y),
                            copy.deepcopy(obj.rotation_euler.z)]
        current_scale = [copy.deepcopy(obj.scale.x),
                            copy.deepcopy(obj.scale.y),
                            copy.deepcopy(obj.scale.z)]
        obj.location.x = 0.0
        obj.location.y = 0.0
        obj.location.z = 0.0
        obj.rotation_euler.x = 0.0
        obj.rotation_euler.y = 0.0
        obj.rotation_euler.z = 0.0
        obj.scale.x = 1.0
        obj.scale.y = 1.0
        obj.scale.z = 1.0
        new_key = save_selected_as_obj_asset()
        # Move the object back
        obj.location.x = current_location[0]
        obj.location.y = current_location[1]
        obj.location.z = current_location[2]
        obj.rotation_euler.x = current_rotation[0]
        obj.rotation_euler.y = current_rotation[1]
        obj.rotation_euler.z = current_rotation[2]
        obj.scale.x = current_scale[0]
        obj.scale.y = current_scale[1]
        obj.scale.z = current_scale[2]

        # Build an Aesel Object
        new_obj = AeselObject()
        new_obj.name = obj.name
        new_obj.type = "mesh"
        new_obj.subtype = "custom"
        new_obj.scene = selected_key
        new_obj.translation = current_location
        new_obj.euler_rotation = current_rotation
        new_obj.scale = current_scale
        obj_response_json = bpy.types.Scene.transaction_client.create_object(selected_key, new_obj)
        bpy.context.active_object['key'] = obj_response_json["objects"][0]["key"]
        print(obj_response_json)

        # Post a new Asset Relationship
        new_relation = AeselAssetRelationship()
        new_relation.asset = new_key
        new_relation.type = "object"
        new_relation.related = obj_response_json["objects"][0]["key"]
        response_json = bpy.types.Scene.transaction_client.save_asset_relationship(new_relation)

        print(response_json)

        # Let's blender know the operator is finished
        return {'FINISHED'}

# Delete the active object from Aesel
class OBJECT_OT_DeleteAeselObject(bpy.types.Operator):
    bl_idname = "object.delete_aesel_object"
    bl_label = "Delete Object"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        selected_key = get_selected_scene(context)
        selected_obj = bpy.context.active_object

        # Get the assets associated to the selected object
        obj_relationship_query = AeselAssetRelationship()
        obj_relationship_query.related = selected_obj["key"]
        obj_relationship_query.type = "object"
        obj_relation_result = bpy.types.Scene.transaction_client.query_asset_relationships(obj_relationship_query)

        # Delete the object assets
        for relation in obj_relation_result:
            bpy.types.Scene.transaction_client.delete_asset(relation["assetId"])

        # Delete the object from aesel
        bpy.types.Scene.transaction_client.delete_object(selected_key, selected_obj["key"])

        # Delete the object from blender
        bpy.ops.object.delete()

        # Let's blender know the operator is finished
        return {'FINISHED'}

# Send lock requests for the active object
class OBJECT_OT_LockAeselObject(bpy.types.Operator):
    bl_idname = "object.lock_aesel_object"
    bl_label = "Lock Object"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        selected_scene = get_selected_scene(context)
        selected_obj = bpy.context.active_object
        device_key = context.preferences.addons[__name__].preferences.device_id

        # Execute the request
        response_json = bpy.types.Scene.transaction_client.lock_object(selected_scene, selected_obj["key"], device_key)
        print(response_json)

        # Add the object to the live objects list
        context.scene.aesel_live_objects.append((context.scene.aesel_objects[obj.name], selected_obj.name))
        # Let's blender know the operator is finished
        return {'FINISHED'}

# Send unlock requests for the active object
class OBJECT_OT_UnlockAeselObject(bpy.types.Operator):
    bl_idname = "object.unlock_aesel_object"
    bl_label = "Unlock Object"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        selected_scene = get_selected_scene(context)
        selected_obj = bpy.context.active_object
        device_key = context.preferences.addons[__name__].preferences.device_id

        # Execute the request
        response_json = bpy.types.Scene.transaction_client.unlock_object(selected_scene, selected_obj["key"], device_key)
        print(response_json)

        # Remove the ID from the live objects list
        context.scene.aesel_live_objects.remove((context.scene.aesel_objects[obj.name], selected_obj.name))
        # Let's blender know the operator is finished
        return {'FINISHED'}

# Object Panel
class VIEW_3D_PT_AeselObjectPanel(bpy.types.Panel):
    """Creates an Aesel Object UI Panel"""
    bl_label = "Aesel Objects"
    bl_idname = "VIEW_3D_PT_aesel_obj_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Aesel'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.create_aesel_object")
        row.operator("object.delete_aesel_object")
        row = layout.row()
        row.operator("object.lock_aesel_object")
        row.operator("object.unlock_aesel_object")
        row = layout.row()
        row.prop(context.scene, 'aesel_auto_updates')
        row.prop(context.scene, 'aesel_listen_for_updates')
