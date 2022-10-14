.. _ref_user_guide:

==========
User guide
==========
This guide provides a general overview of the basics and usage of the
PyGeometry library. See the side panel for the individual sections 
demonstrating the key method concepts of PyGeometry.

.. toctree::
   :maxdepth: 1
   :hidden:
   
   primitives
   shapes
   designer

PyGeometry basic overview
=========================

PyGeometry is a python wrapper for Ansys Geometry Services. The key features of the PyGeometry are:
* Ability to use the library along side other Python libraries
* Fluent based API for clean and easy code
* Build in examples

Simple example
===============

1. start the geometry instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :class:`Modelar()<ansys.geometry.core.modelar.Modelar()>` method
within the ``ansys-geometry-core`` library creates an instance of
Geometry service. By default ``Modeler`` connects to ``127.0.0.1`` 
(``'localhost'``) at the port 50051. You can change this by modifying
the ``host`` and ``port`` parameters of ``Modeler``, but note that you
have to also modify this in your ``docker run`` command by changing ``<HOST-PORT>-50051``.
Now, you can start the service with:

.. code:: python

    >>> from ansys.geometry.core import Modeler
    >>> modeler = Modeler()

2. create geometry models
~~~~~~~~~~~~~~~~~~~~~~~~~
Geometry service is now active and you can start creating the geometry model 
by initializing the :ref:`Sketch <ref_sketch>` and :ref:`Primitives <ref_primitives>`.

.. code:: python

    from ansys.geometry.core.math import Plane, Point3D, Point2D
    from ansys.geometry.core.misc import UNITS
    from ansys.geometry.core.sketch import Sketch   
    origin = Point3D([10, 10, 0])
    plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0])
    sketch = Sketch(plane)
    sketch.triangle(Point2D([-10, 10]), Point2D([5, 6]), Point2D([-10, -10]), tag="triangle2")
    sketch.plot()

.. jupyter-execute::
    :hide-code:

    from ansys.geometry.core.math import Plane, Point3D, Point2D
    from ansys.geometry.core.misc import UNITS
    from ansys.geometry.core.sketch import Sketch   
    origin = Point3D([10, 10, 0])
    plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0])
    sketch = Sketch(plane)
    sketch.triangle(Point2D([-10, 10]), Point2D([5, 6]), Point2D([-10, -10]), tag="triangle2")
    sketch.plot()

