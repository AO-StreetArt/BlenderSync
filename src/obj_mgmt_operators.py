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

from ..animation_client.obj_mgmt import _initiate_create_aesel_obj_flow, _create_aesel_object, _initiate_delete_aesel_obj_flow, _delete_aesel_object, _lock_aesel_object, _unlock_aesel_object

# Save the active object to Aesel
class OBJECT_OT_CreateAeselObject(bpy.types.Operator):
    bl_idname = "object.create_aesel_object"
    bl_label = "Save"
    bl_options = {'REGISTER'}

    def execute(self, context):
        new_obj = _initiate_create_aesel_obj_flow(bpy.context.scene.general_api_wrapper,
                                                  bpy.context.scene.portation_api_wrapper,
                                                  bpy.context.scene.object_api_wrapper,
                                                  bpy.types.Scene.transaction_client,
                                                  bpy.context.scene.aesel_updates_queue)

        # execute the object creation workflow from Aesel on a background thread
        save_thread = threading.Thread(target=_create_aesel_object,
                                       args=(bpy.context.scene.general_api_wrapper,
                                             bpy.context.scene.portation_api_wrapper,
                                             bpy.context.scene.object_api_wrapper,
                                             bpy.types.Scene.transaction_client,
                                             bpy.context.scene.aesel_updates_queue,
                                             new_obj))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

# Delete the active object from Aesel
class OBJECT_OT_DeleteAeselObject(bpy.types.Operator):
    bl_idname = "object.delete_aesel_object"
    bl_label = "Delete"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        scene_key, obj_key = _initiate_delete_aesel_obj_flow(bpy.context.scene.general_api_wrapper,
                                                             bpy.context.scene.object_api_wrapper)

        # execute the object creation workflow from Aesel on a background thread
        save_thread = threading.Thread(target=_delete_aesel_object,
                                       args=(bpy.types.Scene.transaction_client,
                                             scene_key, obj_key))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

# Send lock requests for the active object
class OBJECT_OT_LockAeselObject(bpy.types.Operator):
    bl_idname = "object.lock_aesel_object"
    bl_label = "Lock"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        # execute the object creation workflow from Aesel on a background thread
        save_thread = threading.Thread(target=_lock_aesel_object,
                                       args=(bpy.context.scene.general_api_wrapper,
                                             bpy.context.scene.object_api_wrapper,
                                             bpy.types.Scene.transaction_client,
                                             bpy.context.scene.aesel_updates_queue))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}

# Send unlock requests for the active object
class OBJECT_OT_UnlockAeselObject(bpy.types.Operator):
    bl_idname = "object.unlock_aesel_object"
    bl_label = "Unlock"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        # execute the object creation workflow from Aesel on a background thread
        save_thread = threading.Thread(target=_unlock_aesel_object,
                                       args=(bpy.context.scene.general_api_wrapper,
                                             bpy.context.scene.object_api_wrapper,
                                             bpy.types.Scene.transaction_client,
                                             bpy.context.scene.aesel_updates_queue))
        save_thread.daemon = True
        save_thread.start()

        # Let's blender know the operator is finished
        return {'FINISHED'}
