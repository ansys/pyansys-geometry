Designer
********

Design sub-package provides a ``Design`` for organizing geometry assemblies and synchronizes to
a supporting Geometry Service instance.

Defining the model
------------------

.. code:: python

    # Create a Sketch and draw a circle (from the client)
    sketch = Sketch()
    sketch.draw_circle(Point3D([10, 10, 0], UNITS.mm), Quantity(10, UNITS.mm))

    # Create your design on the server side
    design_name = "ExtrudeProfile"
    design = modeler.create_design(design_name) 


Add materials to model
-----------------------

You can add the data structure and property for individual materials.

.. code:: python

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

Projects all of the specified geometries onto the body. You can create a solid body by
extruding the given sketch profile by a given distance.

.. code:: python

    body = design.extrude_sketch("JustACircle", sketch, Quantity(10, UNITS.mm))

Create bodies by extruding the face
-----------------------------------

It is also possible to extrude a face profile by a given distance to create a new solid body.
There are no modifications against the body containing the source face.

.. code:: python
    
    longer_body = design.extrude_face(
        "LongerCircleFace", body.faces[0], Quantity(20, UNITS.mm)
    )

Design bodies can also be translated, tessellated, and curves can be projected onto them.

* :class:`Body() <ansys.geometry.core.designer.body>`
* :class:`Component() <ansys.geometry.core.designer.component>`

Download and save design
------------------------

With PyGeometry you can save to disk or download the design of the active Geometry Server instance.

.. code:: python

    file = "path/to/download"
    design.download(file, as_stream=False)

* :class:`Design() <ansys.geometry.core.designer.design>`