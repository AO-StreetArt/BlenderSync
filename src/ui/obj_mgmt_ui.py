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

# Object Panel
class VIEW_3D_PT_AeselObjectPanel(bpy.types.Panel):
    """Creates an Aesel Object UI Panel"""
    bl_label = "Aesel Objects"
    bl_idname = "VIEW_3D_PT_aesel_obj_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Aesel'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.create_aesel_object")
        row = layout.row()
        row.operator("object.delete_aesel_object")
        row = layout.row()
        row.operator("object.lock_aesel_object")
        row = layout.row()
        row.operator("object.unlock_aesel_object")
        row = layout.row()
        row.prop(context.scene, 'aesel_auto_updates')
        row = layout.row()
        row.prop(context.scene, 'aesel_listen_for_updates')
