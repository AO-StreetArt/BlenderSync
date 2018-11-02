Property Management
=================

Property Management allows replication of Blender values that are not associated
to an object, such as gravity.

Crud Operations will be supported by the UI, with all properties displayed in a
list.  Each Property will be mapped by the 'asset_sub_id' attribute of the
Clyman Property API to the Blender RNA identifier.

Operators Overview
------------------

* Create Property - Use the RNA value in the text input and current value at that RNA address to generate a new property.  Optionally include a property name.
* Update Property - Update the attributes of the selected Property value in Aesel, including the value.
* Get Property - Retrieve the selected Property from Aesel, and update the corresponding Blender value.
* Delete Property - Delete a property from the Aesel server.
* Filter Properties - Filter the Properties in the properties list.

UI Overview
-----------

The Properties list should share the design of the Scene List, obviously with
Property attributes populated in place of Scene Attributes.
