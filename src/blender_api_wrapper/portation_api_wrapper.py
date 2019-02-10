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

class PortationApiWrapper(object):
    def import_obj_file(self, filename):
        bpy.ops.import_scene.obj(filepath=filename)

    def export_obj_file(self, filename):
        bpy.ops.export_scene.obj(filepath=filename, axis_up='Y', use_selection=False,
                                 use_mesh_modifiers=True, use_edges=True, use_normals=True,
                                 use_uvs=True, use_materials=True, use_nurbs=True,
                                 use_blen_objects=True, group_by_object=True, keep_vertex_order=True, global_scale=1)

    def import_blend_file(self, filename, data_name):
        data_from = None
        data_to = None
        with bpy.data.libraries.load(filename) as (data_from, data_to):
            if data_name is not None:
                data_to.objects = [name for name in data_from.objects if data_name in name]
            else:
                data_to.objects = [name for name in data_from.objects]

        # Link the data to the current scene
        if data_to is not None:
            for obj in data_to.objects:
                if obj is not None:
                    bpy.context.scene.objects.link(obj)

    def export_blend_file(self, filename):
        bpy.ops.wm.save_as_mainfile(filepath=filename, copy=True)
