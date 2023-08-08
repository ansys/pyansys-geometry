.. _ref_primitives:

Primitives
**********

In PyGeometry, the :class:`primitives <ansys/geometry/core/primitives>` subpackage consists
of primitive representations of basic geometric objects, such as ``Point``, ``Vector``, and
``Matrix``. To operate and manipulate physical quantities, this subpackage uses
`Pint <https://github.com/hgrecco/pint>`_, a third-party open source software
that other PyAnsys libraries also use.

This table shows PyGeometry names and base values for the physical quantities:

+----------------------------+---------+
| Name                       | value   |
+============================+=========+
| LENGTH_ACCURACY            | 1e-8    |
+----------------------------+---------+
| ANGLE_ACCURACY             | 1e-6    |
+----------------------------+---------+
| DEFAULT_UNITS.LENGTH       | meter   |
+----------------------------+---------+
| DEFAULT_UNITS.ANGLE        | radian  |
+----------------------------+---------+

To define accuracy and measurements, you use these PyGeometry classes:

* :class:`Accuracy <ansys.geometry.core.misc.accuracy>`
* :class:`Measurements <ansys.geometry.core.misc.measurements>`

Planes
------

The :class:`Plane() <ansys.geometry.core.math.plane>` class provides primitive representation
of a 2D plane in 3D space. It has an origin and a coordinate system.
Sketched shapes are always defined relative to a plane.
The default working plane is XY, which has ``(0,0)`` as its origin.

If you create 2D objects in the plane, PyGeometry converts it to the global coordinate system so that
the 2D feature executes as expected:

.. code:: python

    origin = Point3D([42, 99, 13])
    plane = Plane(origin, UnitVector3D([1, 0, 0]), UnitVector3D([0, 1, 0]))
