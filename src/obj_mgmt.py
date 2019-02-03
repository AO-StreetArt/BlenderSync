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
import threading

from .bsync_utils import get_active_object
from .asset_mgmt import save_selected_as_obj_asset, gen_asset_metadata
from .scene_mgmt import get_selected_scene

from aesel.AeselTransactionClient import AeselTransactionClient
from aesel.model.AeselAssetRelationship import AeselAssetRelationship
from aesel.model.AeselObject import AeselObject

def _create_aesel_object(scene_key, new_obj):
    active_obj = get_active_object(bpy.context)

    # Post the Object
    obj_response_json = bpy.types.Scene.transaction_client.create_object(scene_key, new_obj)
    active_obj['key'] = obj_response_json["objects"][0]["key"]
    print(obj_response_json)

    # Post an Asset
    new_asset_key = save_selected_as_obj_asset(new_obj.name, True, export_file=False)

    # Post a new Asset Relationship
    new_relation = AeselAssetRelationship()
    new_relation.asset = new_asset_key
    new_relation.type = "object"
    new_relation.related = obj_response_json["objects"][0]["key"]
    response_json = bpy.types.Scene.transaction_client.save_asset_relationship(new_relation)

    print(response_json)

# Save the active object to Aesel
class OBJECT_OT_CreateAeselObject(bpy.types.Operator):
    bl_idname = "object.create_aesel_object"
    bl_label = "Save"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = get_active_object(context)
        # First, we need to save the current transform, and move the object
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
        save_selected_as_obj_asset(obj.name, True, post_asset=False)
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
        new_obj.scene = context.scene.current_scene_id
        new_obj.translation = current_location
        new_obj.euler_rotation = current_rotation
        new_obj.scale = current_scale

        # execute the object creation workflow from Aesel on a background thread
        save_thread = threading.Thread(target=_create_aesel_object, args=(context.scene.current_scene_id, new_obj))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

def _delete_aesel_object(scene_key, object_key):
    # Get the assets associated to the selected object
    obj_relationship_query = AeselAssetRelationship()
    obj_relationship_query.related = object_key
    obj_relationship_query.type = "object"
    obj_relation_result = bpy.types.Scene.transaction_client.query_asset_relationships(obj_relationship_query)

    # Delete the object assets
    for relation in obj_relation_result:
        bpy.types.Scene.transaction_client.delete_asset(relation["assetId"])

    # Delete the object from aesel
    bpy.types.Scene.transaction_client.delete_object(scene_key, object_key)

# Delete the active object from Aesel
class OBJECT_OT_DeleteAeselObject(bpy.types.Operator):
    bl_idname = "object.delete_aesel_object"
    bl_label = "Delete"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        # Delete the object from blender
        bpy.ops.object.delete()

        # execute the object creation workflow from Aesel on a background thread
        save_thread = threading.Thread(target=_delete_aesel_object, args=(context.scene.current_scene_id, selected_obj["key"]))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

def _lock_aesel_object(scene_key, object_key, object_name, device_key):
    # Send the Aesel request
    response_json = bpy.types.Scene.transaction_client.lock_object(scene_key, object_key, device_key)
    print(response_json)

    # Drop a message on the queue to make the object live
    bpy.context.scene.aesel_updates_queue.put({'type': 'lock_object',
                                               'obj_key': object_key,
                                               'obj_name': object_name})

# Send lock requests for the active object
class OBJECT_OT_LockAeselObject(bpy.types.Operator):
    bl_idname = "object.lock_aesel_object"
    bl_label = "Lock"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        selected_obj = get_active_object(context)
        device_key = context.preferences.addons[__name__].preferences.device_id

        # execute the object creation workflow from Aesel on a background thread
        save_thread = threading.Thread(target=_lock_aesel_object, args=(context.scene.current_scene_id, selected_obj["key"], selected_obj.name, device_key))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

def _unlock_aesel_object(scene_key, object_key, object_name, device_key):
    # Send the Aesel request
    response_json = bpy.types.Scene.transaction_client.unlock_object(scene_key, object_key, device_key)
    print(response_json)

    # Drop a message on the queue to make the object live
    bpy.context.scene.aesel_updates_queue.put({'type': 'unlock_object',
                                               'obj_key': object_key,
                                               'obj_name': object_name})

# Send unlock requests for the active object
class OBJECT_OT_UnlockAeselObject(bpy.types.Operator):
    bl_idname = "object.unlock_aesel_object"
    bl_label = "Unlock"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        selected_scene = get_selected_scene(context)
        selected_obj = get_active_object(context)
        device_key = context.preferences.addons[__name__].preferences.device_id

        # execute the object creation workflow from Aesel on a background thread
        save_thread = threading.Thread(target=_unlock_aesel_object, args=(context.scene.current_scene_id, selected_obj["key"], selected_obj.name, device_key))
        save_thread.daemon = True
        save_thread.start()

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
        row = layout.row()
        row.operator("object.delete_aesel_object")
        row = layout.row()
        row.operator("object.lock_aesel_object")
        row = layout.row()
        row.operator("object.unlock_aesel_object")
        row = layout.row()
        row.prop(context.scene, 'aesel_auto_updates')
        row = layout.row()
        row.prop(context.scene, 'aesel_listen_for_updates')
