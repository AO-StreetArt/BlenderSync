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

# Scene UI List
class VIEW_3D_UL_Scene_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
        layout.label(text=item.key)
        layout.label(text=item.name)

# Scene Panel
class VIEW_3D_PT_AeselScenePanel(bpy.types.Panel):
    """Creates an Aesel Scene UI Panel"""
    bl_label = "Aesel Scenes"
    bl_idname = "VIEW_3D_PT_aesel_scene_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Aesel'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.find_aesel_scenes")
        row = layout.row()
        row.template_list("VIEW_3D_UL_Scene_List", "SceneList", context.scene, "aesel_current_scenes", context.scene, "list_index")
        row = layout.row()
        row.operator("object.add_aesel_scene")
        row = layout.row()
        row.operator("object.update_aesel_scene")
        row = layout.row()
        row.operator("object.delete_aesel_scene")
        row = layout.row()
        row.operator("object.register_aesel_device")
        row = layout.row()
        row.operator("object.deregister_aesel_device")
        row = layout.row()
        row.operator("object.save_scene_asset")
