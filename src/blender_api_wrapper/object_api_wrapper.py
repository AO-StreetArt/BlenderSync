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

class Object3dInterface(object):
    def __init__(self, blender_object):
        self.blender_obj_ref = blender_object

    def get_name(self):
        return self.blender_obj_ref.name

    def set_name(self, new_name):
        self.blender_obj_ref.name = new_name

    def get_property(self, prop_name):
        return self.blender_obj_ref[prop_name]

    def set_property(self, prop_name, prop_val):
        self.blender_obj_ref[prop_name] = prop_val

    def set_transform(self, transform):
        self.blender_obj_ref.matrix_world = bpy.mathutils.Matrix(([transform[0], transform[1], transform[2], transform[3]],
                                                                  [transform[4], transform[5], transform[6], transform[7]],
                                                                  [transform[8], transform[9], transform[10], transform[11]],
                                                                  [transform[12], transform[13], transform[14], transform[15]]))

class ObjectApiWrapper(object):
    # Get the active object within a Blender context
    def get_active_object(self):
        active_obj = None
        for o in bpy.context.scene.objects:
            if o.select_get():
                return Object3dInterface(o)
