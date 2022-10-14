.. _ref_sketch:

Sketch
*******

In PyGeometry, a `Sketch` is a class used to build 2D basic shape elements.
PyGeometry Sketch contains two fundamental constructs:

* Edges -  a connection between two or more Point2D along a particular path. It represents open shapes such as arc, lines.
* Faces - a set of edges that enclose a surface representing closed shapes such as circle, triangle and so on.

To get initialize the sketch, first you can specify the :class:`Plane() <ansys.geometry.core.math.plane>` which
represent a plane in space, from which other PyGeometry objects can be located.

You can initialize the sketch by:

.. code:: python

    from ansys.geometry.core.sketch.Sketch
    sketch = Sketch()

The sketch can be constructed using different approaches.

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

For further details and get familiarize with different sketch shapes, refer :class:`Sketch() <ansys.geometry.core.sketch>`