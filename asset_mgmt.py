import bpy
import os
from datetime import datetime
from aesel.model.AeselAssetMetadata import AeselAssetMetadata

# Create an Asset by exporting to obj
# This should be called from the 3d view in Object mode
class CreateObjAsset(bpy.types.Operator):
    bl_idname = "object.create_obj_asset"
    bl_label = "Selected to Asset"
    bl_description = "Export selected objects to an .obj file and save this to Aesel"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        # Create the Asset Metadata
        metadata = AeselAssetMetadata()
        metadata.asset_type = ""
        metadata.content_type = "text/plain"
        metadata.file_type = "obj"
        
        # Export the blender object to an Obj file
        blend_file_path = bpy.data.filepath
        directory = os.path.dirname(blend_file_path)
        target_file = os.path.join(directory, 'asset-' + str(datetime.now()) + '.obj')
        bpy.ops.export_scene.obj(filepath=target_file, axis_up='Y', use_selection=True,
                                 use_mesh_modifiers=True, use_edges=True, use_normals=True,
                                 use_uvs=True, use_materials=True, use_nurbs=True,
                                 use_blen_objects=True, group_by_object=True, keep_vertex_order=True, global_scale=1)

        # Post the file to Aesel
        new_key = bpy.types.Scene.transaction_client.create_asset(target_file, metadata)
        print("Exported New Asset with Key %s" % new_key)
        return {"FINISHED"}

class AeselAssetMgmtPanel(bpy.types.Panel):
    bl_idname = "aesel_asset_mgmt_panel"
    bl_label = "Aesel Asset Mgmt"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.create_obj_asset")
