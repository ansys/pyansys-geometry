PyGeometry Math and Sketch concepts
***********************************

PyGeometry math objects
~~~~~~~~~~~~~~~~~~~~~~~

PyGeometry math subpackage consists of the the primitive representation of the basic geometric
objects such as `Point`, `Vector`, `Matrix` along with Units by making use of 
Python package called `Pint <https://github.com/hgrecco/pint>_ ` in order to 
operate and manipulate physical quantities.

Sketch
~~~~~~

In PyGeometry, a `Sketch` is class providing for building 2D basic shape elements.
PyGeometry Sketch contains two fundamental constructs:

* Edges -  a connection between two or more Point2D along a particular path represents open shapes such as arc, lines.
* Faces - a set of edges that enclose a surface represents closed shapes such as circle, triangle and so on.

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

The sketch can be cconstruct by using different approaches.

Fluent based approach
======================

One of the key features of this approach is keeping an active context based upon the previously created 
edges to use as a reference start point for additional objects.


.. code:: python
    
    sketch.segment_to_point(Point2D([3, 3]), "Segment2").segment_to_point(
        Point2D([3, 2]), "Segment3"
    )
    sketch.plot()

you will also able to get the sketch with a newly created sketch objects with user-defined labels.

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

Elements based approach
=======================

You can start creating multiple elements and combine all together with edges or faces in the single plane.

.. code:: python

    sketch.trapezoid(10, 8, np.pi / 4, np.pi / 8, Point2D([10, -10]), tag="trapezoid1")
    sketch.plot()
    
.. jupyter-execute::
    :hide-code:

    from ansys.geometry.core.sketch import Sketch
    from ansys.geometry.core.math import Point2D   
    sketch = Sketch()
    sketch.trapezoid(10, 8, np.pi / 4, np.pi / 8, Point2D([10, -10]), tag="trapezoid1")
    sketch.plot()

For further details and get familiarize with different sketch shapes, refer :ref:`sketch <ansys.geometry.core.math.sketch.Sketch>`