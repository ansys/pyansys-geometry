.. _ref_design:

Design
******

The :class:`Design <ansys.geometry.core.designer.design>` class is the top-level container
for a geometry model in PyAnsys Geometry. It extends the
:class:`Component <ansys.geometry.core.designer.component>` class, meaning that all
component-level operations (creating bodies, sub-components, datum planes, and so on) are
also available directly on the design object.

A ``Design`` object is always created through the
:class:`Modeler <ansys.geometry.core.modeler>` instance:

.. code:: python

    from ansys.geometry.core import Modeler

    modeler = Modeler()
    design = modeler.create_design("MyDesign")

Purpose and responsibilities
-----------------------------

A ``Design`` object represents the root of a geometry assembly. It is responsible for:

- Containing all :class:`Component <ansys.geometry.core.designer.component>` and 
  :class:`Body <ansys.geometry.core.designer.body>` that make up a geometry model.
- Managing **materials** that can be assigned to bodies.
- Managing **named selections**: named groups of geometry entities (components, bodies, faces,
  edges, design points, and vertices) that make it easier to reference specific portions of the
  model.
- Managing **beam profiles** used for structural beam elements.
- Managing **parameters** for parametric modeling.
- Providing **import and export** capabilities to exchange geometry with other tools.

Key properties
--------------

The following are the most commonly used properties on a ``Design`` object.

``bodies``
    A list of all top-level :class:`Body <ansys.geometry.core.designer.body>` objects in
    the design. Use :meth:`get_all_bodies()
    <ansys.geometry.core.designer.component.get_all_bodies>` to retrieve bodies at all
    levels of the hierarchy.

``components``
    A list of all top-level :class:`Component <ansys.geometry.core.designer.component>`
    objects in the design.

``materials``
    A list of :class:`Material <ansys.geometry.core.materials.material>` objects that have
    been added to the design.

``named_selections``
    A list of :class:`NamedSelection <ansys.geometry.core.designer.selection>` objects
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

**Exporting geometry**

PyAnsys Geometry provides dedicated ``export_to_*`` methods for each supported file format.
Each method accepts an optional ``location`` argument. If omitted, the file is saved in the
current working directory using the design name as the filename.

.. code:: python

    # Export as Ansys native format (returns Path to the saved file)
    path = design.export_to_scdocx()

    # Export as STEP
    path = design.export_to_step()

    # Export as IGES
    path = design.export_to_iges()

    # Export as Parasolid (text)
    path = design.export_to_parasolid_text()

    # Export as Parasolid (binary)
    path = design.export_to_parasolid_bin()

    # Export as FMD
    path = design.export_to_fmd()

    # Export as PMDB
    path = design.export_to_pmdb()

    # Export as DISCO
    path = design.export_to_disco()

    # Export as STRIDE
    path = design.export_to_stride()

You can also pass a directory path or a full path to ``location``:

.. code:: python

    import pathlib

    # Save to a specific directory; filename is "<design.name>.stp"
    path = design.export_to_step("path/to/directory")

    # Save to a specific file path
    path = design.export_to_step(pathlib.Path("path/to/directory/my_design.stp"))

The supported file formats are defined in
:class:`DesignFileFormat <ansys.geometry.core.designer.design>`.

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
:class:`Design <ansys.geometry.core.designer.design>`.
