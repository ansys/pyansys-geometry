.. _ref_sketch:

Sketch
*******

In PyGeometry, a :class:`Sketch() <ansys.geometry.core.sketch>` is a class used to build 2D basic shape elements.
This class contains two fundamental constructs:

* Edges: A connection between two or more 2D points along a particular path. Edges represents open shapes
  such as arcs and lines.
* Faces: A set of edges that enclose a surface representing a closed shape such as a circle or triangle.

To initialize the sketch, first you can specify the :class:`Plane() <ansys.geometry.core.math.plane>` class, which
represents a plane in space from which other PyGeometry objects can be located.

You can initialize the sketch with this code:

.. code:: python

    from ansys.geometry.core.sketch import Sketch

    sketch = Sketch()

You can construct a sketch using different approaches.

Functional-style API
====================

A functional-style API is sometimes called a *fluent functional-style api* or *fluent API* in the developer community.
To avoid confusion with the Ansys Fluent product, the PyGeometry API documentation refrains from using the latter term.

One of the key features of a functional-style API is that it keeps an active context based on the previously created
edges to use as a reference starting point for additional objects.

This code creates a sketch with its origin as a starting point. Subsequent calls create segments,
which take as a starting point the last point of the previous edge.

.. code:: python

    sketch.segment_to_point(Point2D([3, 3]), "Segment2").segment_to_point(
        Point2D([3, 2]), "Segment3"
    )
    sketch.plot()


A functional-style API is also able to get a desired shape of the sketch object by taking advantage
of user-defined labels:

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

Direct API
==========

A direct API is sometimes called an *element-based approach* in the developer community.

This code shows how you can use a direct API to create multiple elements independently
and combine them all together in a single plane:

.. code:: python

    sketch.triangle(
        Point2D([-10, 10]), Point2D([5, 6]), Point2D([-10, -10]), tag="triangle2"
    )
    sketch.plot()

.. jupyter-execute::
    :hide-code:

    from ansys.geometry.core.sketch import Sketch
    from ansys.geometry.core.math import Point2D

    sketch = Sketch()
    sketch.triangle(
        Point2D([-10, 10]), Point2D([5, 6]), Point2D([-10, -10]), tag="triangle2"
    )
    sketch.plot()

For more information on sketch shapes, see the :class:`Sketch() <ansys.geometry.core.sketch>`
subpackage.
