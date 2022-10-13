.. _ref_user_guide:

==========
User Guide
==========
This guide provides a general overview of the basics and usage of the
Pygeometry library.

.. toctree::
   :maxdepth: 1
   :hidden:

   math
   plotting
   shapes
   designer

PyGeometry basic overview
=========================

The :class:`Modelar() <ansys.geometry.core.modelar.Modelar()>` method
within the ``ansys-geometry-core`` library creates an instance of
Geometry service. 

Inorder to create an instance, First, start the service locally. If you have docker installed and have
`authenticated to ghcr.io
<https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry>`_,
you can start the geometry service locally using ``docker`` with:

.. code:: bash

   docker run --name ans_geo -e -p 50051:50051 ghcr.io/pyansys/pygeometry:latest


By default ``Modeler`` will connect to ``127.0.0.1`` (``'localhost'``) at the
port 50051. You can change this by modifying the ``host`` and ``port``
parameters of ``Modeler``, but note that you will have to also modify this in
your ``docker run`` command by changing ``<HOST-PORT>-50051``.

Now, you can start the service with:

.. code:: python

    >>> from ansys.geometry.core import Modeler
    >>> modeler = Modeler()


Geometry service is now active and you can start creating the geometry model 
by initializing the Sketch.

.. code:: python

    from ansys.geometry.core.math import Plane, Point3D
    from ansys.geometry.core.misc import UNITS
    from ansys.geometry.core.sketch import Sketch   
    origin = Point3D([0, 0, 0])
    plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0])
    sketch = Sketch(plane)
    circle = sketch.draw_circle(Point3D([0, 0, 0]), radius=30 * UNITS.cm)
    circle.plot()

.. jupyter-execute::
    :hide-code:

    from ansys.geometry.core.math import Plane, Point3D
    from ansys.geometry.core.misc import UNITS
    from ansys.geometry.core.sketch import Sketch   
    origin = Point3D([0, 0, 0])
    plane = Plane(origin, direction_x=[1, 0, 0], direction_y=[0, 1, 0])
    sketch = Sketch(plane)
    circle = sketch.draw_circle(Point3D([0, 0, 0]), radius=30 * UNITS.cm)
    circle.plot()
