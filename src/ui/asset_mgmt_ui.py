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

class VIEW_3D_PT_AeselAssetMgmtPanel(bpy.types.Panel):
    bl_idname = "VIEW_3D_PT_aesel_asset_mgmt_panel"
    bl_label = "Aesel Assets"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Aesel"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Export")
        layout.operator("object.create_obj_asset")
        layout.operator("object.create_blend_asset")
