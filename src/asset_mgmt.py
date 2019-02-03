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

import os

from .bsync_utils import get_assets_file_path

from aesel.model.AeselAssetMetadata import AeselAssetMetadata

# Imports

def import_obj_asset(object_api_wrapper, portation_api_wrapper, ops):
    # Import the obj file using the built-in operator
    portation_api_wrapper.import_obj_file(ops["filename"])
    imported_blender_object = object_api_wrapper.get_active_object()

    print('Imported Name %s' % imported_blender_object.get_name())

    # Update object attributes
    if "name" in ops:
        imported_blender_object.set_name(ops["name"])
    if "key" in ops:
        imported_blender_object.set_property("key", ops["key"])

    # Apply object transforms
    if "transform" in ops:
        imported_blender_object.set_transform(ops["transform"])

def import_blend_asset(portation_api_wrapper, ops):
    filename = ops["filename"]
    data_name = None
    if "dataname" in ops:
        data_name = ops["dataname"]

    # Load the data from the blend file
    portation_api_wrapper.import_blend_file(filename, data_name)

# Exports
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
def save_scene_as_blend_asset(general_api_wrapper,
                              portation_api_wrapper,
                              transaction_client,
                              name,
                              public):
    # Create the Asset Metadata
    metadata = gen_asset_metadata(name, "blend", public)

    # Determine the base path to save to
    root_file_path = general_api_wrapper.get_assets_file_path(general_api_wrapper.get_current_scene_name(),
                                                              general_api_wrapper.get_executable_filepath(),
                                                              addon_prefs.asset_file_location)

    # Export the blender object to a blend file
    target_file = os.path.join(root_file_path, name + '.blend')
    portation_api_wrapper.export_blend_file(target_file)

    # Post the file to Aesel
    return transaction_client.create_asset(target_file, metadata)

# Export the selected objects as a .obj Asset
# The resulting file name should be 'new_key.obj'
def save_selected_as_obj_asset(general_api_wrapper,
                               portation_api_wrapper,
                               transaction_client,
                               name,
                               public,
                               export_file=True,
                               post_asset=True):
    addon_prefs = general_api_wrapper.get_addon_preferences()
    # Create the Asset Metadata
    metadata = gen_asset_metadata(name, "obj", public)

    # Determine the base path to save to
    root_file_path = get_assets_file_path(general_api_wrapper.get_current_scene_name(),
                                          general_api_wrapper.get_executable_filepath(),
                                          addon_prefs.asset_file_location)

    # Export the blender object to an Obj file
    target_file = os.path.join(root_file_path, name + '.obj')
    if export_file:
        portation_api_wrapper.export_obj_file(target_file)

    # Post the file to Aesel
    new_asset_key = None
    if post_asset:
        new_asset_key = transaction_client.create_asset(target_file, metadata)
        print("Exported New Asset with Key %s" % new_asset_key)

    return new_asset_key
