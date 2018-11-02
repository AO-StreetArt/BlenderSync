Object Management
=================

Object Management is primarily accomplished through existing Blender functions.
Users will typically interact with objects (ie. moving them around, assigning
keyframes, etc), and BlenderSync will replicate these objects behind the scenes.

Some operators will be added, however, to perform CRUD operations on Objects in
the remote server.  These operators will always work on the selected objects
in the Blender UI, so will still primarily be driven by normal usage of Blender.

Object Replication
------------------

All Objects within a scene are replicated by sending UDP updates periodically for
any updated objects within that scene.  These updates are sent to the address
returned from scene registration, which is performed when a scene is loaded into
the Blender interface.

Operators Overview
------------------

* Create Object - Save the selected Blender Object(s) to the Aesel servers
* Update Object - Overwrite the attributes of the selected object in the Aesel servers
* Delete Object - Delete the Aesel Objects corresponding to the selected objects

UI Overview
-----------

The only required UI for Object Management is a toolbar showing the object operators.
