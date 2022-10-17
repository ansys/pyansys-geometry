.. _ref_primitives:

Primitives
**********

PyGeometry math sub-package consists of the primitive representation of the basic geometric
objects such as ``Point``, ``Vector``, ``Matrix`` along with units by making use of
`Pint <https://github.com/hgrecco/pint>`_ to 
operate and manipulate physical quantities.

The base values of PyGeometry is as follows:

+-------------------+---------+ 
| Name              | value   |
+===================+=========+
| LENGTH_ACCURACY   | 1e-8    |
+-------------------+---------+  
| ANGLE_ACCURACY    | 1e-6    |
+-------------------+---------+ 
| UNIT_LENGTH       | meter   |
+-------------------+---------+ 
| UNIT_ANGLE        | radian  |
+-------------------+---------+ 

* :class:`Accuracy() <ansys.geometry.core.misc.accuracy>`
* :class:`Measurements() <ansys.geometry.core.misc.measurements>`

Plane concept
-------------

The :class:`Plane() <ansys.geometry.core.math.plane>` class provides primitive representation of a 2D plane in 3D space. 
It has an origin and a coordinate system.
Sketched shapes are always defined relative to a plane.
The default working plane is XY with (0,0) as origin. You can create 2D objects in the plane and 
PyGeometry then converts it to the global coordinate system, so that
the 2D feature executes as expected.

.. code:: python

    origin = Point3D([42, 99, 13])
    plane = Plane(origin, UnitVector3D([1, 0, 0]), UnitVector3D([0, 1, 0]))

See :class:`Plane() <ansys.geometry.core.math.plane>` for further details.