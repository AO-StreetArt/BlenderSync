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
    def get_addon_preferences():
        return bpy.context.preferences.addons["BlenderSync"].preferences

    def get_executable_filepath():
        return bpy.data.filepath

    def get_current_scene_name():
        return bpy.context.scene.current_scene_name

    def set_current_scene_name(new_name):
        bpy.context.scene.current_scene_name = new_name

    # Get the scene currently selected in the scene list
    def get_selected_scene():
        return bpy.context.scene.aesel_current_scenes[bpy.context.scene.list_index].key

    # Get the scene currently selected in the scene list
    def get_selected_scene_name():
        return bpy.context.scene.aesel_current_scenes[bpy.context.scene.list_index].name
