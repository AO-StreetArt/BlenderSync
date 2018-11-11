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
    "name": "bsync",
    "description": "Blender Add-on to Integrate with Aesel Servers",
    "author": "Your Name",
    "version": (0, 0, 2),
    "blender": (2, 79, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Object" }


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

from http.cookiejar import MozillaCookieJar
import time

from aesel.AeselTransactionClient import AeselTransactionClient
from aesel.AeselEventClient import AeselEventClient


# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())


# Global Addon Preferences
##################################

class SaveBlenderSyncPrefs(bpy.types.Operator):
    bl_idname = "object.save_bsync_prefs"
    bl_label = "Save BlenderSync Preferences"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        addon_prefs = bpy.context.user_preferences.addons[__name__].preferences
        bpy.types.Scene.transaction_client = AeselTransactionClient(addon_prefs.aesel_addr)
        if addon_prefs.cookies_file != "":
            bpy.types.Scene.transaction_client.set_cookie(MozillaCookieJar(addon_prefs.cookies_file))
            print("Setting cookie file")
        if addon_prefs.cookie != "":
            bpy.types.Scene.transaction_client.set_cookie_header(addon_prefs.cookie)
            print("Setting cookie")
        bpy.types.Scene.event_client = AeselEventClient(addon_prefs.aesel_udp_host, addon_prefs.aesel_udp_port)
        return {'FINISHED'}

class UpdateAeselCookie(bpy.types.Operator):
    bl_idname = "object.update_aesel_cookie"
    bl_label = "Reload Cookies"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        addon_prefs = bpy.context.user_preferences.addons[__name__].preferences
        if addon_prefs.cookies_file != "":
            bpy.types.Scene.transaction_client.set_cookie(MozillaCookieJar(addon_prefs.cookies_file))
            print("Setting cookie file")
        if addon_prefs.cookie != "":
            bpy.types.Scene.transaction_client.set_cookie_header(addon_prefs.cookie)
            print("Setting cookie")
        return {'FINISHED'}

class BlenderSyncPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    aesel_addr = StringProperty(
            name="Aesel HTTP Address",
            default="http://localhost:8080"
            )
    aesel_udp_host = StringProperty(
            name="Aesel UDP Address",
            default="127.0.0.1",
            )
    aesel_udp_port = IntProperty(
            name="Aesel UDP Port",
            default=8762
            )
    device_id = StringProperty(
            name="Blender Device ID",
            default="my-blender-%s" % time.time()
            )
    udp_host = StringProperty(
            name="Bound Blender UDP Address",
            default="127.0.0.1",
            )
    advertised_udp_host = StringProperty(
            name="Advertised Blender UDP Address",
            default="127.0.0.1",
            )
    udp_port = IntProperty(
            name="Blender UDP Port",
            default=6345
            )
    browser_name = StringProperty(
            name="Login Browser Name",
            default="firefox"
            )
    cookies_file = StringProperty(
            name="Cookies File",
            default=""
            )
    cookie = StringProperty(
            name="Browser Cookie",
            default=""
            )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Blender Sync Preferences")
        layout.prop(self, "aesel_addr")
        aesel_udp_row = layout.row()
        aesel_udp_row.prop(self, "aesel_udp_host")
        aesel_udp_row.prop(self, "aesel_udp_port")
        layout.prop(self, "device_id")
        layout.prop(self, "advertised_udp_host")
        row = layout.row()
        row.prop(self, "udp_host")
        row.prop(self, "udp_port")
        layout.prop(self, "browser_name")
        row = layout.row()
        row.prop(self, "cookies_file")
        row.prop(self, "cookie")
        layout.operator("object.update_aesel_cookie")
        layout.operator("object.save_bsync_prefs")

class SceneSettingItem(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Scene Name", default="test")
    key = bpy.props.StringProperty(name="Scene Key", default="key")

# register
##################################

import traceback

def register():
    try: bpy.utils.register_module(__name__)
    except: traceback.print_exc()
    
    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))
    
    # Setup the Aesel clients
    addon_prefs = bpy.context.user_preferences.addons[__name__].preferences
    bpy.types.Scene.transaction_client = AeselTransactionClient(addon_prefs.aesel_addr)
    if addon_prefs.cookies_file != "":
        bpy.types.Scene.transaction_client.set_cookie(MozillaCookieJar(addon_prefs.cookies_file))
        print("Setting cookies file")
    if addon_prefs.cookie != "":
        bpy.types.Scene.transaction_client.set_cookie_header(addon_prefs.cookie)
        print("Setting cookie")
    bpy.types.Scene.event_client = AeselEventClient(addon_prefs.aesel_udp_host, addon_prefs.aesel_udp_port)
    
    # Setup base properties
    bpy.types.Scene.aesel_current_scenes = bpy.props.CollectionProperty(type=SceneSettingItem)
    bpy.types.Scene.aesel_objects = {}
    bpy.types.Scene.aesel_live_objects = []
    bpy.types.Scene.aesel_listen_live = bpy.props.BoolProperty()
    bpy.types.Scene.list_index = bpy.props.IntProperty(name = "Index for aesel_current_scenes", default = 0)
    bpy.types.Scene.current_scene_id = bpy.props.StringProperty(name = "Current Scene ID", default="")

def unregister():
    # Clear Aesel properties
    del bpy.types.Scene.aesel_live_objects
    del bpy.types.Scene.aesel_objects
    del bpy.types.Scene.aesel_current_scenes
    del bpy.types.Scene.list_index
    del bpy.types.Scene.current_scene_id
    
    # Unregister modules
    try: bpy.utils.unregister_module(__name__)
    except: traceback.print_exc()

    # Clear out Aesel clients
    bpy.types.Scene.transaction_client = None
    bpy.types.Scene.event_client = None
    print("Unregistered {}".format(bl_info["name"]))
