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

    def get_type(self):
        return self.blender_obj_ref.type

    def set_type(self, new_type):
        self.blender_obj_ref.type = new_type

    def get_parent(self):
        return Object3dInterface(self.blender_obj_ref.parent)

    def set_parent(self, new_parent):
        self.blender_obj_ref.parent = new_parent.blender_obj_ref

    def get_property(self, prop_name):
        return self.blender_obj_ref[prop_name]

    def set_property(self, prop_name, prop_val):
        self.blender_obj_ref[prop_name] = prop_val

    def set_selection(self, selection):
        self.blender_obj_ref.select_set(selection)

    def selected(self):
        return self.blender_obj_ref.select_get()

    def get_location_x(self):
        return self.blender_obj_ref.location.x

    def set_location_x(self, new_loc):
        self.blender_obj_ref.location.x = new_loc

    def get_location_y(self):
        return self.blender_obj_ref.location.y

    def set_location_y(self, new_loc):
        self.blender_obj_ref.location.y = new_loc

    def get_location_z(self):
        return self.blender_obj_ref.location.z

    def set_location_z(self, new_loc):
        self.blender_obj_ref.location.z = new_loc

    def get_erotation_x(self):
        return self.blender_obj_ref.rotation_euler.x

    def set_erotation_x(self, new_rot):
        self.blender_obj_ref.rotation_euler.x = new_rot

    def get_erotation_y(self):
        return self.blender_obj_ref.rotation_euler.y

    def set_erotation_y(self, new_rot):
        self.blender_obj_ref.rotation_euler.y = new_rot

    def get_erotation_z(self):
        return self.blender_obj_ref.rotation_euler.z

    def set_erotation_z(self, new_rot):
        self.blender_obj_ref.rotation_euler.z = new_rot

    def get_scale_x(self):
        return self.blender_obj_ref.scale.x

    def set_scale_x(self, new_scl):
        self.blender_obj_ref.scale.x = new_scl

    def get_scale_y(self):
        return self.blender_obj_ref.scale.y

    def set_scale_y(self, new_scl):
        self.blender_obj_ref.scale.y = new_scl

    def get_scale_z(self):
        return self.blender_obj_ref.scale.z

    def set_scale_z(self, new_scl):
        self.blender_obj_ref.scale.z = new_scl

    def set_transform(self, transform):
        self.blender_obj_ref.matrix_world = bpy.mathutils.Matrix(([transform[0], transform[1], transform[2], transform[3]],
                                                                  [transform[4], transform[5], transform[6], transform[7]],
                                                                  [transform[8], transform[9], transform[10], transform[11]],
                                                                  [transform[12], transform[13], transform[14], transform[15]]))

    def get_transform(self):
        return self.blender_obj_ref.matrix_world

class ObjectApiWrapper(object):
    # Get the active object within a Blender context
    def get_active_object(self):
        active_obj = None
        for o in bpy.context.scene.objects:
            if o.select_get():
                return Object3dInterface(o)

    def get_object_by_name(self, name):
        return Object3dInterface(bpy.data.objects[name])

    def delete_selected_objects(self):
        bpy.ops.object.delete()

    def iterate_over_all_objects(self):
        for object in bpy.data.objects:
            yield Object3dInterface(object)

    def iterate_over_selected_objects(self):
        active_obj = None
        for o in bpy.context.scene.objects:
            if o.select_get():
                yield Object3dInterface(o)

    def select_all(self):
        bpy.ops.object.select_all(action='SELECT')

    def add_live_object(self, name, key):
        bpy.context.scene.aesel_live_objects.append((key, name))

    def remove_live_object(self, name, key):
        bpy.context.scene.aesel_live_objects.remove((key, name))

    def iterate_over_live_objects(self):
        for obj in bpy.context.scene.aesel_live_objects:
            yield obj
