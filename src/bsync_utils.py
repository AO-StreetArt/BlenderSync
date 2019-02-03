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

# Get the root file path for assets
def get_assets_file_path(current_scene_name, executable_folder, base_folder):
    # Get the base file path
    base_file_path = None
    if base_folder == ".":
        base_file_path = os.path.dirname(executable_folder)
    else:
        base_file_path = os.path.dirname(base_folder)

    # Join the base file path with the scene
    if current_scene_name != "":
        target = os.path.join(base_file_path, current_scene_name)
    else:
        target = os.path.join(base_file_path, "default")

    # If the target directory doesn't exist, create it
    if not os.path.exists(target):
        os.makedirs(target)

    # Return the target directory
    return target
