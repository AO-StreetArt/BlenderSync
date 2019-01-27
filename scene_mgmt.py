import bpy

from .asset_mgmt import save_selected_as_obj_asset

from aesel.AeselTransactionClient import AeselTransactionClient
from aesel.model.AeselScene import AeselScene
from aesel.model.AeselAssetRelationship import AeselAssetRelationship
from aesel.model.AeselUserDevice import AeselUserDevice
from aesel.model.AeselObject import AeselObject

# Scene UI List
class VIEW_3D_UL_Scene_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
        layout.label(text=item.key)
        layout.label(text=item.name)

# Get the scene currently selected in the scene list
def get_selected_scene(context):
    return context.scene.aesel_current_scenes[context.scene.list_index].key

# Get the scene currently selected in the scene list
def get_selected_scene_name(context):
    return context.scene.aesel_current_scenes[context.scene.list_index].name

# Add a new Scene to the Scene List
class OBJECT_OT_AddAeselScene(bpy.types.Operator):
    bl_idname = "object.add_aesel_scene"
    bl_label = "Create Scene"
    bl_options = {'REGISTER'}
    scene_key: bpy.props.StringProperty(name="Scene Key", default="First")
    scene_name: bpy.props.StringProperty(name="Scene Name", default="Default")
    scene_tag: bpy.props.StringProperty(name="Scene Tags", default="")

    # Called when operator is run
    def execute(self, context):
        # Build a new Aesel scene
        new_scene = AeselScene()
        if self.scene_name != "":
            new_scene.name = self.scene_name
        if self.scene_tag != "":
            new_scene.tags = self.scene_tag.split(",")

        # execute a request to Aesel
        response_json = bpy.types.Scene.transaction_client.create_scene(self.scene_key, new_scene)
        print(response_json)

        # Let's blender know the operator is finished
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

# Add a new Scene to the Scene List
class OBJECT_OT_UpdateAeselScene(bpy.types.Operator):
    bl_idname = "object.update_aesel_scene"
    bl_label = "Update Scene"
    bl_options = {'REGISTER'}
    scene_name: bpy.props.StringProperty(name="Scene Name", default="")
    scene_tag: bpy.props.StringProperty(name="Scene Tags", default="")

    # Called when operator is run
    def execute(self, context):
        # Get the key of the selected scene in the list
        selected_key = get_selected_scene(context)

        # Build a new Aesel scene
        new_scene = AeselScene()
        if self.scene_name != "":
            new_scene.name = self.scene_name
        if self.scene_tag != "":
            new_scene.tags = self.scene_tag.split(",")

        # execute a request to Aesel
        response_json = bpy.types.Scene.transaction_client.update_scene(selected_key, new_scene)
        print(response_json)

        # Let's blender know the operator is finished
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

# Delete a Scene from Aesel and the Scene List
class OBJECT_OT_DeleteAeselScene(bpy.types.Operator):
    bl_idname = "object.delete_aesel_scene"
    bl_label = "Delete Scene"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):

        # execute a request to Aesel
        selected_key = get_selected_scene(context)
        response_json = bpy.types.Scene.transaction_client.delete_scene(selected_key)
        print(response_json)

        # Let's blender know the operator is finished
        return {'FINISHED'}

# Populate the Scene list based on a query
class OBJECT_OT_FindAeselScenes(bpy.types.Operator):
    bl_idname = "object.find_aesel_scenes"
    bl_label = "Find Scenes"
    bl_options = {'REGISTER'}
    scene_name: bpy.props.StringProperty(name="Scene Name", default="")
    scene_tag: bpy.props.StringProperty(name="Scene Tags", default="")

    # Called when operator is run
    def execute(self, context):
        # Build a new Aesel scene
        new_scene = AeselScene()
        if self.scene_name != "":
            new_scene.name = self.scene_name
        if self.scene_tag != "":
            new_scene.tags = self.scene_tag.split(",")

        # execute a request to Aesel
        response_json = bpy.types.Scene.transaction_client.scene_query(new_scene)
        print(response_json)

        context.scene.aesel_current_scenes.clear()
        for scene in response_json['scenes']:
            # Populate the Scene List in the UI
            new_item = context.scene.aesel_current_scenes.add()
            new_item.name = scene['name']
            new_item.key = scene['key']
            print(scene)

        # Let's blender know the operator is finished
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

# Register to the selected scene in the scene list
class OBJECT_OT_RegisterAeselDevice(bpy.types.Operator):
    bl_idname = "object.register_aesel_device"
    bl_label = "Register"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        context.scene.current_scene_id = get_selected_scene(context)
        context.scene.current_scene_name = get_selected_scene_name(context)

        # Send the registration request
        addon_prefs = context.preferences.addons[__package__].preferences
        device = AeselUserDevice()
        device.key = addon_prefs.device_id
        device.hostname = addon_prefs.advertised_udp_host
        device.port = addon_prefs.udp_port
        response_json = bpy.types.Scene.transaction_client.register(selected_key, device)
        print(response_json)

        # Get Assets related to the Scene
        scene_relationship_query = AeselAssetRelationship()
        scene_relationship_query.related = selected_key
        scene_relationship_query.type = "scene"
        scene_relation_response = bpy.types.Scene.transaction_client.query_asset_relationships(scene_relationship_query)

        # Download Scene Assets
        for asset in scene_relation_response:
            content = bpy.types.Scene.transaction_client.get_asset(asset["assetId"])
            filename = 'asset-%s' % asset["assetId"]
            with open(filename, 'wb') as asset_file:
                asset_file.write(content)

            # Import the scene asset
            imported_object = bpy.ops.import_scene.obj(filepath=filename)
            imported_blender_object = bpy.context.selected_objects[0]
            print('Imported Name %s' % imported_blender_object.name)

        # Download Objects
        obj_query = AeselObject()
        obj_query.scene = selected_key
        object_response_json = bpy.types.Scene.transaction_client.object_query(selected_key, obj_query)
        print(object_response_json)

        for record in object_response_json['objects']:

            # Find Assets related to the object
            obj_relationship_query = AeselAssetRelationship()
            obj_relationship_query.related = record["key"]
            obj_relationship_query.type = "object"
            obj_relation_result = bpy.types.Scene.transaction_client.query_asset_relationships(obj_relationship_query)

            # Download Object Assets
            for asset in obj_relation_result:
                content = bpy.types.Scene.transaction_client.get_asset(asset["assetId"])
                filename = 'asset-%s' % asset["assetId"]
                with open(filename, 'wb') as asset_file:
                    asset_file.write(r.content)

                # Import the object asset
                imported_object = bpy.ops.import_scene.obj(filepath=filename)
                imported_blender_object = bpy.context.selected_objects[0]
                print('Imported Name %s' % imported_blender_object.name)

                # Update object attributes
                imported_blender_object.name = record['name']
                imported_blender_object['key'] = record["key"]

                # Apply object transforms
                transform = mathutils.Matrix.Identity(4)
                for i in range(16):
                    transform[int(i/4)][i%4] = record['transform'][i]
                imported_blender_object.matrix_world = transform*imported_blender_object.matrix_world

        # Let's blender know the operator is finished
        return {'FINISHED'}

# Deregister from the selected scene in the scene list
class OBJECT_OT_DeregisterAeselDevice(bpy.types.Operator):
    bl_idname = "object.deregister_aesel_device"
    bl_label = "Deregister"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        selected_key = get_selected_scene(context)

        # execute a request to Aesel
        addon_prefs = context.preferences.addons[__package__].preferences
        response_json = bpy.types.Scene.transaction_client.deregister(selected_key, addon_prefs.device_id)
        print(response_json)
        # Let's blender know the operator is finished
        return {'FINISHED'}

# Save the selected objects as scene assets
class OBJECT_OT_SaveSceneAsset(bpy.types.Operator):
    bl_idname = "object.save_scene_asset"
    bl_label = "Save Scene Asset"
    bl_options = {'REGISTER'}

    # Called when operator is run
    def execute(self, context):
        # Post the file to Aesel
        new_key = save_selected_as_obj_asset()
        print("Exported New Asset with Key %s" % new_key)

        # Post a new Asset Relationship
        new_relation = AeselAssetRelationship()
        new_relation.asset = new_key
        new_relation.type = "scene"
        new_relation.related = get_selected_scene(context)
        response_json = bpy.types.Scene.transaction_client.save_asset_relationship(new_relation)

        print(response_json)

        # Let's blender know the operator is finished
        return {'FINISHED'}

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
        row.operator("object.update_aesel_scene")
        row = layout.row()
        row.operator("object.delete_aesel_scene")
        row = layout.row()
        row.operator("object.register_aesel_device")
        row.operator("object.deregister_aesel_device")
        row = layout.row()
        row.operator("object.save_scene_asset")
