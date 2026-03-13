.. _ref_component:

Component
*********

The :class:`Component <ansys.geometry.core.designer.component>` class represents a
sub-assembly within a design. Components can be nested to any depth to create complex
assembly structures. Each component can contain bodies, beams, nested components,
coordinate systems, datum planes, and design points.

Because :class:`Design <ansys.geometry.core.designer.design>` extends :class:`Component <ansys.geometry.core.designer.component>`, all geometry creation methods
described on this page are also available directly on a :class:`Design <ansys.geometry.core.designer.design>` object.

Purpose and responsibilities
-----------------------------

A :class:`Component <ansys.geometry.core.designer.component>` object is responsible for:

- Organizing bodies and other geometry into a **named sub-assembly** within the design.
- Providing methods to **create geometry** (extrusions, sweeps, revolutions, primitives).
- Supporting **nested assemblies** by allowing components to contain other components.
- Controlling the **placement** (position and orientation) of a sub-assembly within the
  parent coordinate system.
- Managing reference geometry such as **coordinate systems**, **datum planes**, and
  **design points**.
- Sharing topology between bodies via the **shared topology** feature.

Creating a component
--------------------

Components are always created as children of an existing component or design:

.. code:: python

    from ansys.geometry.core import Modeler

    modeler = Modeler()
    design = modeler.create_design("MyDesign")

    # Add a named sub-component to the design
    frame_component = design.add_component("Frame")

    # Add a nested sub-component
    joint_component = frame_component.add_component("Joint")

Component instances and master components
------------------------------------------

PyAnsys Geometry supports **instancing** of components. When you create a component from
a template, both the original and the new instance share the same underlying
:class:`~ansys.geometry.core.designer.part.MasterComponent`. Modifying the master geometry updates all instances.

This is useful when the same part appears multiple times in an assembly (for example,
identical bolts or brackets):

.. code:: python

    # Create the original component (template)
    bolt = design.add_component("Bolt")

    # Create a sketch and extrude it to define the bolt geometry
    from ansys.geometry.core.sketch import Sketch
    from ansys.geometry.core.math import Point2D
    from ansys.geometry.core.misc import UNITS
    from pint import Quantity

    sketch = Sketch()
    sketch.circle(Point2D([0, 0]), Quantity(5, UNITS.mm))
    bolt.extrude_sketch("BoltBody", sketch, Quantity(20, UNITS.mm))

    # Create a second bolt instance that shares the master geometry
    bolt_instance = design.add_component("Bolt_2", template=bolt)

Creating geometry in a component
----------------------------------

A component provides several methods to create 3D geometry from 2D sketches and other
inputs.

**Extruding a sketch**

The most common way to create a solid body is by extruding a 2D sketch:

.. code:: python

    from ansys.geometry.core.sketch import Sketch
    from ansys.geometry.core.math import Point2D
    from ansys.geometry.core.misc import UNITS
    from pint import Quantity

    sketch = Sketch()
    sketch.circle(Point2D([0, 0]), Quantity(10, UNITS.mm))

    # Extrude the sketch profile to produce a cylinder
    cylinder = frame_component.extrude_sketch("Cylinder", sketch, Quantity(30, UNITS.mm))

**Extruding a face**

You can also extrude an existing face on a body:

.. code:: python

    # Extrude the top face of the cylinder
    cap = frame_component.extrude_face("Cap", cylinder.faces[0], Quantity(5, UNITS.mm))

**Sweeping a sketch along a path**

Sweeping moves a 2D profile along a curve to create a 3D solid:

.. code:: python

    # Assuming `path_curve` is an existing TrimmedCurve
    swept_body = frame_component.sweep_sketch(
        "SweepBody", sketch, path_curve
    )

**Revolving a sketch**

Revolving a sketch around an axis creates axisymmetric geometry:

.. code:: python

    from ansys.geometry.core.math import Point3D, UnitVector3D

    axis_origin = Point3D([0, 0, 0])
    axis_direction = UnitVector3D([0, 0, 1])

    revolved = frame_component.revolve_sketch(
        "RevolvedBody", sketch, axis_origin, axis_direction, Quantity(360, UNITS.deg)
    )

**Creating a sphere primitive**

.. code:: python

    sphere = frame_component.create_sphere(
        "Sphere", Point3D([0, 0, 0]), Quantity(15, UNITS.mm)
    )

Managing component placement
------------------------------

Every component has a placement (position and orientation) relative to its parent
component. You can move a component by modifying its placement:

.. code:: python

    from ansys.geometry.core.math import Frame, Point3D, UnitVector3D

    # Define a new frame for the component position
    new_frame = Frame(
        origin=Point3D([50, 0, 0]),
        direction_x=UnitVector3D([1, 0, 0]),
        direction_y=UnitVector3D([0, 1, 0]),
    )
    frame_component.modify_placement(new_frame)

    # Reset placement to the default (origin)
    frame_component.reset_placement()

To obtain the global (world) transformation matrix of a component:

.. code:: python

    world_transform = frame_component.get_world_transform()

Shared topology
---------------

Shared topology controls how the geometry within a component interacts with adjacent
geometry during meshing. The available modes are:

- ``SHARETYPE_NONE``: No sharing (default).
- ``SHARETYPE_SHARE``: Bodies share topology (conformal mesh at interfaces).
- ``SHARETYPE_MERGE``: Bodies are merged into a single entity.
- ``SHARETYPE_GROUPS``: Bodies are grouped for shared topology.

.. code:: python

    from ansys.geometry.core.designer import SharedTopologyType

    frame_component.set_shared_topology(SharedTopologyType.SHARETYPE_SHARE)

Reference geometry
------------------

A component can own reference geometry that helps define positions and orientations within
the assembly.

**Coordinate systems**

.. code:: python

    from ansys.geometry.core.math import Frame, Point3D, UnitVector3D

    cs = frame_component.create_coordinate_system(
        "MyCS",
        Frame(
            Point3D([10, 0, 0]),
            UnitVector3D([1, 0, 0]),
            UnitVector3D([0, 1, 0]),
        ),
    )

**Datum planes**

.. code:: python

    from ansys.geometry.core.math import Plane, Point3D, UnitVector3D

    plane = Plane(Point3D([0, 0, 5]), UnitVector3D([1, 0, 0]), UnitVector3D([0, 1, 0]))
    dp = frame_component.create_datum_plane("MidPlane", plane)

**Design points**

.. code:: python

    design_point = frame_component.add_design_point("Anchor", Point3D([0, 0, 0]))

Accessing bodies recursively
------------------------------

To retrieve all bodies at every level of the component hierarchy:

.. code:: python

    # Returns only the bodies directly owned by `frame_component`
    direct_bodies = frame_component.bodies

    # Returns all bodies in the entire sub-tree
    all_bodies = frame_component.get_all_bodies()

For the full API reference, see
:class:`Component <ansys.geometry.core.designer.component>`.
