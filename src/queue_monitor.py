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

from .asset_mgmt import import_obj_asset, import_blend_asset

import bpy

# Monitor a queue for updates to make to the main viewport on the main thread.
def aesel_queue_monitor():
    while not bpy.context.scene.aesel_updates_queue.empty():
        data_dict = bpy.context.scene.aesel_updates_queue.get()
        print("Processing Data on main thread: %s" % data_dict)

        if data_dict['type'] == 'live_update':
            obj = bpy.data.objects[data_dict['name']]
            transform = data_dict['transform']
            obj.matrix_world = mathutils.Matrix(([transform[0], transform[1], transform[2], transform[3]],
                                                [transform[4], transform[5], transform[6], transform[7]],
                                                [transform[8], transform[9], transform[10], transform[11]],
                                                [transform[12], transform[13], transform[14], transform[15]]))
        elif data_dict['type'] == 'list_add':
            # Populate the Scene List in the UI
            new_item = bpy.context.scene.aesel_current_scenes.add()
            new_item.name = data_dict['data'].name
            new_item.key = data_dict['data'].key

        elif data_dict['type'] == 'list_update':
            for index, item in enumerate(bpy.context.scene.aesel_current_scenes):
                if data_dict['data'].key == item.key:
                    bpy.context.scene.aesel_current_scenes[index].name = data_dict['data'].name

        elif data_dict['type'] == 'list_delete':
            for index, item in enumerate(bpy.context.scene.aesel_current_scenes):
                if data_dict['data'] == item.key:
                    bpy.context.scene.aesel_current_scenes.remove(index)

        elif data_dict['type'] == 'list_set':
            bpy.context.scene.aesel_current_scenes.clear()
            for scene in data_dict['data']['scenes']:
                # Populate the Scene List in the UI
                new_item = bpy.context.scene.aesel_current_scenes.add()
                new_item.name = scene['name']
                new_item.key = scene['key']

        elif data_dict['type'] == 'viewport_clear':
            # select all objects.
            for object in bpy.data.objects:
                bpy.data.objects[object.name].select_set(True)

            # remove all selected.
            bpy.ops.object.delete()

            # remove the meshes, they have no users anymore.
            for item in bpy.data.meshes:
                bpy.data.meshes.remove(item)

        elif data_dict['type'] == 'asset_import':
            # Actually call the import operator(s)
            if data_dict["filename"].endswith(".obj"):
                import_obj_asset(bpy.context.scene.general_api_wrapper,
                                 bpy.context.scene.portation_api_wrapper,
                                 data_dict)
            elif data_dict["filename"].endswith(".blend"):
                import_blend_asset(bpy.context.scene.general_api_wrapper,
                                   bpy.context.scene.portation_api_wrapper,
                                   data_dict)

        elif data_dict['type'] == 'lock_object':
            context.scene.aesel_live_objects.append((data_dict['obj_key'], data_dict['obj_name']))

        elif data_dict['type'] == 'unlock_object':
            context.scene.aesel_live_objects.remove((data_dict['obj_key'], data_dict['obj_name']))
    return 0.1
