Math and Sketch
===============

PyGeometry math objects
-----------------------

PyGeometry math subpackage consists of the the primitive representation of the basic geometric
objects such as `Point`, `Vector`, `Matrix` along with Units by making use of 
Python package called :ref:`Pint <https://github.com/hgrecco/pint> ` in order to 
operate and manipulate physical quantities.

Sketch
------

In PyGeometry, a `Sketch` is class providing for building 2D basic shape elements.
PyGeometry Sketch contains two fundamental constructs:

* Edges -  a connection between two or more Point2D along a particular path represents open shapes such as arc, lines.
* faces - a set of edges that enclose a surface represents closed shapes such as circle, triangle and so on.

To get initialize the sketch, first you can specify the :ref:`Plane <ansys.geometry.core.math.plane.Plane>` which
represent a plane in space, from which other pyGeometry objects can be located. They have a origin and a coordinate system.
Most methods that create an object will be relative to the current plane.
The default work plane XY plane with (0,0) as origin. You can create 2D objects in the plane and 
PyGeometry will convert it to the global coordinate system, so that
the 2D features will be located as expected. 

See :ref:`Plane <ansys.geometry.core.math.plane.Plane>` for further details.

You can initialize the sketch by:

.. code:: python

    from ansys.geometry.core.sketch.Sketch
    sketch = Sketch()

You can start sketching the 


