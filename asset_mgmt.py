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
import os
from datetime import datetime

from aesel.AeselTransactionClient import AeselTransactionClient
from aesel.model.AeselAssetMetadata import AeselAssetMetadata

# Imports

def import_obj_asset(ops):
    # Import the obj file using the built-in operator
    filename = ops["filename"]
    imported_object = bpy.ops.import_scene.obj(filepath=filename)
    imported_blender_object = bpy.context.selected_objects[0]
    print('Imported Name %s' % imported_blender_object.name)

def import_blend_asset(ops):
    filename = ops["filename"]
    data_name = None
    if "dataname" in ops:
        data_name = ops["dataname"]

    # Load the data from the blend file
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

# Monitor a queue of filenames for assets to import
def import_asset_monitor():
    while not bpy.context.scene.aesel_imports_queue.empty():
        data_dict = bpy.context.scene.aesel_imports_queue.get()

        # Actually perform the import
        if data_dict["filename"].endswith(".obj"):
            import_obj_asset(data_dict)
        elif data_dict["filename"].endswith(".blend"):
            import_blend_asset(data_dict)
    return 1.0

# Import UI
# The import UI is only going to deal with local files until the Asset Engine API
# is finalized.  At that point, we can convert a lot of this into an Asset Engine
# for Aesel.

class OBJECT_OT_AddFile(Operator):
    bl_idname = "object.add_file"
    bl_label = "Add File"

    filepath: StringProperty()

    @classmethod
    def poll(cls, context):
        op = context.active_operator
        return op.filepath not in (f.name for f in op.file_list)

    def execute(self, context):
        item = context.active_operator.file_list.add()
        item.name = self.filepath
        return {'FINISHED'}

class OBJECT_OT_AddFiles(Operator):
    bl_idname = "object.add_files"
    bl_label = "Add Files"

    filepaths: CollectionProperty(type=bpy.types.PropertyGroup)

    def execute(self, context):
        file_list = context.active_operator.file_list

        for fp in self.filepaths:
            if fp.name not in (f.name for f in file_list):
                item = file_list.add()
                item.name = fp.name
        return {'FINISHED'}

class OBJECT_OT_RemoveFile(Operator):
    bl_idname = "object.remove_file"
    bl_label = "Remove File"

    index: IntProperty()

    @classmethod
    def poll(cls, context):
        return len(context.active_operator.file_list) > 0

    def execute(self, context):
        try:
            context.active_operator.file_list.remove(self.index)
        except IndexError:
            pass
        return {'FINISHED'}

class OBJECT_OT_ImportAssets(Operator, ExportHelper):
    bl_idname = "object.import_assets"
    bl_label = "Import Assets"
    bl_description = "Import a set of Assets to your local Scene"
    bl_options = {"REGISTER"}

    # ExportHelper mixin class uses this
    filename_ext = ".jpg"

    filter_glob: StringProperty(
            default="*.jpg",
            options={'HIDDEN'},
            )

    # special prop, blender fills it with all selected files if present
    files: CollectionProperty(type=bpy.types.PropertyGroup)

    file_list: CollectionProperty(type=bpy.types.PropertyGroup)
    file_list_index: IntProperty()

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.label(text=bpy.path.basename(self.filepath))

        row.operator(AddFile.bl_idname, icon='ADD').filepath = self.filepath

        props = row.operator(AddFiles.bl_idname, icon='ADD')
        folder = dirname(self.filepath)
        for f in self.files:
            item = props.filepaths.add()
            item.name = join(folder, f.name)

        row.operator(RemoveFile.bl_idname, icon='REMOVE', text="").index = self.file_list_index

        layout.template_list("UI_UL_list", "OBJECT_OT_AddFiles", self, "file_list", self, "file_list_index")

    def execute(self, context):
        # Put the selected file names onto the import queue for processing
        for f in self.file_list:
            bpy.context.scene.aesel_imports_queue.put({"filename": f})
        return {'FINISHED'}

# Exports

# Get the root file path for assets
def get_root_file_path():
    # Get the base file path
    addon_prefs = context.preferences.addons[__package__].preferences
    base_file_path = None
    if addon_prefs.asset_file_location == ".":
        base_file_path = os.path.dirname(bpy.data.filepath)
    else:
        base_file_path = os.path.dirname(addon_prefs.asset_file_location)

    # Join the base file path with the scene
    current_scene_name = bpy.context.scene.current_scene_name
    if current_scene_name != "":
        target = os.path.join(base_file_path, current_scene_name)
    else:
        target = os.path.join(base_file_path, "default")

    # If the target directory doesn't exist, create it
    if not os.path.exists(target):
        os.makedirs(target)

    # Return the target directory
    return target

# Generate an instance of asset metadata to save
def gen_asset_metadata(name, file_type, public):
    metadata = AeselAssetMetadata()
    metadata.name = name
    metadata.asset_type = "Blender"
    metadata.content_type = "text/plain"
    metadata.file_type = file_type
    metadata.isPublic = public
    return metadata

# Save the full current scene in Blender to Aesel as an asset
def save_scene_as_blend_asset(name, public):
    # Create the Asset Metadata
    metadata = gen_asset_metadata(name, "blend", public)

    # Determine the base path to save to
    root_file_path = get_root_file_path()

    # Export the blender object to a blend file
    target_file = os.path.join(root_file_path, name + '.blend')
    bpy.ops.wm.save_as_mainfile(filepath=target_file, copy=True)

    # Post the file to Aesel
    new_asset_key = bpy.types.Scene.transaction_client.create_asset(target_file, metadata)

    return new_asset_key

# Export the selected objects as a .obj Asset
# The resulting file name should be 'new_key.obj'
def save_selected_as_obj_asset(name, public):
    # Create the Asset Metadata
    metadata = gen_asset_metadata(name, "obj", public)

    # Determine the base path to save to
    root_file_path = get_root_file_path()

    # Export the blender object to an Obj file
    target_file = os.path.join(root_file_path, name + '.obj')
    bpy.ops.export_scene.obj(filepath=target_file, axis_up='Y', use_selection=True,
                             use_mesh_modifiers=True, use_edges=True, use_normals=True,
                             use_uvs=True, use_materials=True, use_nurbs=True,
                             use_blen_objects=True, group_by_object=True, keep_vertex_order=True, global_scale=1)

    # Post the file to Aesel
    new_asset_key = bpy.types.Scene.transaction_client.create_asset(target_file, metadata)

    print("Exported New Asset with Key %s" % new_asset_key)


# Create an Asset by exporting to obj
# This should be called from the 3d view in Object mode
class OBJECT_OT_CreateObjAsset(bpy.types.Operator):
    bl_idname = "object.create_obj_asset"
    bl_label = "Selected to Asset"
    bl_description = "Export selected objects to an .obj file and save this to Aesel"
    bl_options = {"REGISTER"}
    asset_name: bpy.props.StringProperty(name="Asset Name", default="")
    asset_public: bpy.props.BoolProperty(name="Is Asset Public?", default=True)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        # Post the file to Aesel on a background thread
        recv_thread = threading.Thread(target=save_selected_as_obj_asset, args=(asset_name, asset_public))
        recv_thread.daemon = True
        recv_thread.start()
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


# Create an Asset by exporting to blend
# This should be called from the 3d view in Object mode
class OBJECT_OT_CreateBlendAsset(bpy.types.Operator):
    bl_idname = "object.create_blend_asset"
    bl_label = "Save All to Asset"
    bl_description = "Export selected objects to a .blend file and save this to Aesel"
    bl_options = {"REGISTER"}
    asset_name: bpy.props.StringProperty(name="Asset Name", default="")
    asset_public: bpy.props.BoolProperty(name="Is Asset Public?", default=True)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        # Post the file to Aesel on a background thread
        recv_thread = threading.Thread(target=save_scene_as_blend_asset, args=(asset_name, asset_public))
        recv_thread.daemon = True
        recv_thread.start()
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


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
        layout.label(text="Import")
        layout.operator("object.import_assets")
