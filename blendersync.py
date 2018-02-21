"""
The MIT License (MIT)

Copyright (c) 2015 Alex Barry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@author: AO Street Art
"""

bl_info = {
    "name": "BlenderSync",
    "author": "AO Street Art",
    "version": (0, 0, 1),
    "blender": (2, 79, 0),
    "description": "Blender Add on to integrate with other instances via Aesel",
    "category": "Object",
}

import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty, CollectionProperty
import requests
import socket

# Callbacks
def set_aesel_auto_update(self, context):
    pass

def get_selected_scene(self, context):
    return context.scene.aesel_current_scenes[context.scene.list_index].name

# Global Addon Properties
class BlenderSyncPreferences(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    aesel_addr = StringProperty(
            name="Aesel Address"
            )
    device_id = StringProperty(
            name="Blender Device ID"
            )
    udp_host = StringProperty(
            name="Blender IP Address",
            default="127.0.0.1",
            )
    udp_port = IntProperty(
            name="Blender IP Port",
            default=5838
            )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Blender Sync Preferences")
        layout.prop(self, "aesel_addr")
        layout.prop(self, "udp_host")
        layout.prop(self, "udp_port")

# Custom UI Panels

# Blender Sync Panel
class BlenderSyncPanel(bpy.types.Panel):
    """Creates a BlenderSync UI Panel"""
    bl_label = "Sync Configuration"
    bl_idname = "POSE_PT_blendersync_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'

    @classmethod
    def poll(cls, context):
        return context.object

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.save_aesel_config")
        row.operator("object.load_aesel_config")

# Scene UI List
class Scene_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
        layout.label(item.name)

# Scene Panel
class AeselScenePanel(bpy.types.Panel):
    """Creates an Aesel Scene UI Panel"""
    bl_label = "Sync Scenes"
    bl_idname = "POSE_PT_aesel_scene_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'

    @classmethod
    def poll(cls, context):
        return context.object

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.find_aesel_scenes")
        row = layout.row()
        row.template_list("Scene_List", "SceneList", context.scene, "aesel_current_scenes", context.scene, "list_index")
        # row.prop(context.scene, 'aesel_current_scenes')
        row = layout.row()
        row.operator("object.add_aesel_scene")
        row.operator("object.delete_aesel_scene")
        row = layout.row()
        row.operator("object.update_aesel_scene")
        row = layout.row()
        row.operator("object.register_aesel_device")
        row.operator("object.deregister_aesel_device")
        row = layout.row()
        row.operator("object.save_scene_assets")

# Object Panel
class AeselObjectPanel(bpy.types.Panel):
    """Creates an Aesel Object UI Panel"""
    bl_label = "Sync Objects"
    bl_idname = "POSE_PT_aesel_object_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'

    @classmethod
    def poll(cls, context):
        return context.object

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.delete_aesel_object")
        row.operator("object.save_aesel_object")
        row = layout.row()
        row.operator("object.send_aesel_updates")
        row = layout.row()
        row.prop(context.scene, 'aesel_auto_updates')
        row.prop(context.scene, 'aesel_update_rate')

# Operators

# TO-DO: Save the Aesel configuration to a JSON File
# Basically, needs to save the scene we're registered to
# User preferences are saved as part of Blender User Preferences
class SaveAeselConfig(bpy.types.Operator):
    bl_idname = "object.save_aesel_config"
    bl_label = "Save Aesel Configuration"
    bl_options = {'REGISTER', 'UNDO'}
    file_path = bpy.props.StringProperty(name="File Path", default="")

    # Called when operator is run
    def execute(self, context):
        addon_prefs = context.user_preferences.addons[__name__].preferences
        print("Global Configuration")
        print("Aesel Address: %s, Blender IP: %s, Blender Port: %s" % (addon_prefs.aesel_addr,
                                                                       addon_prefs.udp_host,
                                                                       addon_prefs.udp_port))

        # Let's blender know the operator is finished
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

# TO-DO: Load the Aesel configuration from a JSON File
class LoadAeselConfig(bpy.types.Operator):
    bl_idname = "object.load_aesel_config"
    bl_label = "Load Aesel Configuration"
    bl_options = {'REGISTER', 'UNDO'}
    file_path = bpy.props.StringProperty(name="File Path", default="")

    # Called when operator is run
    def execute(self, context):

        # Let's blender know the operator is finished
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

# Add a new Scene to the Scene List
class AddAeselScene(bpy.types.Operator):
    bl_idname = "object.add_aesel_scene"
    bl_label = "Create Scene"
    bl_options = {'REGISTER', 'UNDO'}
    scene_name = bpy.props.StringProperty(name="Scene Name", default="Default")
    scene_region = bpy.props.StringProperty(name="Scene Region", default="")
    scene_tag = bpy.props.StringProperty(name="Scene Tags", default="")
    scene_lat = bpy.props.FloatProperty(name="Scene Latitude", default=-9999.0)
    scene_lon = bpy.props.FloatProperty(name="Scene Longitude", default=-9999.0)

    # Called when operator is run
    def execute(self, context):
        # Build an Adrestia Query Map
        query_map = {}
        if self.scene_region != "":
            query_map['region'] = self.scene_region
        if self.scene_tag != "":
            query_map['tags'] = self.scene_tag.split(",")
        if self.scene_lat > -9998.0:
            query_map['latitude'] = self.scene_lat
        if self.scene_lon > -9998.0:
            query_map['longitude'] = self.scene_lon

        # execute a request to Aesel
        addon_prefs = context.user_preferences.addons[__name__].preferences
        r = requests.post(addon_prefs.aesel_addr + '/v1/scene/' + self.scene_name, json=query_map)
        # Parse response JSON
        print(r)
        response_json = r.json()
        print(response_json)

        # Let's blender know the operator is finished
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

# Delete a Scene from Aesel and the Scene List
class DeleteAeselScene(bpy.types.Operator):
    bl_idname = "object.delete_aesel_scene"
    bl_label = "Delete Scene"
    bl_options = {'REGISTER', 'UNDO'}

    # Called when operator is run
    def execute(self, context):

        # execute a request to Aesel
        selected_name = get_selected_scene(context)
        addon_prefs = context.user_preferences.addons[__name__].preferences
        r = requests.delete(addon_prefs.aesel_addr + '/v1/scene/' + selected_name)

        # Parse response JSON
        print(r)
        response_json = r.json()
        print(response_json)

        # Let's blender know the operator is finished
        return {'FINISHED'}

# Populate the Scene list based on a query
class FindAeselScenes(bpy.types.Operator):
    bl_idname = "object.find_aesel_scenes"
    bl_label = "Find Scenes"
    bl_options = {'REGISTER', 'UNDO'}
    scene_name = bpy.props.StringProperty(name="Scene Name", default="")
    scene_region = bpy.props.StringProperty(name="Scene Region", default="")
    scene_tag = bpy.props.StringProperty(name="Scene Tags", default="")
    scene_lat = bpy.props.FloatProperty(name="Scene Latitude", default=-9999.0)
    scene_lon = bpy.props.FloatProperty(name="Scene Longitude", default=-9999.0)

    # Called when operator is run
    def execute(self, context):
        # Build an Adrestia Query Map
        query_map = {}
        if self.scene_name != "":
            query_map['name'] = self.scene_name
        if self.scene_region != "":
            query_map['name'] = self.scene_region
        if self.scene_tag != "":
            query_map['tags'] = self.scene_tag.split(",")
        if self.scene_lat > -9998.0:
            query_map['latitude'] = self.scene_lat
        if self.scene_lon > -9998.0:
            query_map['longitude'] = self.scene_lon

        # execute a request to Aesel
        addon_prefs = context.user_preferences.addons[__name__].preferences
        r = requests.post(addon_prefs.aesel_addr + '/v1/scene/data', json=query_map)
        # Parse response JSON
        print(r)
        response_json = r.json()
        print(response_json)

        context.scene.aesel_current_scenes.clear()
        for scene in response_json['scenes']:
            # Populate the Scene List in the UI
            new_item = context.scene.aesel_current_scenes.add()
            new_item.name = scene['name']
            print(scene)

        # Let's blender know the operator is finished
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

# Update the selected scene in the Scene List
class UpdateAeselScene(bpy.types.Operator):
    bl_idname = "object.update_aesel_scene"
    bl_label = "Update Scene"
    bl_options = {'REGISTER', 'UNDO'}
    scene_name = bpy.props.StringProperty(name="Scene Name", default="")
    scene_region = bpy.props.StringProperty(name="Scene Region", default="")
    scene_tag = bpy.props.StringProperty(name="Scene Tags", default="")
    scene_lat = bpy.props.FloatProperty(name="Scene Latitude", default=-9999.0)
    scene_lon = bpy.props.FloatProperty(name="Scene Longitude", default=-9999.0)

    # Called when operator is run
    def execute(self, context):
        selected_name = get_selected_scene(context)
        # Build an Adrestia Query Map
        query_map = {}
        if self.scene_region != "":
            query_map['region'] = self.scene_region
        if self.scene_name != "":
            query_map['name'] = self.scene_name
        if self.scene_tag != "":
            query_map['tags'] = self.scene_tag.split(",")
        if self.scene_lat > -9998.0:
            query_map['latitude'] = self.scene_lat
        if self.scene_lon > -9998.0:
            query_map['longitude'] = self.scene_lon

        # execute a request to Aesel
        addon_prefs = context.user_preferences.addons[__name__].preferences
        r = requests.post(addon_prefs.aesel_addr + '/v1/scene/' + selected_name, json=query_map)
        # Parse response JSON
        print(r)
        response_json = r.json()
        print(response_json)

        # Let's blender know the operator is finished
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

# Register to the selected scene in the scene list
class RegisterAeselDevice(bpy.types.Operator):
    bl_idname = "object.register_aesel_device"
    bl_label = "Register"
    bl_options = {'REGISTER', 'UNDO'}

    # Called when operator is run
    def execute(self, context):
        selected_name = get_selected_scene(context)

        # execute a request to Aesel
        addon_prefs = context.user_preferences.addons[__name__].preferences
        payload = {'device_id': addon_prefs.device_id, 'hostname': addon_prefs.udp_host, 'port': addon_prefs.udp_port}
        r = requests.put(addon_prefs.aesel_addr + '/v1/scene/' + selected_name + 'registration', params=payload)
        # Parse response JSON
        print(r)
        response_json = r.json()
        print(response_json)
        # Let's blender know the operator is finished
        return {'FINISHED'}

# TO-DO: Save the selected objects as scene assets
class SaveSceneAssets(bpy.types.Operator):
    bl_idname = "object.save_scene_assets"
    bl_label = "Save Scene Assets"
    bl_options = {'REGISTER', 'UNDO'}

    # Called when operator is run
    def execute(self, context):

        # Let's blender know the operator is finished
        return {'FINISHED'}

# Deregister from the selected scene in the scene list
class DeregisterAeselDevice(bpy.types.Operator):
    bl_idname = "object.deregister_aesel_device"
    bl_label = "Deregister"
    bl_options = {'REGISTER', 'UNDO'}

    # Called when operator is run
    def execute(self, context):
        selected_name = get_selected_scene(context)

        # execute a request to Aesel
        addon_prefs = context.user_preferences.addons[__name__].preferences
        payload = {'device_id': addon_prefs.device_id}
        r = requests.delete(addon_prefs.aesel_addr + '/v1/scene/' + selected_name + 'registration', params=payload)
        # Parse response JSON
        print(r)
        response_json = r.json()
        print(response_json)
        # Let's blender know the operator is finished
        return {'FINISHED'}

# TO-DO: Send updates on all active aesel objects in the scene
class SendAeselUpdates(bpy.types.Operator):
    bl_idname = "object.send_aesel_updates"
    bl_label = "Send Update"
    bl_options = {'REGISTER', 'UNDO'}

    # Called when operator is run
    def execute(self, context):

        # Let's blender know the operator is finished
        return {'FINISHED'}

# TO-DO: Save the active object to Aesel
class SaveAeselObject(bpy.types.Operator):
    bl_idname = "object.save_aesel_object"
    bl_label = "Save Object"
    bl_options = {'REGISTER', 'UNDO'}

    # Called when operator is run
    def execute(self, context):

        # Let's blender know the operator is finished
        return {'FINISHED'}

# TO-DO: Delete the active object from Aesel
class DeleteAeselObject(bpy.types.Operator):
    bl_idname = "object.delete_aesel_object"
    bl_label = "Delete Object"
    bl_options = {'REGISTER', 'UNDO'}

    # Called when operator is run
    def execute(self, context):

        # Let's blender know the operator is finished
        return {'FINISHED'}

class SceneSettingItem(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="Scene Name", default="test")

def register():
    bpy.utils.register_class(BlenderSyncPreferences)
    bpy.utils.register_class(SceneSettingItem)
    bpy.types.Scene.aesel_current_scenes = bpy.props.CollectionProperty(type=SceneSettingItem)
    bpy.types.Scene.aesel_auto_updates = bpy.props.BoolProperty(name="Sync Auto Updates", update=set_aesel_auto_update)
    bpy.types.Scene.aesel_update_rate = bpy.props.FloatProperty(name="Sync Rate", update=set_aesel_auto_update)
    bpy.types.Scene.list_index = bpy.props.IntProperty(name = "Index for aesel_current_scenes", default = 0)
    bpy.utils.register_class(DeleteAeselObject)
    bpy.utils.register_class(SaveAeselObject)
    bpy.utils.register_class(SendAeselUpdates)
    bpy.utils.register_class(DeregisterAeselDevice)
    bpy.utils.register_class(RegisterAeselDevice)
    bpy.utils.register_class(UpdateAeselScene)
    bpy.utils.register_class(FindAeselScenes)
    bpy.utils.register_class(DeleteAeselScene)
    bpy.utils.register_class(AddAeselScene)
    bpy.utils.register_class(SaveSceneAssets)
    bpy.utils.register_class(LoadAeselConfig)
    bpy.utils.register_class(SaveAeselConfig)
    bpy.utils.register_class(AeselObjectPanel)
    bpy.utils.register_class(Scene_List)
    bpy.utils.register_class(AeselScenePanel)
    bpy.utils.register_class(BlenderSyncPanel)

def unregister():
    bpy.utils.unregister_class(BlenderSyncPanel)
    bpy.utils.unregister_class(AeselScenePanel)
    bpy.utils.unregister_class(Scene_List)
    bpy.utils.unregister_class(AeselObjectPanel)
    bpy.utils.unregister_class(SaveAeselConfig)
    bpy.utils.unregister_class(LoadAeselConfig)
    bpy.utils.unregister_class(SaveSceneAssets)
    bpy.utils.unregister_class(AddAeselScene)
    bpy.utils.unregister_class(DeleteAeselScene)
    bpy.utils.unregister_class(FindAeselScenes)
    bpy.utils.unregister_class(UpdateAeselScene)
    bpy.utils.unregister_class(RegisterAeselDevice)
    bpy.utils.unregister_class(DeregisterAeselDevice)
    bpy.utils.unregister_class(SendAeselUpdates)
    bpy.utils.unregister_class(SaveAeselObject)
    bpy.utils.unregister_class(DeleteAeselObject)
    del bpy.types.Scene.aesel_current_scenes
    del bpy.types.Scene.aesel_auto_updates
    del bpy.types.Scene.aesel_update_rate
    del bpy.types.Scene.list_index
    bpy.utils.unregister_class(SceneSettingItem)
    bpy.utils.unregister_class(BlenderSyncPreferences)

if __name__ == "__main__":
    register()
