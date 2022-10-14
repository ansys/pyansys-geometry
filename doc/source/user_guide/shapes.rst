.. _ref_pygeometry_math_and_sketching_concept:

PyGeometry math and sketch concepts
***********************************

PyGeometry math objects
~~~~~~~~~~~~~~~~~~~~~~~

PyGeometry math sub-package consists of the primitive representation of the basic geometric
objects such as `Point`, `Vector`, `Matrix` along with Units by making use of the
Python package called `Pint <https://github.com/hgrecco/pint>`_ to 
operate and manipulate physical quantities.

Sketch
~~~~~~

In PyGeometry, a `Sketch` is class providing for building 2D basic shape elements.
PyGeometry Sketch contains two fundamental constructs:

* Edges -  a connection between two or more Point2D along a particular path represents open shapes such as arc, lines.
* Faces - a set of edges that enclose a surface represents closed shapes such as circle, triangle and so on.

To get initialize the sketch, first you can specify the :class:`Plane() <ansys.geometry.core.math.plane.Plane>` which
represent a plane in space, from which other PyGeometry objects can be located. They have a origin and a coordinate system.
Most methods that create an object are relative to the current plane.
The default work plane XY plane with (0,0) as origin. You can create 2D objects in the plane and 
PyGeometry then convert it to the global coordinate system, so that
the 2D features executes as expected. 

See :class:`Plane() <ansys.geometry.core.math.plane.Plane>` for further details.

You can initialize the sketch by:

.. code:: python

    from ansys.geometry.core.sketch.Sketch
    sketch = Sketch()

The sketch can be construct by using different approaches.

Fluent based approach (Fluent API)
==================================

One of the key features of this approach is keeping an active context based upon the previously created 
edges to use as a reference start point for additional objects.


.. code:: python
    
    sketch.segment_to_point(Point2D([3, 3]), "Segment2").segment_to_point(
        Point2D([3, 2]), "Segment3"
    )
    sketch.plot()

Here sketch has been created on with its origin, subsequently calls segment methods which takes the first segment 
edges to use as a reference start point for the second segment.  

It is also able to get the sketch with a newly created sketch objects with user-defined labels.

.. code:: python
    
    sketch.get("<tag>")

.. jupyter-execute::
    :hide-code:

    from ansys.geometry.core.sketch import Sketch
    from ansys.geometry.core.math import Point2D   
    sketch = Sketch()
    sketch.segment_to_point(Point2D([3, 3]), "Segment2").segment_to_point(
        Point2D([3, 2]), "Segment3"
    )
    sketch.plot()

Elements based approach (Direct API)
====================================

You can start creating multiple elements and combine all together with edges or faces in the single plane.

.. code:: python

    sketch.triangle(Point2D([-10, 10]), Point2D([5, 6]), Point2D([-10, -10]), tag="triangle2")
    sketch.plot()
    
.. jupyter-execute::
    :hide-code:

    from ansys.geometry.core.sketch import Sketch
    from ansys.geometry.core.math import Point2D   
    sketch = Sketch()
    sketch.triangle(Point2D([-10, 10]), Point2D([5, 6]), Point2D([-10, -10]), tag="triangle2")
    sketch.plot()

For further details and get familiarize with different sketch shapes, refer :class:`Sketch() <ansys.geometry.core.sketch.Sketch>`