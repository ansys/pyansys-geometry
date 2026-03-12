.. _ref_design:

Design
******

The :class:`Design <ansys.geometry.core.designer.Design>` class is the top-level container
for a geometry model in PyAnsys Geometry. It extends the
:class:`Component <ansys.geometry.core.designer.Component>` class, meaning that all
component-level operations (creating bodies, sub-components, datum planes, and so on) are
also available directly on the design object.

A ``Design`` object is always created through the
:class:`Modeler <ansys.geometry.core.modeler.Modeler>` instance:

.. code:: python

    from ansys.geometry.core import Modeler

    modeler = Modeler()
    design = modeler.create_design("MyDesign")

Purpose and responsibilities
-----------------------------

A ``Design`` object represents the root of a geometry assembly. It is responsible for:

- Containing all :ref:`components <ref_component>` and :ref:`bodies <ref_body>` that make up
  a geometry model.
- Managing **materials** that can be assigned to bodies.
- Managing **named selections** — named groups of geometry entities (bodies, faces, edges,
  and vertices) that make it easier to reference specific portions of the model.
- Managing **beam profiles** used for structural beam elements.
- Managing **parameters** for parametric modeling.
- Providing **import and export** capabilities to exchange geometry with other tools.

Key properties
--------------

The following are the most commonly used properties on a ``Design`` object.

``bodies``
    A list of all top-level :class:`Body <ansys.geometry.core.designer.Body>` objects in
    the design. Use :meth:`get_all_bodies()
    <ansys.geometry.core.designer.Component.get_all_bodies>` to retrieve bodies at all
    levels of the hierarchy.

``components``
    A list of all top-level :class:`Component <ansys.geometry.core.designer.Component>`
    objects in the design.

``materials``
    A list of :class:`Material <ansys.geometry.core.materials.Material>` objects that have
    been added to the design.

``named_selections``
    A list of :class:`NamedSelection <ansys.geometry.core.designer.NamedSelection>` objects
    available in the design.

``is_active``
    ``True`` if the design is currently the active design in the Geometry service session.

Working with materials
----------------------

Materials define physical properties (such as density, Poisson's ratio, and tensile
strength) that can be assigned to bodies. Add a material to a design before assigning
it to any body.

.. code:: python

    from pint import Quantity
    from ansys.geometry.core.materials import Material
    from ansys.geometry.core.materials import MaterialProperty, MaterialPropertyType
    from ansys.geometry.core.misc import UNITS

    # Define material properties
    density = Quantity(7850, UNITS.kg / UNITS.m**3)
    poisson_ratio = Quantity(0.3, UNITS.dimensionless)

    # Create and add material to the design
    steel = Material(
        "steel",
        density,
        [MaterialProperty(MaterialPropertyType.POISSON_RATIO, "PoissonRatio", poisson_ratio)],
    )
    design.add_material(steel)

To assign a material to a body:

.. code:: python

    body.assign_material(steel)

To remove a material from the design:

.. code:: python

    design.remove_material(steel)

Working with named selections
------------------------------

Named selections allow you to group and later reference specific geometry entities, such as
bodies, faces, edges, or vertices.

.. code:: python

    # Create a named selection containing specific bodies
    ns = design.create_named_selection("ImportantBodies", bodies=[body1, body2])

    # Access all named selections in the design
    for ns in design.named_selections:
        print(ns.name)

    # Delete a named selection when no longer needed
    design.delete_named_selection(ns)

Importing and exporting geometry
---------------------------------

PyAnsys Geometry supports importing geometry files into a design and exporting designs
to several industry-standard formats.

**Importing geometry**

.. code:: python

    # Import a STEP file into the design
    design.insert_file("path/to/geometry.step")

**Exporting (downloading) geometry**

The :meth:`download() <ansys.geometry.core.designer.Design.download>` method saves the
design to a local file. The format is determined by the file extension:

.. code:: python

    # Download as Ansys native format
    design.download("path/to/design.scdocx")

    # Download as STEP
    design.download("path/to/design.step")

    # Download as IGES
    design.download("path/to/design.igs")

    # Download as Parasolid (text)
    design.download("path/to/design.x_t")

    # Download as Parasolid (binary)
    design.download("path/to/design.x_b")

The supported file formats are defined in
:class:`DesignFileFormat <ansys.geometry.core.designer.DesignFileFormat>`.

Working with parameters
-----------------------

Parameters allow for parametric modeling, where dimensions can be controlled by named
variables.

.. code:: python

    # Retrieve all parameters in the design
    params = design.get_all_parameters()

    # Update a parameter value
    design.set_parameter("Height", Quantity(50, UNITS.mm))

Closing a design
----------------

When you are finished working with a design, close it to release server-side resources:

.. code:: python

    design.close()

For the full API reference, see
:class:`Design <ansys.geometry.core.designer.Design>`.
