import unittest
import bpy
import sys

# Install and Enable the Addon within the currently running blender instance
bpy.ops.wm.addon_install(filepath="/home/travis/build/AO-StreetArt/BlenderSync/blendersync.py")
bpy.ops.wm.addon_enable(module="blendersync")

#Import the addon for the purposes of the test script
try:
    import blendersync
except Exception as e:
    print(e)
    sys.exit(1)

class TestAddon(unittest.TestCase):
    def test_addon_enabled(self):
        self.assertIsNotNone(blendersync.bl_info)

# we have to manually invoke the test runner here
suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
unittest.TextTestRunner().run(suite)
