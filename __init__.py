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

bl_info = {
    "name": "BlenderSync",
    "description": "Blender Add-on to Integrate with Aesel Servers",
    "author": "Your Name",
    "version": (0, 0, 3),
    "blender": (2, 80, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Object" }

# Basic imports

import functools
import queue
import threading
import time
import traceback

from aesel.AeselTransactionClient import AeselTransactionClient
from aesel.AeselEventClient import AeselEventClient

from aesel.model.AeselObject import AeselObject

from .animation_client.queue_monitor import aesel_queue_monitor


# load and reload submodules
##################################

if "bpy" in locals():
    import importlib
    importlib.reload(general_api_wrapper)
    importlib.reload(object_api_wrapper)
    importlib.reload(portation_api_wrapper)
    importlib.reload(scene_mgmt_operators)
    importlib.reload(asset_mgmt_operators)
    importlib.reload(obj_mgmt_operators)
    importlib.reload(obj_streaming_callbacks)
    importlib.reload(test_operators)
    importlib.reload(asset_mgmt_ui)
    importlib.reload(obj_mgmt_ui)
    importlib.reload(scene_mgmt_ui)
else:
    from .src.blender_api_wrapper import general_api_wrapper
    from .src.blender_api_wrapper import object_api_wrapper
    from .src.blender_api_wrapper import portation_api_wrapper
    from .src import scene_mgmt_operators
    from .src import asset_mgmt_operators
    from .src import obj_mgmt_operators
    from .src import obj_streaming_callbacks
    from .src import test_operators
    from .src.ui import asset_mgmt_ui
    from .src.ui import obj_mgmt_ui
    from .src.ui import scene_mgmt_ui

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

# Global Addon Preferences
##################################

class OBJECT_OT_SaveBlenderSyncPrefs(bpy.types.Operator):
    bl_idname = "object.save_bsync_prefs"
    bl_label = "Save BlenderSync Preferences"
    bl_options = {'REGISTER'}

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        bpy.types.Scene.transaction_client = AeselTransactionClient(addon_prefs.aesel_addr)
        bpy.types.Scene.event_client = AeselEventClient(addon_prefs.aesel_udp_host, addon_prefs.aesel_udp_port)
        return {'FINISHED'}

class OBJECT_OT_AeselLogin(bpy.types.Operator):
    bl_idname = "object.aesel_login"
    bl_label = "Login"
    bl_options = {'REGISTER'}
    username: bpy.props.StringProperty(name="Username", default="")
    password: bpy.props.StringProperty(name="Password", subtype='PASSWORD')

    def execute(self, context):
        try:
            bpy.types.Scene.transaction_client.login(self.username, self.password)
        except Exception as e:
            self.report({'ERROR'}, 'Login unsuccessful: %s' % traceback.format_exc(e))
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

def toggle_global_schedulers(self, context):
    addon_prefs = context.preferences.addons[__name__].preferences
    if addon_prefs.enable_bg_schedulers:
        # Register background functions that should run forever
        bpy.app.timers.register(queue_monitor.aesel_queue_monitor)
    else:
        # Turn off global schedulers (ie. during rendering)
        bpy.app.timers.unregister(queue_monitor.aesel_queue_monitor)

class BlenderSyncPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    aesel_addr: StringProperty(
            name="Aesel HTTP Address",
            default="http://localhost:8080"
            )
    aesel_udp_host: StringProperty(
            name="Aesel UDP Address",
            default="127.0.0.1",
            )
    aesel_udp_port: IntProperty(
            name="Aesel UDP Port",
            default=8762
            )
    udp_encryption_active: BoolProperty(
            name="Activate UDP Encryption"
            )
    aesel_udp_decryption_key: StringProperty(
            name="Aesel UDP Decryption Key",
            default="",
            )
    aesel_udp_decryption_iv: StringProperty(
            name="Aesel UDP Decryption IV",
            default="",
            )
    aesel_udp_encryption_key: StringProperty(
            name="Aesel UDP Encryption Key",
            default="",
            )
    aesel_udp_encryption_iv: StringProperty(
            name="Aesel UDP Encryption IV",
            default="",
            )
    device_id: StringProperty(
            name="Blender Device ID",
            default="my-blender-%s" % time.time()
            )
    udp_host: StringProperty(
            name="Bound Blender UDP Address",
            default="127.0.0.1",
            )
    advertised_udp_host: StringProperty(
            name="Advertised Blender UDP Address",
            default="127.0.0.1",
            )
    udp_port: IntProperty(
            name="Blender UDP Port",
            default=6345
            )
    update_rate: IntProperty(
            name="Number of Update Events to send per second",
            default=10
            )
    asset_file_type: StringProperty(
            name="Default Asset File Type",
            default="blend"
            )
    asset_file_location: StringProperty(
            name="Local Asset Folder",
            default="."
            )
    enable_bg_schedulers: BoolProperty(
            name="Enable Background Schedulers",
            default=True, update=toggle_global_schedulers
            )

    def draw(self, context):
        layout = self.layout

        layout.label(text="Blender Sync Preferences")
        layout.prop(self, "aesel_addr")
        layout.prop(self, "aesel_udp_host")
        layout.prop(self, "aesel_udp_port")
        layout.prop(self, "udp_encryption_active")
        layout.prop(self, "aesel_udp_encryption_iv")
        layout.prop(self, "aesel_udp_encryption_key")
        layout.prop(self, "aesel_udp_decryption_iv")
        layout.prop(self, "aesel_udp_decryption_key")
        layout.prop(self, "device_id")
        layout.prop(self, "advertised_udp_host")
        layout.prop(self, "udp_host")
        layout.prop(self, "udp_port")
        layout.prop(self, "update_rate")
        layout.prop(self, "asset_file_type")
        layout.prop(self, "asset_file_location")
        layout.prop(self, "enable_bg_schedulers")
        layout.operator("object.aesel_login")
        layout.operator("object.save_bsync_prefs")

class SceneSettingItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Scene Name", default="test")
    key: bpy.props.StringProperty(name="Scene Key", default="key")

# register
##################################

import traceback

# Registration for each class individually,
# per change notes for Blender2.8 release
# https://wiki.blender.org/wiki/Reference/Release_Notes/2.80/Python_API/Addons
classes = [SceneSettingItem,
            BlenderSyncPreferences,
            OBJECT_OT_AeselLogin,
            OBJECT_OT_SaveBlenderSyncPrefs,
            scene_mgmt_ui.VIEW_3D_UL_Scene_List,
            scene_mgmt_operators.OBJECT_OT_AddAeselScene,
            scene_mgmt_operators.OBJECT_OT_UpdateAeselScene,
            scene_mgmt_operators.OBJECT_OT_DeleteAeselScene,
            scene_mgmt_operators.OBJECT_OT_FindAeselScenes,
            scene_mgmt_operators.OBJECT_OT_RegisterAeselDevice,
            scene_mgmt_operators.OBJECT_OT_DeregisterAeselDevice,
            scene_mgmt_operators.OBJECT_OT_SaveSceneAsset,
            scene_mgmt_ui.VIEW_3D_PT_AeselScenePanel,
            obj_mgmt_operators.OBJECT_OT_CreateAeselObject,
            obj_mgmt_operators.OBJECT_OT_DeleteAeselObject,
            obj_mgmt_operators.OBJECT_OT_LockAeselObject,
            obj_mgmt_operators.OBJECT_OT_UnlockAeselObject,
            obj_mgmt_ui.VIEW_3D_PT_AeselObjectPanel,
            asset_mgmt_operators.OBJECT_OT_CreateObjAsset,
            asset_mgmt_operators.OBJECT_OT_CreateBlendAsset,
            asset_mgmt_ui.VIEW_3D_PT_AeselAssetMgmtPanel,
            test_operators.OBJECT_OT_ExecuteBlenderSyncTests]

def register():
    try:
        for cls in classes:
            bpy.utils.register_class(cls)
    except:
        traceback.print_exc()

    # Setup the Aesel clients
    addon_prefs = bpy.context.preferences.addons[__name__].preferences
    bpy.types.Scene.transaction_client = AeselTransactionClient(addon_prefs.aesel_addr)
    bpy.types.Scene.event_client = AeselEventClient(addon_prefs.aesel_udp_host, addon_prefs.aesel_udp_port)

    # Setup base properties
    bpy.types.Scene.aesel_current_scenes = bpy.props.CollectionProperty(type=SceneSettingItem)
    bpy.types.Scene.aesel_objects = {}
    bpy.types.Scene.aesel_live_objects = []
    bpy.types.Scene.aesel_listen_live = bpy.props.BoolProperty()
    bpy.types.Scene.aesel_updates_live = bpy.props.BoolProperty()
    bpy.types.Scene.aesel_updates_initiated = bpy.props.BoolProperty()
    bpy.types.Scene.general_api_wrapper = general_api_wrapper.GeneralApiWrapper()
    bpy.types.Scene.object_api_wrapper = object_api_wrapper.ObjectApiWrapper()
    bpy.types.Scene.portation_api_wrapper = portation_api_wrapper.PortationApiWrapper()
    bpy.types.Scene.aesel_auto_updates = bpy.props.BoolProperty(name="Send Updates", update=obj_streaming_callbacks.set_aesel_auto_update)
    bpy.types.Scene.aesel_listen_for_updates = bpy.props.BoolProperty(name="Listen for Updates", update=obj_streaming_callbacks.set_aesel_listen)
    bpy.types.Scene.aesel_updates_queue = queue.Queue()
    bpy.types.Scene.list_index = bpy.props.IntProperty(name = "Index for aesel_current_scenes", default = 0)
    bpy.types.Scene.current_scene_id = bpy.props.StringProperty(name = "Current Scene ID", default="")
    bpy.types.Scene.current_scene_name = bpy.props.StringProperty(name = "Current Scene Name", default="")

    # Register background functions
    bpy.app.timers.register(functools.partial(aesel_queue_monitor,
                                              bpy.types.Scene.general_api_wrapper,
                                              bpy.types.Scene.object_api_wrapper,
                                              bpy.types.Scene.portation_api_wrapper,
                                              bpy.types.Scene.aesel_updates_queue))

def unregister():
    # Shut down any scheduled methods
    # addon_prefs = bpy.context.preferences.addons[__name__].preferences
    # if bpy.app.timers.is_registered(queue_monitor.aesel_queue_monitor):
    #     bpy.app.timers.unregister(queue_monitor.aesel_queue_monitor)
    # if bpy.app.timers.is_registered(send_object_updates):
    #     bpy.app.timers.unregister(send_object_updates)

    # Clear Aesel properties
    bpy.types.Scene.aesel_listen_live = False
    bpy.types.Scene.aesel_updates_live = False
    del bpy.types.Scene.aesel_live_objects
    del bpy.types.Scene.aesel_objects
    del bpy.types.Scene.aesel_current_scenes
    del bpy.types.Scene.aesel_listen_live
    del bpy.types.Scene.aesel_updates_initiated
    del bpy.types.Scene.aesel_updates_live
    del bpy.types.Scene.aesel_auto_updates
    del bpy.types.Scene.aesel_updates_queue
    del bpy.types.Scene.list_index
    del bpy.types.Scene.current_scene_id

    # Unregister modules
    try:
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
    except:
        traceback.print_exc()

    # Clear out Aesel clients
    bpy.types.Scene.transaction_client = None
    bpy.types.Scene.event_client = None
    print("Unregistered {}".format(bl_info["name"]))
