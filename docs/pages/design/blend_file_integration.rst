Native Blend File Integration
=============================

The primary storage mechanism for the first iteration of BlenderSync will be
.blend files stored in Aesel.

This provides the required framework for more advanced workflows, by using
Asset Sub ID's and Relationship Subtypes to allow these blend files to represent
a variety of different asset types.  This means taking advantage of all of Blender's
features without having to necessarily code for each one inside the backend.

In order for .blend files to be imported, however, we need to make certain
underlying assumptions about how we are going to implement our scenes.

Basic Scene Structure
---------------------

Within each Scene, we will have a number of collections:

* One for all Scene Assets
* One for each Aesel Object at the top of a parent-child chain

Scene Assets will simply be imported into the Scene Asset Collection, but each
Object Asset will need to be imported into it's respective Collection, and potentially
linked to a parent.  Parent-child relationships will be stored in the 'parent'
field of the object in Aesel.  Each object in Aesel will correspond to an object
in a Blend File.

Sub ID's and Subtypes
---------------------

Within an Asset Relationship, an Asset Sub ID will refer to the path within a blend
file to import, and a relationship subtype will be used to specify
the type of path for the Asset Sub ID.  For example, the subtype might be 'object',
in which case the sub ID would be the name of the object within the blend file to import.
