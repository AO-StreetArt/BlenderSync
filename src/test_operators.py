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
import traceback
import sys

from .blender_api_wrapper.general_api_wrapper import GeneralApiWrapper
from .blender_api_wrapper.object_api_wrapper import ObjectApiWrapper
from .blender_api_wrapper.portation_api_wrapper import PortationApiWrapper

def general_api_tests(context, general_api_wrapper):
    # Test Addon Preferences Access
    addon_prefs = general_api_wrapper.get_addon_preferences()
    assert(addon_prefs.aesel_addr == "http://localhost:8080")

    # Test Executable filepath access
    exec_path = general_api_wrapper.get_executable_filepath()
    assert(exec_path != "")

    # Test Current Scene access
    general_api_wrapper.set_current_scene_id("123")
    scene_id = general_api_wrapper.get_current_scene_id()
    assert(scene_id == "123")

    general_api_wrapper.set_current_scene_name("123")
    scene_name = general_api_wrapper.get_current_scene_name()
    assert(scene_name == "123")

    # Scene List tests
    general_api_wrapper.add_to_scenes_ui_list("name", "key")
    assert(len(bpy.context.scene.aesel_current_scenes) == 1)
    bpy.context.scene.list_index = 0
    assert(general_api_wrapper.get_selected_scene() == "key")
    assert(general_api_wrapper.get_selected_scene_name() == "name")

    general_api_wrapper.add_to_scenes_ui_list("name2", "key2")
    assert(len(bpy.context.scene.aesel_current_scenes) == 2)

    general_api_wrapper.update_scenes_ui_list("name3", "key")
    assert(general_api_wrapper.get_selected_scene() == "key")
    assert(general_api_wrapper.get_selected_scene_name() == "name3")

    general_api_wrapper.remove_from_scenes_ui_list("key")
    assert(len(bpy.context.scene.aesel_current_scenes) == 1)

    general_api_wrapper.clear_scenes_ui_list()
    assert(len(bpy.context.scene.aesel_current_scenes) == 0)

    # Boolean Flag tests
    general_api_wrapper.set_udp_listener_active(False)
    assert(not general_api_wrapper.is_udp_listener_active())
    general_api_wrapper.set_udp_listener_active(True)
    assert(general_api_wrapper.is_udp_listener_active())

    general_api_wrapper.set_udp_sender_active(False)
    assert(not general_api_wrapper.is_udp_sender_active())
    general_api_wrapper.set_udp_sender_active(True)
    assert(general_api_wrapper.is_udp_sender_active())

def object_api_tests(context, object_api_wrapper):
    # Create a cube as the selected, active object
    bpy.ops.mesh.primitive_cube_add(size=2, view_align=False, enter_editmode=False, location=(0, 0, 0))

    # Object Accessor Tests
    active_obj = object_api_wrapper.get_active_object()
    assert(active_obj.get_location_x() - 0.0 < 0.01)

    obj_view = object_api_wrapper.get_object_by_name(active_obj.get_name())
    assert(obj_view.get_location_x() - 0.0 < 0.01)

    # Live Object Tests
    object_api_wrapper.add_live_object(active_obj.get_name(), "123")
    assert(len(bpy.context.scene.aesel_live_objects) == 1)

    for obj in object_api_wrapper.iterate_over_live_objects():
        assert(obj[1] == active_obj.get_name())

    object_api_wrapper.remove_live_object(active_obj.get_name(), "123")
    assert(len(bpy.context.scene.aesel_live_objects) == 0)

    # Clear the viewport
    object_api_wrapper.select_all()
    object_api_wrapper.delete_selected_objects()

    # Validate that there are no objects in the viewport
    for obj in object_api_wrapper.iterate_over_all_objects():
        assert(False)

def portation_api_tests(context, portation_api_wrapper):
    # Create a cube as the selected, active object
    bpy.ops.mesh.primitive_cube_add(size=2, view_align=False, enter_editmode=False, location=(1, 1, 1))

    # Obj tests
    os.remove("test_obj_export.obj")
    portation_api_wrapper.export_obj_file("test_obj_export.obj")

    # Clear the viewport
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    portation_api_wrapper.import_obj_file("test_obj_export.obj")
    obj_name = ""
    obj_exists = False
    for o in bpy.context.scene.objects:
        if o.select_get():
            obj_name = o.name
            obj_exists = True
            assert(o.location.x - 1.0 < 0.01)
    assert(obj_exists)

    # Blend tests
    os.remove("test_blend_export.blend")
    portation_api_wrapper.export_blend_file("test_blend_export.blend")

    # Clear the viewport
    for o in bpy.context.scene.objects:
        o.select_set(True)
    bpy.ops.object.delete()

    portation_api_wrapper.import_blend_file("test_blend_export.blend", obj_name)
    obj_exists = False
    for o in bpy.context.scene.objects:
        if o.select_get():
            obj_exists = True
            assert(o.location.x - 1.0 < 0.01)
    assert(obj_exists)


def get_exc_details():
    _, _, tb = sys.exc_info()
    traceback.print_tb(tb) # Fixed format
    tb_info = traceback.extract_tb(tb)
    filename, line, func, text = tb_info[-1]
    return func, line

def print_exception_details(e):
    function, line = get_exc_details()

    print("")
    print("---Test Failure---")
    print('Unknown error in function {} at line {}:\n{}'.format(function, line, str(e)))

def print_assertion_details():
    function, line = get_exc_details()

    print("")
    print("---Test Failure---")
    print('Assertion failed in function {} at line {}'.format(function, line))

# Execute BlenderSync tests
#   this includes both API Wrapper unit tests and headless integration tests
#   this assumes that the tests are run from the 3D view with default settings
class OBJECT_OT_ExecuteBlenderSyncTests(bpy.types.Operator):
    bl_idname = "object.execute_blendersync_tests"
    bl_label = "Test BlenderSync"
    bl_description = "Run BlenderSync automated tests and view the output in the console"
    bl_options = {"REGISTER"}

    def execute(self, context):
        # Execute General API Wrapper Tests
        general_api_wrapper = context.scene.general_api_wrapper
        object_api_wrapper = context.scene.object_api_wrapper
        portation_api_wrapper = context.scene.portation_api_wrapper

        print("======Executing Blender API Tests======")
        print("")
        print("======Executing General API Tests======")
        print("")
        general_tests_success = True
        try:
            general_api_tests(context, general_api_wrapper)
        except AssertionError as e:
            print_assertion_details()
            general_tests_success = False
        except Exception as e:
            print_exception_details(e)
            general_tests_success = False

        if general_tests_success:
            print("Pass")

        print("")
        print("======Executing Object API Tests======")
        print("")
        object_tests_success = True
        try:
            object_api_tests(context, object_api_wrapper)
        except AssertionError as e:
            print_assertion_details()
            object_tests_success = False
        except Exception as e:
            print_exception_details(e)
            object_tests_success = False

        if object_tests_success:
            print("Pass")

        print("")
        print("======Executing Portation API Tests======")
        print("")
        portation_tests_success = True
        try:
            portation_api_tests(context, portation_api_wrapper)
        except AssertionError as e:
            print_assertion_details()
            portation_tests_success = False
        except Exception as e:
            print_exception_details(e)
            portation_tests_success = False

        if portation_tests_success:
            print("Pass")

        if not general_tests_success or not object_tests_success or not portation_tests_success:
            self.report({'ERROR'}, "Test Failures, please see console logs for details")
        else:
            self.report({'INFO'}, "Tests Passed")

        # Let Blender know the tests are complete
        return {"FINISHED"}
