.. _ref_body:

Body
****

The :class:`Body <ansys.geometry.core.designer.body>` class represents a 3D solid or
surface body within a component. Bodies are the leaf-level geometry objects in the
assembly hierarchy and are the primary objects used for analysis, visualization, and
export.

Bodies are created through component methods such as
:meth:`extrude_sketch() <ansys.geometry.core.designer.component.extrude_sketch>`,
:meth:`sweep_sketch() <ansys.geometry.core.designer.component.sweep_sketch>`, and
:meth:`revolve_sketch() <ansys.geometry.core.designer.component.revolve_sketch>`.
For more information, see :class:`Component <ansys.geometry.core.designer.component>`.

Purpose and responsibilities
----------------------------

A :class:`Body <ansys.geometry.core.designer.body>` object is responsible for:

- Representing a **solid or surface** geometry entity with faces, edges, and vertices.
- Supporting **geometric transformations** (translate, rotate, scale, mirror).
- Supporting **boolean operations** (unite, subtract, intersect).
- Providing **visualization** and **tessellation** of the geometry.
- Allowing **material assignment**.
- Exposing **physical properties** such as volume and bounding box.

Solid bodies versus surface bodies
------------------------------------

A body can be either a **solid body** (a closed, watertight 3D volume) or a
**surface body** (an open, 2D surface embedded in 3D space). You can check the type
by inspecting the ``is_surface`` property:

.. code:: python

    if body.is_surface:
        print("This is a surface body.")
    else:
        print("This is a solid body.")

Surface bodies have additional properties:

- ``surface_thickness``: The thickness assigned to the mid-surface.
- ``surface_offset``: The offset type for the mid-surface.

Key properties
--------------

The following are the most commonly used properties on a ``Body`` object.

``name``
    The user-defined name of the body.

``id``
    The unique identifier of the body within the Geometry service.

``faces``
    A list of :class:`Face <ansys.geometry.core.designer.face>` objects bounding the body.

``edges``
    A list of :class:`Edge <ansys.geometry.core.designer.edge>` objects on the body.

``vertices``
    A list of :class:`Vertex <ansys.geometry.core.designer.vertex>` objects on the body.

``volume``
    The computed volume of the body (only applicable for solid bodies).

``bounding_box``
    An axis-aligned bounding box enclosing the body.

``is_alive``
    ``True`` if the body still exists in the Geometry service (it may have been deleted or
    consumed by a boolean operation).

``is_suppressed``
    ``True`` if the body is currently suppressed (hidden) in the design.

``material``
    The :class:`Material <ansys.geometry.core.materials.material>` assigned to this body,
    or ``None`` if no material has been assigned.

Renaming and styling
---------------------

.. code:: python

    from ansys.geometry.core.designer.body import FillStyle

    # Rename the body
    body.set_name("MyRenamedBody")

    # Set the display color (RGB tuple with values between 0 and 255)
    body.set_color((255, 0, 0))   # Red

    # Control transparency
    body.set_fill_style(FillStyle.TRANSPARENT)

    # Suppress (hide) the body
    body.set_suppressed(True)

    # Unsuppress (show) the body
    body.set_suppressed(False)

Assigning materials
--------------------

.. code:: python

    # Assign a material (the material must exist in the design)
    body.assign_material(steel)

    # Retrieve the assigned material
    assigned = body.get_assigned_material()

    # Remove the material assignment
    body.remove_assigned_material()

Geometric transformations
--------------------------

Bodies can be moved, rotated, scaled, and mirrored within their parent component.

**Translating a body**

.. code:: python

    from ansys.geometry.core.math import UnitVector3D
    from ansys.geometry.core.misc import UNITS
    from pint import Quantity

    # Translate 20 mm in the X direction
    body.translate(UnitVector3D([1, 0, 0]), Quantity(20, UNITS.mm))

**Rotating a body**

.. code:: python

    from ansys.geometry.core.math import Point3D, UnitVector3D
    from ansys.geometry.core.misc import UNITS
    from pint import Quantity

    axis_origin = Point3D([0, 0, 0])
    axis_direction = UnitVector3D([0, 0, 1])

    # Rotate 45 degrees around the Z axis
    body.rotate(axis_origin, axis_direction, Quantity(45, UNITS.deg))

**Scaling a body**

.. code:: python

    # Scale uniformly by a factor of 2
    body.scale(2.0)

**Mirroring a body**

.. code:: python

    from ansys.geometry.core.math import Plane, Point3D, UnitVector3D

    # Mirror across the XY plane
    mirror_plane = Plane(Point3D([0, 0, 0]), UnitVector3D([1, 0, 0]), UnitVector3D([0, 1, 0]))
    body.mirror(mirror_plane)

Boolean operations
-------------------

Boolean operations combine or subtract volumes to produce new geometry. After a boolean
operation, the tool body is consumed (``is_alive`` becomes ``False``), while the target
body is modified in place.

**Unite (union)**

Joins two bodies into a single body:

.. code:: python

    # Unite `body` with `other_body`; `other_body` is consumed
    body.unite(other_body)

**Subtract**

Removes the volume of one body from another:

.. code:: python

    # Subtract `tool_body` from `body`; `tool_body` is consumed
    body.subtract(tool_body)

**Intersect**

Keeps only the volume common to both bodies:

.. code:: python

    # Intersect `body` with `other_body`; `other_body` is consumed
    body.intersect(other_body)

.. note::

   After a boolean operation, always check ``body.is_alive`` before accessing the result.
   The tool body is consumed by the operation. If the result is an empty solid (for example,
   when there is no intersection), the target body may also be removed.

Copying a body
--------------

.. code:: python

    # Create an independent copy of the body in the same component
    body_copy = body.copy(parent_component, "CopiedBody")

Curve imprinting and projection
---------------------------------

You can imprint 2D sketch curves onto the faces of a body to create new edges:

.. code:: python

    from ansys.geometry.core.sketch import Sketch
    from ansys.geometry.core.math import Point2D
    from ansys.geometry.core.misc import UNITS
    from pint import Quantity

    imprint_sketch = Sketch()
    imprint_sketch.circle(Point2D([0, 0]), Quantity(3, UNITS.mm))

    # Imprint the sketch curves onto the body, creating new face edges
    body.imprint_curves([body.faces[0]], imprint_sketch)

Checking collision
-------------------

.. code:: python

    from ansys.geometry.core.designer.body import CollisionType

    collision_result = body.get_collision(other_body)

    if collision_result == CollisionType.INTERFERENCE:
        print("Bodies interfere.")
    elif collision_result == CollisionType.TOUCHING:
        print("Bodies are touching.")
    else:
        print("No collision detected.")

Tessellation and visualization
-------------------------------

Tessellating a body generates a mesh representation (triangulation) of its surface, which
is useful for visualization and downstream analysis.

.. code:: python

    # Visualize the body in an interactive 3D plot
    body.plot()

    # Get a PyVista PolyData object for custom visualization
    poly_data = body.tessellate()

    # Get raw tessellation data
    raw_tess = body.get_raw_tessellation()

For the full API reference, see
:class:`Body <ansys.geometry.core.designer.body>`.
