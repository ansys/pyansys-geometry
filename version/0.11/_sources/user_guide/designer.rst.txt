Designer
********

The PyAnsys Geometry :class:`designer <ansys.geometry.core.designer>` subpackage organizes geometry assemblies
and synchronizes to a supporting Geometry service instance.

Create the model
----------------
This code create the :class:`Modeler() <ansys.geometry.core.modeler>` object which owns the whole designs
tools and data.

.. code:: python

    from ansys.geometry.core import Modeler

    # Create the modeler object itself
    modeler = Modeler()


Define the model
----------------
The following code define the model by creating a sketch with a circle on the client.
It then creates the model on the server.

.. code:: python

    from ansys.geometry.core.sketch import Sketch
    from ansys.geometry.core.math import Point2D
    from ansys.geometry.core.misc import UNITS
    from pint import Quantity

    # Create a sketch and draw a circle on the client
    sketch = Sketch()
    sketch.circle(Point2D([10, 10], UNITS.mm), Quantity(10, UNITS.mm))

    # Create your design on the server
    design_name = "ExtrudeProfile"
    design = modeler.create_design(design_name)


Add materials to model
-----------------------
This code adds the data structure and properties for individual materials:

.. code:: python

    from ansys.geometry.core.materials.material import Material
    from ansys.geometry.core.materials.property import (
        MaterialProperty,
        MaterialPropertyType,
    )

    density = Quantity(125, 1000 * UNITS.kg / (UNITS.m * UNITS.m * UNITS.m))
    poisson_ratio = Quantity(0.33, UNITS.dimensionless)
    tensile_strength = Quantity(45)
    material = Material(
        "steel",
        density,
        [MaterialProperty(MaterialPropertyType.POISSON_RATIO, "myPoisson", poisson_ratio)],
    )
    material.add_property(MaterialPropertyType.TENSILE_STRENGTH, "myTensile", Quantity(45))
    design.add_material(material)

Create bodies by extruding the sketch
-------------------------------------
Extruding a sketch projects all of the specified geometries onto the body. To create a solid body,
this code extrudes the sketch profile by a given distance.

.. code:: python

    body = design.extrude_sketch("JustACircle", sketch, Quantity(10, UNITS.mm))

Create bodies by extruding the face
-----------------------------------
The following code shows how you can also extrude a face profile by a given distance to create a solid body.
There are no modifications against the body containing the source face.

.. code:: python

    longer_body = design.extrude_face(
        "LongerCircleFace", body.faces[0], Quantity(20, UNITS.mm)
    )

You can also translate and tessellate design bodies and project curves onto them. For
more information, see these classes:

* :class:`Body() <ansys.geometry.core.designer.body>`
* :class:`Component() <ansys.geometry.core.designer.component>`

Download and save design
------------------------

You can save your design to disk or download the design of the active Geometry server instance.
The following code shows how to download and save the design.

.. code:: python

    file = "path/to/download.scdocx"
    design.download(file)

For more information, see the :class:`Design <ansys.geometry.core.designer.design>` submodule.
