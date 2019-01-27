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

import time
import queue

from aesel.AeselTransactionClient import AeselTransactionClient
from aesel.AeselEventClient import AeselEventClient

from aesel.model.AeselObject import AeselObject


# load and reload submodules
##################################

if "bpy" in locals():
    import importlib
    importlib.reload(scene_mgmt)
    importlib.reload(asset_mgmt)
    importlib.reload(obj_mgmt)
else:
    from . import scene_mgmt
    from . import asset_mgmt
    from . import obj_mgmt

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


# Object Streaming
##################################

# Pick up messages off a central Queue and update blender data with them
def process_object_updates():
    while not bpy.context.scene.aesel_updates_queue.empty():
        data_dict = bpy.context.scene.aesel_updates_queue.get()
        obj = bpy.data.objects[data_dict['name']]
        transform = data_dict['transform']
        obj.matrix_world = mathutils.Matrix(([transform[0], transform[1], transform[2], transform[3]],
                                            [transform[4], transform[5], transform[6], transform[7]],
                                            [transform[8], transform[9], transform[10], transform[11]],
                                            [transform[12], transform[13], transform[14], transform[15]]))
    return 0.1

# Listen for updates from Aesel
def listen_for_object_updates():
    addon_prefs = bpy.context.preferences.addons[__name__].preferences
    server_address = (addon_prefs.udp_host, addon_prefs.udp_port)
    print('Opening UDP Port: %s :: %s' % server_address)
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # AES-256-cbc Decryption
    cipher_backend = default_backend()
    cipher = Cipher(algorithms.AES(addon_prefs.aesel_udp_decryption_key), modes.CBC(addon_prefs.aesel_udp_decryption_iv), backend=cipher_backend)

    # Bind the socket to the port
    sock.bind(server_address)
    while(bpy.context.scene.aesel_listen_live):
        # Recieve a message from Aesel
        data, address = sock.recvfrom(8192)
        print(data)
        data_str = None
        if data:
            # Decode the recieved data, and decrypt if necessary
            if addon_prefs.udp_encryption_active:
                decryptor = cipher.decryptor()
                data_str = decryptor.update(bytes(msg, 'UTF-8')) + decryptor.finalize()
            else:
                data_str = data.decode("utf-8")
            print("Recieved data %s" % data_str)

            # Parse the data and drop it onto a queue for processing
            data_dict = json.loads(data_str)
            bpy.context.scene.aesel_updates_queue.put(data_dict)
    print("Not listening on UDP port anymore")

def send_object_updates():
    if bpy.context.scene.aesel_updates_live:
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        for elt in bpy.context.scene.aesel_live_objects:
            obj = bpy.data.objects[elt[1]]
            print("Sending UDP update for object %s" % elt[1])
            aesel_obj = AeselObject()
            aesel_obj.key = elt[0]
            aesel_obj.name = elt[1]
            aesel_obj.scene = scene_mgmt.get_selected_scene(bpy.context)
            aesel_obj.transform = [obj.matrix_world[0][0], obj.matrix_world[0][1],
                                   obj.matrix_world[0][2], obj.matrix_world[0][3],
                                   obj.matrix_world[1][0], obj.matrix_world[1][1],
                                   obj.matrix_world[1][2], obj.matrix_world[1][3],
                                   obj.matrix_world[2][0], obj.matrix_world[2][1],
                                   obj.matrix_world[2][2], obj.matrix_world[2][3],
                                   obj.matrix_world[3][0], obj.matrix_world[3][1],
                                   obj.matrix_world[3][2], obj.matrix_world[3][3]]
            # Send the actual message
            bpy.types.Scene.event_client.send_object_update(aesel_obj)
    # Return 1 / (updates per second) for the blender timer api
    return 1.0 / addon_prefs.update_rate

# Callbacks which are triggered when boolean properties are flipped
def set_aesel_auto_update(self, context):
    if not context.scene.aesel_updates_live:
        context.scene.aesel_updates_live = True
        if not context.scene.aesel_updates_initiated:
            context.scene.aesel_updates_initiated = True
            # Use the blender timer api to schedule sending automatic updates
            # TO-DO: Does this cause any sort of delay in the viewport?
            bpy.app.timers.register(send_object_updates)
    else:
        context.scene.aesel_updates_live = False

def set_aesel_listen(self, context):
    if not bpy.context.scene.aesel_listen_live:
        bpy.context.scene.aesel_listen_live = True

        # Register a function with a timer to process object updates from a Queue
        if not bpy.context.scene.aesel_listen_initiated:
            bpy.context.scene.aesel_listen_initiated = True
            bpy.app.timers.register(process_object_updates)

        # Start a background thread to listen on the UDP socket and put
        # the messages onto a queue, where they can be picked up by a
        # timer on the main thread to update the actual blender data.
        # this is the suggested design pattern in the blender docs:
        # https://docs.blender.org/api/blender2.8/bpy.app.timers.html#use-a-timer-to-react-to-events-in-another-thread
        recv_thread = threading.Thread(target=listen_for_object_updates, args=())
        recv_thread.daemon = True
        recv_thread.start()
    else:
        bpy.context.scene.aesel_listen_live = False

# Global Addon Preferences
##################################

class OBJECT_OT_SaveBlenderSyncPrefs(bpy.types.Operator):
    bl_idname = "object.save_bsync_prefs"
    bl_label = "Save BlenderSync Preferences"
    bl_options = {'REGISTER'}

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        bpy.types.Scene.transaction_client = AeselTransactionClient(addon_prefs.aesel_addr)
        if addon_prefs.cookie != "":
            bpy.types.Scene.transaction_client.set_cookie_header(addon_prefs.cookie)
            print("Setting cookie")
        bpy.types.Scene.event_client = AeselEventClient(addon_prefs.aesel_udp_host, addon_prefs.aesel_udp_port)
        return {'FINISHED'}

class OBJECT_OT_UpdateAeselCookie(bpy.types.Operator):
    bl_idname = "object.update_aesel_cookie"
    bl_label = "Reload Cookies"
    bl_options = {'REGISTER'}

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons[__name__].preferences
        if addon_prefs.cookie != "":
            bpy.types.Scene.transaction_client.set_cookie_header(addon_prefs.cookie)
            print("Setting cookie")
        return {'FINISHED'}

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
    cookie: StringProperty(
            name="Authentication Token",
            default=""
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
            name="Local folder location to store asset files",
            default="."
            )
    enable_bg_schedulers: BoolProperty(
            name="Enable BlenderSync background schedulers",
            default=True
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
        layout.prop(self, "cookie")
        layout.operator("object.update_aesel_cookie")
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
classes = [BlenderSyncPreferences,
            SceneSettingItem,
            OBJECT_OT_UpdateAeselCookie,
            OBJECT_OT_SaveBlenderSyncPrefs,
            obj_mgmt.OBJECT_OT_CreateAeselObject,
            obj_mgmt.OBJECT_OT_DeleteAeselObject,
            obj_mgmt.OBJECT_OT_LockAeselObject,
            obj_mgmt.OBJECT_OT_UnlockAeselObject,
            obj_mgmt.VIEW_3D_PT_AeselObjectPanel,
            asset_mgmt.OBJECT_OT_CreateObjAsset,
            asset_mgmt.VIEW_3D_PT_AeselAssetMgmtPanel,
            scene_mgmt.VIEW_3D_UL_Scene_List,
            scene_mgmt.OBJECT_OT_AddAeselScene,
            scene_mgmt.OBJECT_OT_UpdateAeselScene,
            scene_mgmt.OBJECT_OT_DeleteAeselScene,
            scene_mgmt.OBJECT_OT_FindAeselScenes,
            scene_mgmt.OBJECT_OT_RegisterAeselDevice,
            scene_mgmt.OBJECT_OT_DeregisterAeselDevice,
            scene_mgmt.OBJECT_OT_SaveSceneAsset,
            scene_mgmt.VIEW_3D_PT_AeselScenePanel]

def register():
    try:
        for cls in classes:
            bpy.utils.register_class(cls)
    except:
        traceback.print_exc()

    # Setup the Aesel clients
    addon_prefs = bpy.context.preferences.addons[__name__].preferences
    bpy.types.Scene.transaction_client = AeselTransactionClient(addon_prefs.aesel_addr)
    if addon_prefs.cookie != "":
        bpy.types.Scene.transaction_client.set_cookie_header(addon_prefs.cookie)
        print("Setting cookie")
    bpy.types.Scene.event_client = AeselEventClient(addon_prefs.aesel_udp_host, addon_prefs.aesel_udp_port)

    # Setup base properties
    bpy.types.Scene.aesel_current_scenes = bpy.props.CollectionProperty(type=SceneSettingItem)
    bpy.types.Scene.aesel_objects = {}
    bpy.types.Scene.aesel_live_objects = []
    bpy.types.Scene.aesel_listen_live = bpy.props.BoolProperty()
    bpy.types.Scene.aesel_listen_initiated = bpy.props.BoolProperty()
    bpy.types.Scene.aesel_updates_live = bpy.props.BoolProperty()
    bpy.types.Scene.aesel_updates_initiated = bpy.props.BoolProperty()
    bpy.types.Scene.aesel_auto_updates = bpy.props.BoolProperty(name="Send Updates", update=set_aesel_auto_update)
    bpy.types.Scene.aesel_listen_for_updates = bpy.props.BoolProperty(name="Listen for Updates", update=set_aesel_listen)
    bpy.types.Scene.aesel_updates_queue = queue.Queue()
    bpy.types.Scene.aesel_imports_queue = queue.Queue()
    bpy.types.Scene.list_index = bpy.props.IntProperty(name = "Index for aesel_current_scenes", default = 0)
    bpy.types.Scene.current_scene_id = bpy.props.StringProperty(name = "Current Scene ID", default="")
    bpy.types.Scene.current_scene_name = bpy.props.StringProperty(name = "Current Scene Name", default="")

    # Register background functions that should run forever
    bpy.app.timers.register(asset_mgmt.import_asset_monitor)

def unregister():
    # Clear Aesel properties
    del bpy.types.Scene.aesel_live_objects
    del bpy.types.Scene.aesel_objects
    del bpy.types.Scene.aesel_current_scenes
    del bpy.types.Scene.aesel_listen_live
    del bpy.types.Scene.aesel_updates_initiated
    del bpy.types.Scene.aesel_updates_live
    del bpy.types.Scene.aesel_listen_initiated
    del bpy.types.Scene.aesel_auto_updates
    del bpy.types.Scene.aesel_update_rate
    del bpy.types.Scene.aesel_updates_queue
    del bpy.types.Scene.aesel_imports_queue
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
