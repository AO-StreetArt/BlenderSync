.. _install:

Blender Sync Testing
====================

BlenderSync is a Blender implementation of the AeselAnimationClient, which means
that primary testing is done through `Travis CI <https://travis-ci.org/AO-StreetArt/AeselAnimationClient>`__
against that repository:

Blender API Wrapper Tests
-------------------------

A test operator is provided which can be used to run unit and integration tests
within Blender.  Open the provided 'test.blend' file, enable the BlenderSync
addon, and then use the F3 search menu to run 'Test BlenderSync'.
