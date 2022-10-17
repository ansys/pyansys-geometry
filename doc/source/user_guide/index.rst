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

PyGeometry is a Python wrapper for the Ansys Geometry Service. The key features of PyGeometry are:
* Ability to use the library along side other Python libraries
* Fluent based API for clean and easy coding experience
* Built-in examples

Simple interactive example
==========================

#. Start the geometry instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :class:`Modeler() <ansys.geometry.core.modelar>` class
within the ``ansys-geometry-core`` library creates an instance of
the Geometry Service. By default ``Modeler`` connects to ``127.0.0.1`` 
(``'localhost'``) at the port 50051. You can change this by modifying
the ``host`` and ``port`` parameters of ``Modeler``, but note that you
have to also modify this in your ``docker run`` command by changing ``<HOST-PORT>-50051``.
Now, you can start the service with:

.. code:: python

    >>> from ansys.geometry.core import Modeler
    >>> modeler = Modeler()

#. Create Geometry models
~~~~~~~~~~~~~~~~~~~~~~~~~

The Geometry Service is now active and you can start creating the geometry model 
by initializing the :ref:`Sketch <ref_sketch>` and :ref:`Primitives <ref_primitives>`.

.. code:: python

    from ansys.geometry.core.math import Plane, Point3D, Point2D
    from ansys.geometry.core.misc import UNITS
    from ansys.geometry.core.sketch import Sketch

    # Define our sketch
    origin = Point3D([0, 0, 10])
    plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0])

    # Create the sketch
    sketch = Sketch(plane)
    sketch.circle(Point2D([1, 1]), 30*UNITS.m)
    sketch.plot()

.. jupyter-execute::
    :hide-code:

    from ansys.geometry.core.math import Plane, Point3D, Point2D
    from ansys.geometry.core.misc import UNITS
    from ansys.geometry.core.sketch import Sketch   
    origin = Point3D([0, 0, 10])
    plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0])
    sketch = Sketch(plane)
    sketch.circle(Point2D([1, 1]), 30*UNITS.m)
    sketch.plot()

