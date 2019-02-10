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

class GeneralApiWrapper(object):
    def get_addon_preferences(self):
        return bpy.context.preferences.addons["BlenderSync"].preferences

    def get_executable_filepath(self):
        return bpy.app.binary_path

    def get_current_scene_id(self):
        return bpy.context.scene.current_scene_id

    def set_current_scene_id(self, new_id):
        bpy.context.scene.current_scene_id = new_id

    def get_current_scene_name(self):
        return bpy.context.scene.current_scene_name

    def set_current_scene_name(self, new_name):
        bpy.context.scene.current_scene_name = new_name

    # Get the scene currently selected in the scene list
    def get_selected_scene(self):
        return bpy.context.scene.aesel_current_scenes[bpy.context.scene.list_index].key

    # Get the scene currently selected in the scene list
    def get_selected_scene_name(self):
        return bpy.context.scene.aesel_current_scenes[bpy.context.scene.list_index].name

    def add_to_scenes_ui_list(self, name, key):
        new_item = bpy.context.scene.aesel_current_scenes.add()
        new_item.name = name
        new_item.key = key

    def update_scenes_ui_list(self, name, key):
        for index, item in enumerate(bpy.context.scene.aesel_current_scenes):
            if key == item.key:
                bpy.context.scene.aesel_current_scenes[index].name = name

    def remove_from_scenes_ui_list(self, key):
        for index, item in enumerate(bpy.context.scene.aesel_current_scenes):
            if key == item.key:
                bpy.context.scene.aesel_current_scenes.remove(index)

    def clear_scenes_ui_list(self):
        bpy.context.scene.aesel_current_scenes.clear()

    def is_udp_listener_active(self):
        return bpy.context.scene.aesel_listen_live

    def set_udp_listener_active(self, new_active):
        bpy.context.scene.aesel_listen_live = new_active

    def is_udp_sender_active(self):
        return bpy.context.scene.aesel_updates_live

    def set_udp_sender_active(self, new_active):
        bpy.context.scene.aesel_updates_live = new_active
