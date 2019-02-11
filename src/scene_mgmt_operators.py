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
import threading

from ..animation_client.scene_mgmt import _add_aesel_scene, _update_aesel_scene, _delete_aesel_scene, _find_aesel_scenes, _register_aesel_device, _deregister_aesel_device, _save_scene_asset

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

# Register to the selected scene in the scene list
class OBJECT_OT_RegisterAeselDevice(bpy.types.Operator):
    bl_idname = "object.register_aesel_device"
    bl_label = "Register"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        # execute the scene loading workflow from Aesel on a background thread
        save_thread = threading.Thread(target=_register_aesel_device,
                                       args=(bpy.context.scene.general_api_wrapper,
                                             bpy.types.Scene.transaction_client,
                                             bpy.context.scene.aesel_updates_queue))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

# Deregister from the selected scene in the scene list
class OBJECT_OT_DeregisterAeselDevice(bpy.types.Operator):
    bl_idname = "object.deregister_aesel_device"
    bl_label = "Deregister"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        # execute the scene deregistration request to Aesel on a background thread
        save_thread = threading.Thread(target=_deregister_aesel_device,
                                       args=(bpy.context.scene.general_api_wrapper,
                                             bpy.types.Scene.transaction_client,
                                             bpy.context.scene.aesel_updates_queue))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

# Save the selected objects as scene assets
class OBJECT_OT_SaveSceneAsset(bpy.types.Operator):
    bl_idname = "object.save_scene_asset"
    bl_label = "Save Scene Asset"
    bl_options = {'REGISTER'}
    asset_name: bpy.props.StringProperty(name="Asset Name", default="")
    asset_public: bpy.props.BoolProperty(name="Is Asset Public?", default=True)

    # Called when operator is run
    def execute(self, context):
        # Execute the request to save the asset on a background thread
        save_thread = threading.Thread(target=_save_scene_asset,
                                       args=(bpy.context.scene.general_api_wrapper,
                                             bpy.context.scene.portation_api_wrapper,
                                             bpy.types.Scene.transaction_client,
                                             self.asset_name,
                                             self.asset_public))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
