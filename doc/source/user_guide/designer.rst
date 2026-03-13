.. _ref_designer:

Designer
********

The PyAnsys Geometry :mod:`designer <ansys.geometry.core.designer>` subpackage organizes geometry
assemblies and synchronizes to a supporting Geometry service instance.

.. _ref_designer_architecture:

Architecture overview
---------------------

PyAnsys Geometry uses a hierarchical object model to represent 3D geometry. Understanding
this hierarchy is essential to effectively using the API.

The core classes in the ``designer`` subpackage are:

- :ref:`Design <ref_design>`: The top-level container for a geometry model. Each design
  corresponds to a single session in the Geometry service and can contain components, bodies,
  materials, named selections, and more.
- :ref:`Component <ref_component>`: A sub-assembly within a design. Components can be nested
  to create complex assemblies and can contain other components, bodies, beams, coordinate
  systems, datum planes, and design points.
- :ref:`Body <ref_body>`: A 3D solid or surface body within a component. Bodies can be
  created by extruding, sweeping, or revolving sketches, or by applying boolean operations
  to existing bodies.

The following diagram illustrates the assembly hierarchy::

    Design
    ├── Component
    │   ├── Body
    │   ├── Component (nested)
    │   │   └── Body
    │   ├── CoordinateSystem
    │   ├── DatumPlane
    │   └── DesignPoint
    ├── Body
    ├── Material
    └── NamedSelection

.. note::

   ``Design`` extends ``Component``, so everything that you can do with a ``Component``
   can also be done directly on a ``Design`` object. At the top level, a design acts as
   the root component of the assembly.

   For a detailed description of each class and its capabilities, see:

   - :ref:`Design <ref_design>`
   - :ref:`Component <ref_component>`
   - :ref:`Body <ref_body>`

Quick start
-----------

The following example demonstrates the typical workflow for creating a geometry model with
PyAnsys Geometry.

First, connect to the Geometry service using the
:class:`Modeler <ansys.geometry.core.modeler>` class:

.. code:: python

    from ansys.geometry.core import Modeler

    modeler = Modeler()

Then, create a design, which is the root container for all geometry:

.. code:: python

    from ansys.geometry.core.sketch import Sketch
    from ansys.geometry.core.math import Point2D
    from ansys.geometry.core.misc import UNITS
    from pint import Quantity

    # Create a sketch and draw a circle
    sketch = Sketch()
    sketch.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))

    # Create a design on the service
    design = modeler.create_design("MyDesign")

Extrude the sketch to create a solid body:

.. code:: python

    body = design.extrude_sketch("Cylinder", sketch, Quantity(10, UNITS.mm))

Download and save the resulting design:

.. code:: python

    path = design.export_to_scdocx("path/to")

.. warning::

   To ensure design objects are up to date, access design information (bodies,
   components, and so on) via the design instance properties and methods rather
   than storing that information separately. For example, use ``design.bodies``
   rather than storing the result in a separate variable (``bodies =
   design.bodies``) and accessing it later. The separate variable can become
   stale if the design is updated after the initial retrieval.

For detailed usage information on each class, see the following pages:

.. toctree::
   :maxdepth: 1

   design
   component
   body
