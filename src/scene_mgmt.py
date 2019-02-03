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
import os
import threading

from .bsync_utils import get_assets_file_path
from .asset_mgmt import save_selected_as_obj_asset

from aesel.AeselTransactionClient import AeselTransactionClient
from aesel.model.AeselScene import AeselScene
from aesel.model.AeselAssetRelationship import AeselAssetRelationship
from aesel.model.AeselUserDevice import AeselUserDevice
from aesel.model.AeselObject import AeselObject

# Scene UI List
class VIEW_3D_UL_Scene_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
        layout.label(text=item.key)
        layout.label(text=item.name)

# Method for creating a scene in the Aesel server
def _add_aesel_scene(transaction_client, updates_queue, key, name, tags):
    # Build a new Aesel scene
    new_scene = AeselScene()
    if name != "":
        new_scene.name = name
    if tags != "":
        new_scene.tags = tags.split(",")

    # Send the request
    response_json = transaction_client.create_scene(key, new_scene)
    print(response_json)

    # Put a message onto the updates queue to update the UI
    new_scene.key = key
    updates_queue.put({'type': 'list_add', 'data': new_scene})

# Add a new Scene to the Scene List
class OBJECT_OT_AddAeselScene(bpy.types.Operator):
    bl_idname = "object.add_aesel_scene"
    bl_label = "Create"
    bl_options = {'REGISTER'}
    scene_key: bpy.props.StringProperty(name="Scene Key", default="First")
    scene_name: bpy.props.StringProperty(name="Scene Name", default="Default")
    scene_tag: bpy.props.StringProperty(name="Scene Tags", default="")

    # Called when operator is run
    def execute(self, context):
        # execute a request to Aesel on a background thread
        save_thread = threading.Thread(target=_add_aesel_scene,
                                       args=(bpy.types.Scene.transaction_client,
                                             bpy.context.scene.aesel_updates_queue,
                                             self.scene_key,
                                             self.scene_name,
                                             self.scene_tag))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

def _update_aesel_scene(general_api_wrapper, transaction_client, updates_queue, name, tags):
    # Get the key of the selected scene in the list
    selected_key = general_api_wrapper.get_selected_scene(context)

    # Build a new Aesel scene
    new_scene = AeselScene()
    if self.scene_name != "":
        new_scene.name = self.scene_name
    if self.scene_tag != "":
        new_scene.tags = self.scene_tag.split(",")

    # Send the request
    response_json = transaction_client.update_scene(selected_key, scene)
    scene.key = key
    updates_queue.put({'type': 'list_update', 'data': scene})
    print(response_json)

# Add a new Scene to the Scene List
class OBJECT_OT_UpdateAeselScene(bpy.types.Operator):
    bl_idname = "object.update_aesel_scene"
    bl_label = "Update"
    bl_options = {'REGISTER'}
    scene_name: bpy.props.StringProperty(name="Scene Name", default="")
    scene_tag: bpy.props.StringProperty(name="Scene Tags", default="")

    # Called when operator is run
    def execute(self, context):
        # execute a request to Aesel on a background thread
        save_thread = threading.Thread(target=_update_aesel_scene,
                                       args=(bpy.context.scene.general_api_wrapper,
                                             bpy.types.Scene.transaction_client,
                                             bpy.context.scene.aesel_updates_queue,
                                             self.scene_name,
                                             self.scene_tag))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

def _delete_aesel_scene(general_api_wrapper, transaction_client, updates_queue):
    selected_key = general_api_wrapper.get_selected_scene(context)

    response_json = transaction_client.delete_scene(selected_key)
    print(response_json)

    updates_queue.put({'type': 'list_delete', 'data': selected_key})

# Delete a Scene from Aesel and the Scene List
class OBJECT_OT_DeleteAeselScene(bpy.types.Operator):
    bl_idname = "object.delete_aesel_scene"
    bl_label = "Delete"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        # execute a request to Aesel on a background thread
        save_thread = threading.Thread(target=_delete_aesel_scene,
                                       args=(bpy.context.scene.general_api_wrapper,
                                             bpy.types.Scene.transaction_client,
                                             bpy.context.scene.aesel_updates_queue))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

def _find_aesel_scenes(transaction_client, updates_queue, key, name, tags):
    # Build a new Aesel scene
    scene_query = AeselScene()
    if key != "":
        scene_query.key = key
    if name != "":
        scene_query.name = name
    if tags != "":
        scene_query.tags = tags.split(",")

    # Send the Aesel request
    response_json = transaction_client.scene_query(scene_query)
    updates_queue.put({'type': 'list_set', 'data': response_json})
    print(response_json)

# Populate the Scene list based on a query
class OBJECT_OT_FindAeselScenes(bpy.types.Operator):
    bl_idname = "object.find_aesel_scenes"
    bl_label = "Find Scenes"
    bl_options = {'REGISTER'}
    scene_key: bpy.props.StringProperty(name="Scene Key", default="")
    scene_name: bpy.props.StringProperty(name="Scene Name", default="")
    scene_tag: bpy.props.StringProperty(name="Scene Tags", default="")

    # Called when operator is run
    def execute(self, context):
        # execute a request to Aesel
        save_thread = threading.Thread(target=_find_aesel_scenes,
                                       args=(bpy.types.Scene.transaction_client,
                                             bpy.context.scene.aesel_updates_queue,
                                             self.scene_key,
                                             self.scene_name,
                                             self.scene_tag))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

def _register_aesel_device(selected_key, device):
    # Send the registration request
    response_json = bpy.types.Scene.transaction_client.register(selected_key, device)
    print(response_json)

    # Get Assets related to the Scene
    scene_relationship_query = AeselAssetRelationship()
    scene_relationship_query.related = selected_key
    scene_relationship_query.type = "scene"
    scene_relation_response = bpy.types.Scene.transaction_client.query_asset_relationships(scene_relationship_query)

    # Download Scene Assets
    for asset in scene_relation_response:
        content = bpy.types.Scene.transaction_client.get_asset(asset["assetId"])

        # Save the asset to a file
        root_file_path = get_assets_file_path(bpy.context.scene.current_scene_name,
                                              bpy.data.filepath,
                                              bpy.context.preferences.addons["BlenderSync"].preferences.asset_file_location)
        filename = os.path.join(root_file_path, 'asset-%s.blend' % asset["assetId"])
        with open(filename, 'wb') as asset_file:
            asset_file.write(content)

        # Put the file path onto a queue to be imported on the main thread
        bpy.context.scene.aesel_updates_queue.put({"filename": filename,
                                                   "type": "asset_import",
                                                   "relationship_type": asset["relationshipType"],
                                                   "relationship_subtype": asset["relationshipSubtype"],
                                                   "assetId": asset["assetId"],
                                                   "assetSubId": asset["assetSubId"],
                                                   "relatedId": asset["relatedId"]})

    # Download Objects
    obj_query = AeselObject()
    obj_query.scene = selected_key
    object_response_json = bpy.types.Scene.transaction_client.object_query(selected_key, obj_query)
    print(object_response_json)

    for record in object_response_json['objects']:

        # Find Assets related to the object
        obj_relationship_query = AeselAssetRelationship()
        obj_relationship_query.related = record["key"]
        obj_relationship_query.type = "object"
        obj_relation_result = bpy.types.Scene.transaction_client.query_asset_relationships(obj_relationship_query)

        # Download Object Assets
        for asset in obj_relation_result:
            content = bpy.types.Scene.transaction_client.get_asset(asset["assetId"])

            # Save the asset to a file
            root_file_path = get_assets_file_path(bpy.context.scene.current_scene_name,
                                                  bpy.data.filepath,
                                                  bpy.context.preferences.addons["BlenderSync"].preferences.asset_file_location)
            filename = os.path.join(root_file_path, 'asset-%s.blend' % asset["assetId"])
            with open(filename, 'wb') as asset_file:
                asset_file.write(content)

            # Put the file path onto a queue to be imported on the main thread
            bpy.context.scene.aesel_updates_queue.put({"filename": filename,
                                                       "name": record["name"],
                                                       "key": record["key"],
                                                       "transform": record["transform"],
                                                       "type": "asset_import",
                                                       "relationship_type": asset["relationshipType"],
                                                       "relationship_subtype": asset["relationshipSubtype"],
                                                       "assetId": asset["assetId"],
                                                       "assetSubId": asset["assetSubId"],
                                                       "relatedId": asset["relatedId"]})

# Register to the selected scene in the scene list
class OBJECT_OT_RegisterAeselDevice(bpy.types.Operator):
    bl_idname = "object.register_aesel_device"
    bl_label = "Register"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        # Set the current Scene ID to the selected one
        context.scene.current_scene_id = get_selected_scene(context)
        context.scene.current_scene_name = get_selected_scene_name(context)

        # Build the user device for registration
        addon_prefs = context.preferences.addons["BlenderSync"].preferences
        device = AeselUserDevice()
        device.key = addon_prefs.device_id
        device.hostname = addon_prefs.advertised_udp_host
        device.port = addon_prefs.udp_port

        # execute the scene loading workflow from Aesel on a background thread
        save_thread = threading.Thread(target=_register_aesel_device, args=(context.scene.current_scene_id, device))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

def _deregister_aesel_device(scene_id, device_id):
    # execute a request to Aesel
    response_json = bpy.types.Scene.transaction_client.deregister(scene_id, device_id)
    print(response_json)

    # Queue a message to clear the viewport of objects on the main thread
    bpy.context.scene.aesel_updates_queue.put({'type': 'viewport_clear'})

# Deregister from the selected scene in the scene list
class OBJECT_OT_DeregisterAeselDevice(bpy.types.Operator):
    bl_idname = "object.deregister_aesel_device"
    bl_label = "Deregister"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        addon_prefs = context.preferences.addons["BlenderSync"].preferences
        scene_id = context.scene.current_scene_id
        context.scene.current_scene_id = ''
        context.scene.current_scene_name = ''

        # execute the scene deregistration request to Aesel on a background thread
        save_thread = threading.Thread(target=_deregister_aesel_device, args=(scene_id, addon_prefs.device_id))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

def _save_scene_asset(scene_id, asset_name, asset_public):
    # Post the file to Aesel
    new_key = save_selected_as_obj_asset(bpy.types.Scene.transaction_client, asset_name, asset_public)
    print("Exported New Asset with Key %s" % new_key)

    # Post a new Asset Relationship
    new_relation = AeselAssetRelationship()
    new_relation.asset = new_key
    new_relation.type = "scene"
    new_relation.related = scene_id
    response_json = bpy.types.Scene.transaction_client.save_asset_relationship(new_relation)

    print(response_json)

# Save the selected objects as scene assets
class OBJECT_OT_SaveSceneAsset(bpy.types.Operator):
    bl_idname = "object.save_scene_asset"
    bl_label = "Save Scene Asset"
    bl_options = {'REGISTER'}
    asset_name: bpy.props.StringProperty(name="Asset Name", default="")
    asset_public: bpy.props.BoolProperty(name="Is Asset Public?", default=True)

    # Called when operator is run
    def execute(self, context):
        # Get the scene to save the asset against
        scene_key = get_selected_scene(context)
        if context.scene.current_scene_id is not None and context.scene.current_scene_id != '':
            scene_key = context.scene.current_scene_id

        # Execute the request to save the asset on a background thread
        save_thread = threading.Thread(target=_save_scene_asset, args=(scene_key,self.asset_name, self.asset_public))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

# Scene Panel
class VIEW_3D_PT_AeselScenePanel(bpy.types.Panel):
    """Creates an Aesel Scene UI Panel"""
    bl_label = "Aesel Scenes"
    bl_idname = "VIEW_3D_PT_aesel_scene_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Aesel'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.find_aesel_scenes")
        row = layout.row()
        row.template_list("VIEW_3D_UL_Scene_List", "SceneList", context.scene, "aesel_current_scenes", context.scene, "list_index")
        row = layout.row()
        row.operator("object.add_aesel_scene")
        row = layout.row()
        row.operator("object.update_aesel_scene")
        row = layout.row()
        row.operator("object.delete_aesel_scene")
        row = layout.row()
        row.operator("object.register_aesel_device")
        row = layout.row()
        row.operator("object.deregister_aesel_device")
        row = layout.row()
        row.operator("object.save_scene_asset")
